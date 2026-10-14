# FLEX Explorer — Microgravity Fire Safety

An interactive web app that explores NASA's **FLEX (Flame Extinguishment Experiment)**
dataset on droplet combustion in microgravity — visualizing d² burning curves,
burning-rate constants *k*, and extinction behaviour for methanol & heptane droplets.

> تطبيق تفاعلي يستكشف بيانات NASA FLEX عن احتراق القطيرات في الجاذبية الصغرى،
> ويعرض منحنيات d²، معدلات الاحتراق k، وسلوك الانطفاء.

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

## ▶️ How to Run
The app needs a local HTTP server (browsers block `fetch()` of local files on `file://`):
```bash
cd flex-explorer
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
