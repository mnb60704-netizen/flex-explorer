"""Task 1 — Regression: predict burning_rate_mm2_s for the FLEX dataset.

Rules honoured:
- Uses data/model_ready/flex_train.csv + flex_targets.csv.
- Drops rows whose target is empty or 0.
- GroupKFold(5) on campaign_id (derived from the flex_id prefix) -> no leakage.
- random_state = 42 everywhere.
- No deep learning.
"""
import json
import os
import pickle
import re
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fuel_mean_regressor import FuelMeanRegressor  # noqa: E402

SEED = 42
N_SPLITS = 5
BOOT = 10000

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN_CSV = os.path.join(PROJ, "data", "model_ready", "flex_train.csv")
TARGETS_CSV = os.path.join(PROJ, "data", "model_ready", "flex_targets.csv")
MODELS_DIR = os.path.join(PROJ, "models")
REPORTS_DIR = os.path.join(PROJ, "reports")

FEATURES = ["pressure_atm", "x_o2", "x_n2", "x_co2", "x_he", "initial_diameter_mm"]
NUM_COLS = FEATURES
TARGET = "burning_rate_mm2_s"


def campaign_id(fid):
    fid = str(fid)
    if "CAL" in fid:
        return fid[: fid.index("CAL") + 3]
    return re.sub(r"[HMRF]\d+$", "", fid)


def load():
    tr = pd.read_csv(TRAIN_CSV)
    tg = pd.read_csv(TARGETS_CSV)
    df = tr.merge(tg, on="test_id")
    df["campaign_id"] = df["flex_id"].map(campaign_id)
    df["y"] = pd.to_numeric(df["target_regression"], errors="coerce")
    n_total = len(df)
    df = df[df["y"].notna() & (df["y"] != 0)].copy().reset_index(drop=True)
    return df, n_total


def build_X(df):
    X = df[NUM_COLS].copy()
    X["fuel_methanol"] = (df["fuel"].astype(str).str.lower() == "methanol").astype(int).values
    return X


def impute(Xtr, Xte):
    Xtr = Xtr.copy()
    Xte = Xte.copy()
    med = Xtr[NUM_COLS].median()
    Xtr[NUM_COLS] = Xtr[NUM_COLS].fillna(med)
    Xte[NUM_COLS] = Xte[NUM_COLS].fillna(med)
    return Xtr, Xte


def metrics(y, p):
    return {
        "mae": float(mean_absolute_error(y, p)),
        "rmse": float(np.sqrt(mean_squared_error(y, p))),
        "r2": float(r2_score(y, p)),
    }


def boot_ci(scores, lo=5, hi=95, seed=SEED):
    s = np.asarray(scores, dtype=float)
    s = s[~np.isnan(s)]
    rng = np.random.default_rng(seed)
    draws = rng.choice(s, size=(BOOT, s.size), replace=True).mean(axis=1)
    return [float(np.percentile(draws, lo)), float(np.percentile(draws, hi))]


SPECS = {
    "baseline_fuel_mean": lambda: FuelMeanRegressor(),
    "random_forest": lambda: RandomForestRegressor(
        n_estimators=400, min_samples_leaf=2, random_state=SEED, n_jobs=-1
    ),
    "hist_gradient_boosting": lambda: HistGradientBoostingRegressor(random_state=SEED),
}
# Simplicity ranking (lower = simpler). Used for the "<5% -> prefer simpler" rule.
COMPLEXITY = {"baseline_fuel_mean": 0, "random_forest": 1, "hist_gradient_boosting": 2}


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    df, n_total = load()
    y = df["y"].to_numpy(dtype=float)
    X = build_X(df)
    groups = df["campaign_id"].to_numpy()

    print("=" * 70)
    print("TASK 1 — Regression: burning_rate_mm2_s")
    print("=" * 70)
    print(f"rows total          : {n_total}")
    print(f"rows used           : {len(df)}  (dropped {n_total - len(df)}: NaN or 0 target)")
    print(f"campaigns           : {df['campaign_id'].nunique()}  (GroupKFold({N_SPLITS}))")
    print(f"fuels -> rows        : {df['fuel'].value_counts().to_dict()}")
    print(f"features            : {list(X.columns)}")
    print(f"feature NaN (median-imputed per fold): {X[NUM_COLS].isna().sum().to_dict()}")
    print()

    gkf = GroupKFold(n_splits=N_SPLITS)
    results = {}
    for name, factory in SPECS.items():
        fold_mae, fold_rmse, fold_r2 = [], [], []
        oof = np.full(len(df), np.nan)
        for itr, ite in gkf.split(X, y, groups):
            Xtr, Xte = impute(X.iloc[itr], X.iloc[ite])
            model = factory().fit(Xtr, y[itr])
            p = model.predict(Xte)
            fold_mae.append(float(mean_absolute_error(y[ite], p)))
            fold_rmse.append(float(np.sqrt(mean_squared_error(y[ite], p))))
            fold_r2.append(float(r2_score(y[ite], p)))
            oof[ite] = p
        results[name] = {
            "oof": metrics(y, oof),
            "fold_mean": {
                "mae": float(np.mean(fold_mae)),
                "rmse": float(np.mean(fold_rmse)),
                "r2": float(np.mean(fold_r2)),
            },
            "ci90_folds": {
                "mae": boot_ci(fold_mae),
                "rmse": boot_ci(fold_rmse),
                "r2": boot_ci(fold_r2),
            },
            "fold_mae": fold_mae,
            "fold_rmse": fold_rmse,
            "fold_r2": fold_r2,
        }

    # ---------- comparison table ----------
    print("-" * 70)
    print(f"{'model':<26}{'MAE':>9}{'RMSE':>9}{'R2':>9}   MAE 90% CI (folds)")
    print("-" * 70)
    base_mae = results["baseline_fuel_mean"]["oof"]["mae"]
    for name in SPECS:
        r = results[name]["oof"]
        ci = results[name]["ci90_folds"]["mae"]
        gain = (base_mae - r["mae"]) / base_mae * 100
        print(
            f"{name:<26}{r['mae']:>9.4f}{r['rmse']:>9.4f}{r['r2']:>9.4f}   "
            f"[{ci[0]:.4f}, {ci[1]:.4f}]  ({gain:+.1f}% vs baseline)"
        )
    print("-" * 70)
    print()

    # ---------- selection ----------
    best = min(SPECS, key=lambda n: results[n]["oof"]["mae"])
    best_mae = results[best]["oof"]["mae"]
    within = [n for n in SPECS if (results[n]["oof"]["mae"] - best_mae) / best_mae < 0.05]
    chosen = min(within, key=lambda n: COMPLEXITY[n])

    if chosen == best:
        reason = (
            f"{chosen} has the lowest OOF MAE ({best_mae:.4f}); no simpler model is "
            f"within 5% of it."
        )
    else:
        gap = (results[chosen]["oof"]["mae"] - best_mae) / best_mae * 100
        reason = (
            f"{best} has the lowest OOF MAE ({best_mae:.4f}), but {chosen} is only "
            f"{gap:.2f}% worse (<5%) and is simpler, so {chosen} is selected."
        )
    print(f"selected model : {chosen}")
    print(f"reason         : {reason}")
    print()

    # ---------- refit on ALL kept rows + save ----------
    Xa = X.copy()
    Xa[NUM_COLS] = Xa[NUM_COLS].fillna(Xa[NUM_COLS].median())
    final = SPECS[chosen]().fit(Xa, y)
    payload = {
        "model": final,
        "model_name": chosen,
        "task": "regression",
        "target": TARGET,
        "features": list(X.columns),
        "categorical_encoding": {"fuel": "binary fuel_methanol (Methanol=1, Heptane=0)"},
        "imputation": "median fit on training folds (numeric features)",
        "cv": f"GroupKFold({N_SPLITS}) on campaign_id",
        "campaign_id_rule": "flex_id: if 'CAL' -> prefix through CAL; else strip trailing [HMRF]<digits>",
        "random_state": SEED,
        "n_rows_used": int(len(df)),
    }
    with open(os.path.join(MODELS_DIR, "best_regressor.pkl"), "wb") as f:
        pickle.dump(payload, f)

    out = {
        "task": "regression",
        "target": TARGET,
        "features": list(X.columns),
        "n_total_rows": n_total,
        "n_rows_used": int(len(df)),
        "n_rows_dropped": int(n_total - len(df)),
        "n_campaigns": int(df["campaign_id"].nunique()),
        "cv": f"GroupKFold({N_SPLITS}) on campaign_id",
        "random_state": SEED,
        "ci_method": "bootstrap on fold scores (B=10000, percentile, 90%)",
        "models": results,
        "baseline_mae": base_mae,
        "selected_model": chosen,
        "selection_reason": reason,
    }
    with open(os.path.join(REPORTS_DIR, "regression_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    write_report(out, results, base_mae, chosen, reason)

    print(f"saved : models/best_regressor.pkl  ({chosen})")
    print("saved : reports/regression_metrics.json")
    print("saved : reports/regression_report.md")


def write_report(out, results, base_mae, chosen, reason):
    L = []
    L.append("# Task 1 — Regression Report: `burning_rate_mm2_s`\n")
    L.append("## Setup\n")
    L.append(f"- **Target:** `{TARGET}` (mm²/s)")
    L.append(f"- **Features:** {', '.join('`'+c+'`' for c in out['features'])}")
    L.append(
        "- **Encoding:** `fuel` → binary `fuel_methanol` (Methanol=1, Heptane=0); "
        "numeric features median-imputed (fit per training fold)."
    )
    L.append(
        f"- **Rows:** {out['n_rows_used']} used of {out['n_total_rows']} "
        f"(dropped {out['n_rows_dropped']} with empty/zero target)."
    )
    L.append(
        f"- **CV:** `GroupKFold(5)` on `campaign_id` ({out['n_campaigns']} campaigns) — "
        "groups never split across folds (no leakage)."
    )
    L.append(f"- **random_state:** {out['random_state']} (models + bootstrap).")
    L.append(f"- **CI:** {out['ci_method']}.\n")

    L.append("## Results (out-of-fold)\n")
    L.append("| Model | MAE | RMSE | R² | MAE 90% CI (folds) | vs baseline |")
    L.append("|---|---:|---:|---:|---|---:|")
    order = ["baseline_fuel_mean", "random_forest", "hist_gradient_boosting"]
    for name in order:
        r = results[name]["oof"]
        ci = results[name]["ci90_folds"]["mae"]
        gain = (base_mae - r["mae"]) / base_mae * 100
        L.append(
            f"| `{name}` | {r['mae']:.4f} | {r['rmse']:.4f} | {r['r2']:.4f} | "
            f"[{ci[0]:.4f}, {ci[1]:.4f}] | {gain:+.1f}% |"
        )
    L.append("")

    L.append("### Per-fold MAE\n")
    L.append("| Model | fold1 | fold2 | fold3 | fold4 | fold5 |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for name in order:
        fm = results[name]["fold_mae"]
        L.append(f"| `{name}` | " + " | ".join(f"{v:.4f}" for v in fm) + " |")
    L.append("")

    L.append("## Selected model\n")
    L.append(f"**`{chosen}`** — {reason}\n")
    L.append(f"Saved to `models/best_regressor.pkl` (refit on all {out['n_rows_used']} kept rows).\n")

    L.append("## Notes & caveats\n")
    L.append(
        "- Baseline = training mean of `burning_rate_mm2_s` per fuel class "
        "(no other features used) — the reference the ML models must beat."
    )
    L.append(
        "- Metrics on out-of-fold predictions; the 90% CI is a bootstrap over the "
        "5 fold scores, so it is intentionally coarse."
    )
    L.append(
        "- Prediction is only valid **inside the observed range** "
        f"(O₂ ≈ 0.12–0.34, pressure ≈ 0.5–3.1 atm, d₀ ≈ 1.1–4.67 mm). **No extrapolation.**"
    )
    L.append("- No deep learning used, per project rules.\n")

    with open(os.path.join(REPORTS_DIR, "regression_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()
