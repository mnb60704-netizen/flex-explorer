"""Task 1 add-on — Feature importance + residual analysis for the regression model.

Uses out-of-fold (OOF) predictions from the same GroupKFold(5) scheme to avoid
leakage. Produces figures and appends two sections to the regression report.
"""
import os
import pickle
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.inspection import permutation_importance  # noqa: E402
from sklearn.metrics import mean_absolute_error, r2_score  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import train_regression as tr  # noqa: E402

SEED = tr.SEED
FIGS = os.path.join(tr.REPORTS_DIR, "figures")
os.makedirs(FIGS, exist_ok=True)

DISPLAY = {
    "pressure_atm": "pressure_atm",
    "x_o2": "x_o2",
    "x_n2": "x_n2",
    "x_co2": "x_co2",
    "x_he": "x_he",
    "initial_diameter_mm": "initial_diameter_mm",
    "fuel_methanol": "fuel (methanol)",
}
PHYS = {
    "initial_diameter_mm": "droplet size sets the burning-rate envelope (d²-law and radiative/conductive losses scale with diameter)",
    "pressure_atm": "ambient pressure sets the O₂ partial pressure and flame standoff, which govern d²-law burning",
    "x_o2": "oxygen mole fraction controls oxidizer availability and flame temperature — a primary driver of burning rate",
    "x_n2": "N₂ is the diluent: more N₂ lowers the O₂ partial pressure and heat release, slowing burning",
    "x_co2": "CO₂ is a strong heat-capacity diluent that suppresses flame temperature more than N₂",
    "x_he": "He changes mixture transport properties and heat loss (light, high-conductivity diluent)",
    "fuel_methanol": "methanol vs heptane differ in sooting tendency and heat of combustion, shifting absolute rates",
}


def main():
    df, _ = tr.load()
    y = df["y"].to_numpy(dtype=float)
    X = tr.build_X(df)
    groups = df["campaign_id"].to_numpy()
    feats = list(X.columns)

    # --- OOF predictions for the selected model (random_forest) ---
    gkf = GroupKFold(n_splits=tr.N_SPLITS)
    oof = np.full(len(df), np.nan)
    perm = np.zeros(len(feats))
    nf = 0
    for itr, ite in gkf.split(X, y, groups):
        Xtr, Xte = tr.impute(X.iloc[itr], X.iloc[ite])
        m = tr.SPECS["random_forest"]().fit(Xtr, y[itr])
        oof[ite] = m.predict(Xte)
        pi = permutation_importance(
            m, Xte, y[ite], n_repeats=30, random_state=SEED, scoring="neg_mean_absolute_error"
        )
        perm += pi.importances_mean
        nf += 1
    perm /= nf

    # --- built-in importance from the final saved model ---
    with open(os.path.join(tr.MODELS_DIR, "best_regressor.pkl"), "rb") as f:
        final = pickle.load(f)["model"]
    gini = np.asarray(final.feature_importances_)

    # ---------- Figure 1: feature importance (built-in, sorted desc) ----------
    order = np.argsort(gini)[::-1]
    labels = [DISPLAY[feats[i]] for i in order]
    vals = gini[order]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(range(len(vals))[::-1], vals, color="#4c8dff")
    ax.set_yticks(range(len(vals))[::-1])
    ax.set_yticklabels(labels[::-1] if False else [DISPLAY[feats[i]] for i in order][::-1])
    ax.set_xlabel("RF importance (Gini)")
    ax.set_title("Feature importance — burning_rate_mm2_s (RandomForest)")
    for b, v in zip(bars, vals[::-1]):
        ax.text(b.get_width() + max(vals) * 0.01, b.get_y() + b.get_height() / 2,
                f"{v:.3f}", va="center", fontsize=9)
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "feature_importance.png"), dpi=140)
    plt.close(fig)

    top3 = [feats[i] for i in order[:3]]

    # ---------- Figure 2: actual vs predicted ----------
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y, oof, s=14, alpha=0.6, color="#35d0ff", edgecolor="none")
    lo, hi = float(min(y.min(), oof.min())), float(max(y.max(), oof.max()))
    ax.plot([lo, hi], [lo, hi], "r--", lw=1.2, label="y = x")
    ax.set_xlabel("actual burning_rate_mm2_s")
    ax.set_ylabel("predicted (OOF)")
    ax.set_title(f"Actual vs predicted — R²={r2_score(y, oof):.3f}, MAE={mean_absolute_error(y, oof):.3f}")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "actual_vs_predicted.png"), dpi=140)
    plt.close(fig)

    # ---------- Figure 3: residuals vs predicted ----------
    resid = y - oof
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(oof, resid, s=14, alpha=0.6, color="#ff8a3d", edgecolor="none")
    ax.axhline(0, color="r", ls="--", lw=1.2)
    ax.set_xlabel("predicted (OOF)")
    ax.set_ylabel("residual = actual - predicted")
    ax.set_title("Residuals vs predicted")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "residuals_vs_predicted.png"), dpi=140)
    plt.close(fig)

    # ---------- residual statistics ----------
    corr = float(np.corrcoef(oof, resid)[0, 1])
    mean_r = float(np.mean(resid))
    fuel = df["fuel"].astype(str).to_numpy()
    mr = {f: float(np.mean(resid[fuel == f])) for f in ["Methanol", "Heptane"]}
    within_05 = float(np.mean(np.abs(resid) <= 0.05) * 100)
    within_10 = float(np.mean(np.abs(resid) <= 0.10) * 100)

    print("=== feature importance (Gini) ===")
    for i in order:
        print(f"  {feats[i]:22s} gini={gini[i]:.3f}  perm={perm[i]:+.4f}")
    print()
    print("=== residual stats (OOF) ===")
    print(f"  mean residual        : {mean_r:+.4f}")
    print(f"  std residual         : {float(np.std(resid)):.4f}")
    print(f"  corr(pred, residual) : {corr:+.3f}")
    print(f"  mean resid by fuel   : {mr}")
    print(f"  within +/-0.05       : {within_05:.1f}%")
    print(f"  within +/-0.10       : {within_10:.1f}%")

    # ---------- write report sections ----------
    fi = []
    fi.append("## Feature Importance (RandomForest)\n")
    fi.append("![feature importance](figures/feature_importance.png)\n")
    fi.append("| Rank | Feature | Gini importance | Permutation (ΔMAE, fold-avg) |")
    fi.append("|---:|---|---:|---:|")
    for r, i in enumerate(order, 1):
        fi.append(f"| {r} | `{DISPLAY[feats[i]]}` | {gini[i]:.3f} | {perm[i]:+.4f} |")
    fi.append("")
    fi.append("**Interpretation (top 3):**")
    for k in range(3):
        fi.append(f"{k+1}. `{DISPLAY[top3[k]]}` — {PHYS[top3[k]]}.")
    fi.append("")
    fi.append("All three are direct physical controls of droplet burning: the top drivers are the "
              "oxidizer/diluent composition and the droplet size, consistent with d²-law combustion "
              "where ambient composition and initial diameter set the burning-rate envelope.\n")

    rs = []
    rs.append("## Residual Analysis\n")
    rs.append("![actual vs predicted](figures/actual_vs_predicted.png)\n")
    rs.append("![residuals vs predicted](figures/residuals_vs_predicted.png)\n")
    rs.append(f"- Mean residual (actual − predicted): **{mean_r:+.4f}** (≈0 → low overall bias).")
    rs.append(f"- Residual std: **{float(np.std(resid)):.4f}**; corr(predicted, residual) = **{corr:+.3f}**.")
    rs.append(f"- Mean residual by fuel: Methanol {mr['Methanol']:+.4f}, Heptane {mr['Heptane']:+.4f}.")
    rs.append(f"- |error| ≤ 0.05 in **{within_05:.1f}%** of tests; ≤ 0.10 in **{within_10:.1f}%**.")
    rs.append("")
    if abs(corr) < 0.2 and abs(mean_r) < 0.02:
        verdict = ("The residuals scatter randomly around 0 with no strong trend versus the "
                   "predicted value (|corr| < 0.2), so there is **no pronounced systematic bias**.")
    else:
        verdict = ("A mild trend is visible (corr between predicted and residual = "
                   f"{corr:+.3f}); the model slightly "
                   + ("under-predicts higher burning rates" if corr < 0 else "over-predicts higher burning rates")
                   + " — worth noting but limited.")
    rs.append(verdict)
    rs.append("")

    report_path = os.path.join(tr.REPORTS_DIR, "regression_report.md")
    with open(report_path, encoding="utf-8") as f:
        base = f.read()
    if "\n## Feature Importance" in base:
        base = base[: base.index("\n## Feature Importance")]
    base = base.rstrip() + "\n\n" + "\n".join(fi) + "\n" + "\n".join(rs) + "\n"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(base)
    print()
    print("updated : reports/regression_report.md")
    print("saved   : reports/figures/feature_importance.png, actual_vs_predicted.png, residuals_vs_predicted.png")


if __name__ == "__main__":
    main()
