"""Task 2 — Classification: predict test_end (Extinction / Disruption / Completion).

Rules honoured:
- Uses data/model_ready/flex_train.csv + flex_targets.csv.
- Drops rows whose test_end is empty (none in practice).
- GroupKFold(5) on campaign_id -> no leakage.
- random_state = 42 everywhere.
- No deep learning.
"""
import json
import os
import pickle
import sys

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import train_regression as tr  # noqa: E402  (reuse campaign_id/build_X/impute/paths/SEED)

SEED = tr.SEED
N_SPLITS = tr.N_SPLITS
TARGET = "test_end"


def load_cls():
    train_csv = pd.read_csv(tr.TRAIN_CSV)
    targets_csv = pd.read_csv(tr.TARGETS_CSV)
    df = train_csv.merge(targets_csv, on="test_id")
    df["campaign_id"] = df["flex_id"].map(tr.campaign_id)
    df["yc"] = df["target_classification"].astype(str).str.strip()
    n_total = len(df)
    keep = df["yc"].notna() & (df["yc"] != "") & (df["yc"].str.lower() != "nan")
    df = df[keep].copy().reset_index(drop=True)
    return df, n_total


def metrics(y, p, labels):
    return {
        "balanced_accuracy": float(balanced_accuracy_score(y, p)),
        "macro_f1": float(f1_score(y, p, average="macro")),
        "confusion_matrix": confusion_matrix(y, p, labels=labels).tolist(),
    }


def _lr():
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    class_weight="balanced", max_iter=5000, random_state=SEED
                ),
            ),
        ]
    )


SPECS = {
    "baseline_most_frequent": lambda: DummyClassifier(
        strategy="most_frequent", random_state=SEED
    ),
    "logistic_regression": _lr,
    "random_forest": lambda: RandomForestClassifier(
        n_estimators=400,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
    ),
}
# Simplicity ranking (lower = simpler) for the "<5% -> prefer simpler" rule.
COMPLEXITY = {"baseline_most_frequent": 0, "logistic_regression": 1, "random_forest": 2}


def main():
    os.makedirs(tr.MODELS_DIR, exist_ok=True)
    os.makedirs(tr.REPORTS_DIR, exist_ok=True)

    df, n_total = load_cls()
    y = df["yc"].to_numpy()
    X = tr.build_X(df)
    groups = df["campaign_id"].to_numpy()
    labels = sorted(np.unique(y))

    print("=" * 70)
    print("TASK 2 — Classification: test_end")
    print("=" * 70)
    print(f"rows total          : {n_total}")
    print(f"rows used           : {len(df)}  (dropped {n_total - len(df)}: empty class)")
    print(f"classes             : {dict(df['yc'].value_counts())}")
    print(f"campaigns           : {df['campaign_id'].nunique()}  (GroupKFold({N_SPLITS}))")
    print(f"features            : {list(X.columns)}")
    print()

    gkf = GroupKFold(n_splits=N_SPLITS)
    results = {}
    for name, factory in SPECS.items():
        fold_ba, fold_f1 = [], []
        oof = np.full(len(df), "", dtype=object)
        for itr, ite in gkf.split(X, y, groups):
            Xtr, Xte = tr.impute(X.iloc[itr], X.iloc[ite])
            model = factory().fit(Xtr, y[itr])
            p = model.predict(Xte)
            oof[ite] = p
            fold_ba.append(float(balanced_accuracy_score(y[ite], p)))
            fold_f1.append(float(f1_score(y[ite], p, average="macro", zero_division=0)))
        results[name] = {
            "oof": metrics(y, oof, labels),
            "fold_mean": {
                "balanced_accuracy": float(np.mean(fold_ba)),
                "macro_f1": float(np.mean(fold_f1)),
            },
            "fold_balanced_accuracy": fold_ba,
            "fold_macro_f1": fold_f1,
        }

    print("-" * 70)
    print(f"{'model':<26}{'bal.acc':>9}{'macroF1':>9}   vs baseline (bal.acc)")
    print("-" * 70)
    base_ba = results["baseline_most_frequent"]["oof"]["balanced_accuracy"]
    for name in SPECS:
        r = results[name]["oof"]
        gain = (r["balanced_accuracy"] - base_ba) / base_ba * 100
        print(f"{name:<26}{r['balanced_accuracy']:>9.4f}{r['macro_f1']:>9.4f}   {gain:+.1f}%")
    print("-" * 70)
    print()

    # ---------- selection (primary = balanced accuracy) ----------
    best = max(SPECS, key=lambda n: results[n]["oof"]["balanced_accuracy"])
    best_ba = results[best]["oof"]["balanced_accuracy"]
    within = [
        n for n in SPECS if (best_ba - results[n]["oof"]["balanced_accuracy"]) / best_ba < 0.05
    ]
    chosen = min(within, key=lambda n: COMPLEXITY[n])

    if chosen == best:
        reason = (
            f"{chosen} has the highest OOF balanced accuracy ({best_ba:.4f}); "
            f"no simpler model is within 5% of it."
        )
    else:
        gap = (best_ba - results[chosen]["oof"]["balanced_accuracy"]) / best_ba * 100
        reason = (
            f"{best} has the highest OOF balanced accuracy ({best_ba:.4f}), but {chosen} "
            f"is only {gap:.2f}% behind (<5%) and is simpler, so {chosen} is selected."
        )
    print(f"selected model : {chosen}")
    print(f"reason         : {reason}")
    print()

    # chosen-model OOF confusion matrix + per-class report
    cm = np.array(results[chosen]["oof"]["confusion_matrix"])
    print("OOF confusion matrix (rows = true, cols = pred):")
    print("labels:", labels)
    print(cm)
    print()
    oof_chosen = _oof_of(results, chosen, y, X, groups, labels)
    print(classification_report(y, oof_chosen, labels=labels, zero_division=0))

    # ---------- refit chosen on ALL rows + save ----------
    Xa = X.copy()
    Xa[tr.NUM_COLS] = Xa[tr.NUM_COLS].fillna(Xa[tr.NUM_COLS].median())
    final = SPECS[chosen]().fit(Xa, y)
    payload = {
        "model": final,
        "model_name": chosen,
        "task": "classification",
        "target": TARGET,
        "classes": labels,
        "features": list(X.columns),
        "categorical_encoding": {"fuel": "binary fuel_methanol (Methanol=1, Heptane=0)"},
        "imputation": "median fit on training folds (numeric features)",
        "cv": f"GroupKFold({N_SPLITS}) on campaign_id",
        "campaign_id_rule": "flex_id: if 'CAL' -> prefix through CAL; else strip trailing [HMRF]<digits>",
        "random_state": SEED,
        "n_rows_used": int(len(df)),
    }
    with open(os.path.join(tr.MODELS_DIR, "best_classifier.pkl"), "wb") as f:
        pickle.dump(payload, f)

    out = {
        "task": "classification",
        "target": TARGET,
        "classes": labels,
        "features": list(X.columns),
        "n_total_rows": n_total,
        "n_rows_used": int(len(df)),
        "n_rows_dropped": int(n_total - len(df)),
        "class_support": {k: int(v) for k, v in df["yc"].value_counts().items()},
        "n_campaigns": int(df["campaign_id"].nunique()),
        "cv": f"GroupKFold({N_SPLITS}) on campaign_id",
        "random_state": SEED,
        "models": results,
        "baseline_balanced_accuracy": base_ba,
        "selected_model": chosen,
        "selection_reason": reason,
    }
    with open(
        os.path.join(tr.REPORTS_DIR, "classification_metrics.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2)

    write_report(out, results, labels, base_ba, chosen, reason, y)
    print(f"saved : models/best_classifier.pkl  ({chosen})")
    print("saved : reports/classification_metrics.json")
    print("saved : reports/classification_report.md")


def _oof_of(results, chosen, y, X, groups, labels):
    # recompute OOF for the chosen model (cheap; used for the printed report)
    gkf = GroupKFold(n_splits=N_SPLITS)
    oof = np.full(len(y), "", dtype=object)
    for itr, ite in gkf.split(X, y, groups):
        Xtr, Xte = tr.impute(X.iloc[itr], X.iloc[ite])
        m = SPECS[chosen]().fit(Xtr, y[itr])
        oof[ite] = m.predict(Xte)
    return oof


def write_report(out, results, labels, base_ba, chosen, reason, y):
    L = []
    L.append("# Task 2 — Classification Report: `test_end`\n")
    L.append("## Setup\n")
    L.append(f"- **Target:** `{TARGET}` — classes: {', '.join('`'+c+'`' for c in labels)}")
    L.append(f"- **Features:** {', '.join('`'+c+'`' for c in out['features'])}")
    L.append(
        "- **Encoding:** `fuel` → binary `fuel_methanol`; numeric features median-imputed "
        "(fit per training fold)."
    )
    L.append(
        f"- **Rows:** {out['n_rows_used']} used of {out['n_total_rows']} "
        f"(dropped {out['n_rows_dropped']} with empty class). Class support: {out['class_support']}."
    )
    L.append(
        f"- **CV:** `GroupKFold(5)` on `campaign_id` ({out['n_campaigns']} campaigns) — no leakage."
    )
    L.append(f"- **random_state:** {out['random_state']}.\n")

    L.append("## Results (out-of-fold)\n")
    L.append("| Model | Balanced accuracy | Macro-F1 | vs baseline (bal.acc) |")
    L.append("|---|---:|---:|---:|")
    for name in ["baseline_most_frequent", "logistic_regression", "random_forest"]:
        r = results[name]["oof"]
        gain = (r["balanced_accuracy"] - base_ba) / base_ba * 100
        L.append(
            f"| `{name}` | {r['balanced_accuracy']:.4f} | {r['macro_f1']:.4f} | {gain:+.1f}% |"
        )
    L.append("")

    L.append(f"### Confusion matrix — `{chosen}` (OOF, rows = true, cols = predicted)\n")
    cm = results[chosen]["oof"]["confusion_matrix"]
    L.append("| true \\ pred | " + " | ".join(labels) + " |")
    L.append("|---|" + "---:|" * len(labels))
    for i, lab in enumerate(labels):
        L.append(f"| **{lab}** | " + " | ".join(str(v) for v in cm[i]) + " |")
    L.append("")

    L.append("## Selected model\n")
    L.append(f"**`{chosen}`** — {reason}\n")
    L.append(f"Saved to `models/best_classifier.pkl` (refit on all {out['n_rows_used']} rows).\n")

    L.append("## Notes & caveats\n")
    L.append(
        "- Baseline = majority class (`Extinction`) — balanced accuracy ≈ 0.33 by construction; "
        "the ML models must beat it on a per-class-fair basis."
    )
    L.append(
        "- Classes are imbalanced (Extinction 186 / Disruption 61 / Completion 27), hence "
        "`class_weight='balanced'` and balanced-accuracy / macro-F1 as metrics."
    )
    L.append(
        "- `Completion` (27 samples) is the hardest class; its per-class recall dominates macro metrics."
    )
    L.append(
        "- Prediction is only valid **inside the observed range** (O₂ ≈ 0.12–0.34, "
        "pressure ≈ 0.5–3.1 atm, d₀ ≈ 1.1–4.67 mm). **No extrapolation.**"
    )
    L.append("- No deep learning used, per project rules.\n")

    with open(
        os.path.join(tr.REPORTS_DIR, "classification_report.md"), "w", encoding="utf-8"
    ) as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()
