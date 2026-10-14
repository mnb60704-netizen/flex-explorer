# data/model_ready — Model-Ready FLEX Dataset

A tidy, training-ready bundle derived from the official NASA PSI-69 FLEX export.
**Nothing here was filtered or deleted** — all **274 experiments** are present.

## 📦 What's in this folder

| File | Rows | Purpose |
|---|---:|---|
| `flex_train.csv` | 274 | **Inputs** (features) + context columns. Includes all 14 columns except `test_date`/`test_gmt`. |
| `flex_targets.csv` | 274 | **Targets** only, kept separate: `test_id`, `target_regression` (k), `target_classification` (test_end), `target_regression_2` (extinction d). |
| `flex_features.md` | — | What the inputs vs targets are, and what is deliberately excluded. |
| `split_plan.md` | — | The future cross-validation plan (GroupKFold on `campaign_id`). |
| `README.md` | — | This file. |

The `flex_train.csv` column order is:
```
test_id, flex_id, fuel, pressure_atm, x_o2, x_n2, x_co2, x_he,
initial_diameter_mm, extinction_diameter_mm, burning_rate_mm2_s,
burn_time_s, test_end, quality_flag
```

## 🎯 Inputs vs targets

- **Features:** `fuel`, `pressure_atm`, `x_o2`, `x_n2`, `x_co2`, `x_he`, `initial_diameter_mm`
- **Targets:**
  - `burning_rate_mm2_s` → **regression** (mm²/s)
  - `test_end` → **classification** (`Extinction` / `Disruption` / `Completion`)
  - `extinction_diameter_mm` → **second regression** (mm)

Targets live in `flex_targets.csv`; **join back on `test_id`** at training time.

## 🧪 How it will be used later

1. Load `flex_train.csv` (features) and `flex_targets.csv` (targets).
2. Merge on `test_id`.
3. Split with **`GroupKFold(5)` on `campaign_id`** (see `split_plan.md`) — no row-level random splits.
4. Train simple, interpretable models per target (see constraints below).
5. Filter (`quality_flag`, `extinction_diameter_mm = 0`) **after** splitting, per target.

## ⚠️ Constraints

- **No extrapolation:** predictions are only meaningful **inside the observed ranges**
  (O₂ ≈ 0.12–0.34, pressure ≈ 0.5–3.1 atm, d₀ ≈ 1.1–4.67 mm). Do not extrapolate.
- **No deep learning:** this is a small (274-row), structured, physics-driven table.
  Use interpretable models (linear/regularized regression, gradient-boosted trees, etc.) —
  deep nets would overfit and are not warranted.
- **Respect the groups:** keep campaigns intact across train/test.
- **Unit caveat:** `burning_rate_mm2_s` is **mm²/s** (PSI header missing `/s`).
- **Do not edit the source:** `data/flex_clean.csv` is authoritative and must not be modified;
  these files are copies/derivations of it.
