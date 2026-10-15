# FLEX Explorer — Microgravity Fire Safety

An interactive web app that explores NASA's **FLEX (Flame Extinguishment Experiment)**
dataset on droplet combustion in microgravity — visualizing d² burning curves,
burning-rate constants *k*, and extinction behaviour for methanol & heptane droplets.
It also ships trained **machine-learning models** (burning rate + test outcome) and a
transparent "how it was computed" methodology section.

> تطبيق تفاعلي يستكشف بيانات NASA FLEX عن احتراق القطيرات في الجاذبية الصغرى،
> ويعرض منحنيات d²، معدلات الاحتراق k، وسلوك الانطفاء، مع نماذج تعلّم آلي مدرّبة
> وشرح كامل لمصدر البيانات ومنهجية التقييم.

🔗 **Live:** https://mnb60704-netizen.github.io/flex-explorer/

---

## 📊 Data Source
- **Dataset:** NASA PSI-69 — FLEX (Flame Extinguishment Experiment), **Version 5**
- **DOI:** [10.60555/mbq8-0451](https://doi.org/10.60555/mbq8-0451)
- **License:** CC0-1.0 (public domain)
- **Official page:** https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
- **Rows:** 274 experiments × 16 columns (`data/flex_clean.csv`, re-encoded cp1252 → UTF-8, no rows dropped)
- **Download record:** `data/provenance.csv` (URL, access date, row/column count, raw sha256)
- **Checksums:** raw `flex_data.csv`
  `37c88ce8ae9391b7544ff630a45ce87543d04d317cdbfbed104fe7d5c27e1b96` ·
  clean `flex_clean.csv`
  `16f300da016b0d06c6e4a579008b1307799663ec7192cdd1f352d15818d431e2`

> **Space vs. ground:** the PSI-69 description states FLEX uses *both* space-based data
> and extensive ground-based tests, and the table has **no column marking which row is
> which** — so this project never claims an individual row is a space experiment.

## ✨ Features
- **Filters:** Fuel (All / Methanol / Heptane) · O₂ mole fraction (0.10–0.35) ·
  Pressure (0.5–3.1 atm) · Test end (All / Extinction / Disruption / Completion) ·
  **Diluent gas** (N₂ / CO₂ / He) · **Reset**
- **Live KPIs** recomputed from the current selection (records, median *k* + IQR,
  median burn time, share of Extinction, observed O₂ range, missing-value count)
- **Chart 1 —** d² vs burn time (one segment per test: `(0, d₀²) → (t_burn, d_ext²)`)
- **Chart 2 —** burning-rate constant **k** vs O₂ mole fraction (scatter, colored by fuel)
- **Chart 3 —** extinction diameter vs O₂ mole fraction (scatter, colored by fuel)
- **Chart 4 —** how tests end (Extinction / Disruption / Completion, per fuel)
- **Compare & rank conditions —** group by fuel / O₂ band / pressure band / diluent,
  sortable table with n, median *k*, IQR, % Extinction, median O₂
- **Filter-aware insights** — each card is labelled *ملاحظة من البيانات* (computed from
  the rows) vs *تفسير محتمل* (sourced interpretation), with the source line
- **Ask the data —** deterministic Q&A computed locally from the filtered rows
  (no LLM, no external service); it refuses to invent an answer when the data is insufficient
- **Table —** all 16 columns of the filtered experiments, with `quality_flag` badges
- **ML Results —** metrics read from `reports/*.json` + figures (see below)
- **Data source & methodology —** source/DOI/license/sha256, cleaning rules, leakage
  guards, live per-column missing counts, model limits, citation

## 🎓 Machine Learning Results
Trained on the FLEX rows with **GroupKFold(5) on `campaign_id`** (derived from the
`flex_id` prefix — a campaign never spans train/test), `random_state=42`, no deep
learning. Reproduce with the scripts in [`scripts/`](scripts/).

**Regression — burning-rate constant `k` (mm²/s)** · 258 usable rows (16 dropped: empty/0 target) · 78 campaigns
| Model | MAE | RMSE | R² |
|---|---|---|---|
| baseline (mean per fuel) | 0.1026 | 0.1341 | 0.047 |
| **RandomForest** (selected) | **0.0545** | 0.0831 | **0.634** |
| HistGradientBoosting | 0.0564 | 0.0841 | 0.625 |

→ **+46.8%** MAE improvement over the baseline. Feature importance (Gini): **x_o2 (0.35)**,
initial diameter (0.23), x_he (0.19), pressure (0.08), x_co2 (0.07), x_n2 (0.05), fuel (0.03).

**Classification — `test_end` (Extinction / Disruption / Completion)** · 274 rows · 81 campaigns
| Model | Balanced acc | Macro-F1 |
|---|---|---|
| baseline (majority class) | 0.333 | 0.270 |
| **LogisticRegression** (selected) | **0.631** | **0.576** |
| RandomForest | 0.547 | 0.532 |

→ **+89%** balanced accuracy over the baseline. OOF confusion matrix
(rows = true, cols = pred, order Completion/Disruption/Extinction):
`[[15,6,6],[15,39,7],[34,22,130]]`.

📈 Full reports: [`reports/regression_report.md`](reports/regression_report.md) ·
[`reports/classification_report.md`](reports/classification_report.md) — machine-readable
metrics in `reports/*_metrics.json` + `reports/feature_importance.json`, figures in
[`reports/figures/`](reports/figures/).

⚠️ **Known limitation:** the *Completion* class is weak (only 27 samples; precision 0.23,
recall 0.56) and is often confused with *Disruption*. Predictions are valid only
**inside the observed ranges** (no extrapolation).

## ▶️ How to Run
The app needs a local HTTP server (browsers block `fetch()` of local files on `file://`).
Run it from the repository root:
```bash
python -m http.server 8000
```
Then open **http://localhost:8000/** — or use the GitHub Pages link above.

**Retrain the models** (writes `models/*.pkl` and `reports/*`):
```bash
python scripts/train_regression.py
python scripts/train_classification.py
python scripts/analyze_regression.py     # figures + reports/feature_importance.json
```

**Verify everything** (data hashes, distributions, and that the stored metrics
reproduce bit-for-bit; no network, no writes):
```bash
python scripts/test_project.py
```

## 📖 Data Dictionary
Every column (meaning · unit · source) is documented in
[`data_dictionary.md`](data_dictionary.md).

Note: the original PSI header reads `Burning rate; mm`, but the real unit is **mm²/s**
(burning-rate constant *k*), as documented in NASA/TP-2015-216046.

## ⚠️ Limitations
- This is a **research / data-exploration tool — not a certified fire-safety system**.
- It does **not** predict fires on spacecraft or any real vehicle.
- The table does **not** distinguish space-based from ground-based tests — no per-row claim is made.
- ML models are valid only inside the observed input ranges
  (O₂ ≈ 0.12–0.34 · 0.5–3.1 atm · d₀ ≈ 1.1–4.67 mm); no extrapolation.
- `burning_rate` is in **mm²/s**; the original PSI header is missing the `/s`.
- *Completion* is the weakest predicted class (27 samples): low precision/recall — interpret with caution.
- One row (`test_id 114`) has no recorded pressure (`pressure_atm = 0`) and is excluded by the pressure filter.

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
