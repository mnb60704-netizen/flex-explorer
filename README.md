# FLEX Explorer — Microgravity Fire Safety

An interactive web app that explores NASA's **FLEX (Flame Extinguishment Experiment)**
dataset on droplet combustion in microgravity — visualizing d² burning curves,
burning-rate constants *k*, and extinction behaviour for methanol & heptane droplets.
It also ships trained **machine-learning models** (burning rate + test outcome).

> تطبيق تفاعلي يستكشف بيانات NASA FLEX عن احتراق القطيرات في الجاذبية الصغرى،
> ويعرض منحنيات d²، معدلات الاحتراق k، وسلوك الانطفاء، مع نماذج تعلّم آلي مدرّبة.

🔗 **Live:** https://mnb60704-netizen.github.io/flex-explorer/

---

## 📊 Data Source
- **Dataset:** NASA PSI-69 — FLEX (Flame Extinguishment Experiment), **Version 5**
- **DOI:** [10.60555/mbq8-0451](https://doi.org/10.60555/mbq8-0451)
- **License:** CC0-1.0 (public domain)
- **Official page:** https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
- **Rows:** 274 experiments

## ✨ Features
- **Filters:** Fuel (All / Methanol / Heptane) · O₂ mole-fraction range (0.10–0.35) ·
  Pressure range (0.5–3.1 atm) · Test end (All / Extinction / Disruption / Completion) · **Reset**
- **Chart 1 —** d² vs burn time (one line segment per test: `(0, d₀²) → (t_burn, d_ext²)`)
- **Chart 2 —** Burning-rate constant **k** (mm²/s) per test, colored by fuel
- **Chart 3 —** Extinction diameter vs O₂ mole fraction (scatter, colored by fuel)
- **Table —** all 16 columns of the filtered experiments, with `quality_flag` badges
- **ML Results —** summary of the trained models + figures (see below)

## 🎓 Machine Learning Results
Trained on all **274 experiments** with **GroupKFold(5) on `campaign_id`** (no leakage —
a campaign never spans train/test), `random_state=42`. Reproduce with the scripts in
[`scripts/`](scripts/).

**Regression — burning-rate constant `k` (mm²/s)** · 258 usable rows
| Model | MAE | RMSE | R² |
|---|---|---|---|
| baseline (mean per fuel) | 0.1026 | 0.1341 | 0.047 |
| **RandomForest ⭐** | **0.0545** | 0.0831 | **0.634** |
| HistGradientBoosting | 0.0564 | 0.0841 | 0.625 |

→ **+46.8%** MAE improvement over baseline. Top features: **x_o2 (0.35)**, initial
diameter (0.23), x_he (0.19).

**Classification — `test_end` (Extinction / Disruption / Completion)** · 274 rows
| Model | Balanced acc | Macro-F1 |
|---|---|---|
| baseline (majority class) | 0.333 | 0.270 |
| **LogisticRegression ⭐** | **0.631** | **0.576** |
| RandomForest | 0.547 | 0.532 |

→ **+89%** balanced accuracy over baseline.

📈 Full reports: [`reports/regression_report.md`](reports/regression_report.md) ·
[`reports/classification_report.md`](reports/classification_report.md) — figures in
[`reports/figures/`](reports/figures/).

⚠️ **Known limitation:** the *Completion* class is weak (only 27 samples; recall 0.56,
precision 0.23) and is often confused with *Disruption*. Predictions are valid only
**inside the observed ranges** (no extrapolation).
Completion class (27 samples) has low precision/recall due to limited sample size; results for this class should be interpreted with caution.

## ▶️ How to Run
The app needs a local HTTP server (browsers block `fetch()` of local files on `file://`).
Run it from the repository root:
```bash
python -m http.server 8000
```
Then open **http://localhost:8000/** — or use the GitHub Pages link above.

## 📖 Data Dictionary
Every column (meaning · unit · source) is documented in
[`data_dictionary.md`](data_dictionary.md).

Note: the original PSI header reads `Burning rate; mm`, but the real unit is **mm²/s**
(burning-rate constant *k*), as documented in NASA/TP-2015-216046.

## ⚠️ Limitations
- This is a **research / data-exploration tool — not a certified fire-safety system**.
- It does **not** predict fires on spacecraft or any real vehicle.
- `burning_rate` is in **mm²/s**; the original PSI header is missing the `/s`.
- ML models are valid only inside the observed input ranges (no extrapolation).
- *Completion* is the weakest predicted class (27 samples): low precision/recall — interpret with caution.

## 📚 Citation
**Data**
> NASA Physical Sciences Informatics (PSI). *PSI-69 — Flame Extinguishment Experiment
> (FLEX), Version 5* [Data set]. NASA. https://doi.org/10.60555/mbq8-0451

**Reference report**
> NASA/TP-2015-216046 — *Flame Extinguishment Experiment (FLEX)*, NASA Technical
> Publication. https://ntrs.nasa.gov/citations/20150023456

## 📄 License
- **Data:** CC0-1.0
- **Code:** MIT
