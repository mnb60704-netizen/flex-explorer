# Task 2 — Classification Report: `test_end`

## Setup

- **Target:** `test_end` — classes: `Completion`, `Disruption`, `Extinction`
- **Features:** `pressure_atm`, `x_o2`, `x_n2`, `x_co2`, `x_he`, `initial_diameter_mm`, `fuel_methanol`
- **Encoding:** `fuel` → binary `fuel_methanol`; numeric features median-imputed (fit per training fold).
- **Rows:** 274 used of 274 (dropped 0 with empty class). Class support: {'Extinction': 186, 'Disruption': 61, 'Completion': 27}.
- **CV:** `GroupKFold(5)` on `campaign_id` (81 campaigns) — no leakage.
- **random_state:** 42.

## Results (out-of-fold)

| Model | Balanced accuracy | Macro-F1 | vs baseline (bal.acc) |
|---|---:|---:|---:|
| `baseline_most_frequent` | 0.3333 | 0.2696 | +0.0% |
| `logistic_regression` | 0.6313 | 0.5764 | +89.4% |
| `random_forest` | 0.5474 | 0.5315 | +64.2% |

### Confusion matrix — `logistic_regression` (OOF, rows = true, cols = predicted)

| true \ pred | Completion | Disruption | Extinction |
|---|---:|---:|---:|
| **Completion** | 15 | 6 | 6 |
| **Disruption** | 15 | 39 | 7 |
| **Extinction** | 34 | 22 | 130 |

## Selected model

**`logistic_regression`** — logistic_regression has the highest OOF balanced accuracy (0.6313); no simpler model is within 5% of it.

Saved to `models/best_classifier.pkl` (refit on all 274 rows).

## Notes & caveats

- Baseline = majority class (`Extinction`) — balanced accuracy ≈ 0.33 by construction; the ML models must beat it on a per-class-fair basis.
- Classes are imbalanced (Extinction 186 / Disruption 61 / Completion 27), hence `class_weight='balanced'` and balanced-accuracy / macro-F1 as metrics.
- `Completion` (27 samples) is the hardest class; its per-class recall dominates macro metrics.
- Prediction is only valid **inside the observed range** (O₂ ≈ 0.12–0.34, pressure ≈ 0.5–3.1 atm, d₀ ≈ 1.1–4.67 mm). **No extrapolation.**
- No deep learning used, per project rules.
