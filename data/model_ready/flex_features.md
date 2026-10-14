# FLEX — Model-Ready Features & Targets

**Folder contents used for modeling:**
- `flex_train.csv` — inputs (features) + context columns (**274 rows**, no date/time columns).
- `flex_targets.csv` — targets, kept **separate** from inputs.

> ⚠️ No rows were removed. All 274 experiments are present in both files.
> Filtering (e.g. dropping `quality_flag != "ok"` or `extinction_diameter_mm = 0`)
> happens **in code at training time — not in these files**.

---

## ✅ Features (inputs)

| Feature | Type | Unit | Notes |
|---|---|---|---|
| `fuel` | categorical | — | `Methanol` / `Heptane` (encode: one-hot or 0/1) |
| `pressure_atm` | numeric | atm | ambient pressure (`mmHg/760`) |
| `x_o2` | numeric | mole fraction | oxidizer |
| `x_n2` | numeric | mole fraction | diluent (default) |
| `x_co2` | numeric | mole fraction | diluent |
| `x_he` | numeric | mole fraction | diluent |
| `initial_diameter_mm` | numeric | mm | droplet initial diameter (d₀) |

**Composition is constrained:** `x_o2 + x_n2 + x_co2 + x_he = 1` → features are linearly
dependent (for linear models, consider dropping one or using 3 of them).
Diluents are mutually exclusive: `x_co2>0` → CO₂, else `x_he>0` → He, else N₂.

## 🎯 Targets

| Target (this name in `flex_targets.csv`) | Source column | Task | Unit / classes |
|---|---|---|---|
| `target_regression` | `burning_rate_mm2_s` | regression | **mm²/s** |
| `target_classification` | `test_end` | classification | `Extinction` / `Disruption` / `Completion` |
| `target_regression_2` | `extinction_diameter_mm` | regression | mm |

---

## 🚫 Not used as features

- `test_date`, `test_gmt` — time metadata (excluded from `flex_train.csv`).
- `test_id`, `flex_id` — identifiers (for joins/tracing only, not model inputs).
- `quality_flag` — data-quality metadata (used for filtering, not as an input).
- `burn_time_s` — coupled with the targets (potential leakage) → treated as context, not an input.
- `extinction_diameter_mm` — it **is** a target (`target_regression_2`); never feed it as an
  input when predicting itself.

---

## 📌 Notes & caveats

- **Unit:** `burning_rate_mm2_s` is in **mm²/s** — the original PSI header `Burning rate; mm`
  is missing the `/s` (documented in NASA/TP-2015-216046).
- **`extinction_diameter_mm = 0`** means **"not measured"**, not a physical value
  (a zero extinction diameter is impossible). Treat it as missing.
- **`test_id = 114`** (`C11M201`) has `pressure_atm = 0` → `quality_flag = "missing_pressure"`.
- **No row deletion** — the dataset stays complete; any filtering is the modeler's choice in code.
