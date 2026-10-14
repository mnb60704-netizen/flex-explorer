# FLEX Clean Data Dictionary

**Dataset:** `data/flex_clean.csv` — نظيف/مُعاد تسميته من تصدير PSI-69 الرسمي.
**Source file:** `data/flex_data.csv` (تصدير خام، ترميز Windows‑1252/cp1252).
**Rows:** 274 · **Columns:** 16 · **Encoding (clean):** UTF‑8.
**Provenance:** `data/provenance.csv` (الرابط + تاريخ الوصول + `sha256`).

> ⚠️ **ملاحظة الوحدة (مهمة):** العمود الأصلي في PSI اسمه حرفيًا `Burning rate; mm` — لكن وحدته الفعلية هي **mm²/s**
> (ثابت معدّل الاحتراق `k`، "burning-rate constant"). هذا موثّق في **NASA/TP-2015-216046**
> ("…burning-rate constants…"), وفي وصف NTRS: *"Burning rate constant, K"*.
> لذلك أُعيد تسميته إلى `burning_rate_mm2_s` بدون تغيير القيم.

---

## الأعمدة / Columns

| # | Column | Meaning | Unit | Source column | Notes |
|---|--------|---------|------|---------------|-------|
| 1 | `test_id` | رقم الاختبار التسلسلي (1–274) | — | `FLEX Test #` | لا فجوات؛ 274 صفًا |
| 2 | `flex_id` | مُعرّف FLEX (كود الاختبار) | — | `FLEX Identifier` | مثل `20CAL08`, `H19H101` |
| 3 | `test_date` | تاريخ الاختبار | M/D/YYYY | `Test Date` | كما في المصدر (2009–2011) |
| 4 | `test_gmt` | وقت الاختبار (GMT) | hh:mm:ss | `Test GMT` | — |
| 5 | `fuel` | الوقود | — | `Fuel` | `Methanol` = 157 · `Heptane` = 117 |
| 6 | `pressure_atm` | الضغط المحيط — **مُحوَّل** | atm | `Ambient pressure; mmHg` | `= mmHg / 760` |
| 7 | `x_o2` | كسر الأكسجين المولي | dimensionless | `O initial ambient composition; mole fraction` | نطاق 0.12–0.34 |
| 8 | `x_n2` | كسر النيتروجين المولي | dimensionless | `N … mole fraction` | المُخفِّف الافتراضي |
| 9 | `x_co2` | كسر ثاني أكسيد الكربون المولي | dimensionless | `CO initial ambient composition; mole fraction` | 0 = غير موجود |
| 10 | `x_he` | كسر الهيليوم المولي | dimensionless | `He … mole fraction` | 0 = غير موجود |
| 11 | `initial_diameter_mm` | القطر الابتدائي للقطرة | mm | `Droplet initial diameter; mm` | 262 قيمة (12 فارغ) |
| 12 | `extinction_diameter_mm` | قطر الانطفاء المرئي للهب | mm | `Visible flame extinction diameter; mm` | 197 قيمة (77 فارغ) · **القيمة `0` = لم يُقس (ليست قيمة فيزيائية)** |
| 13 | `burning_rate_mm2_s` | **ثابت معدّل الاحتراق `k`** | **mm²/s** | `Burning rate; mm` | ⚠️ الوحدة mm²/s — انظر الملاحظة أعلاه |
| 14 | `burn_time_s` | زمن الاحتراق | s | `Burn time; s` | 268 قيمة (6 فارغ) · **اختبارا 223/224 تقريبيان (`~6`, `~9`)** |
| 15 | `test_end` | نهاية الاختبار | — | `Test end` | `Extinction` 186 · `Disruption` 61 · `Completion` 27 |
| 16 | `quality_flag` | جودة الصف | — | (مشتق) | `ok` 196 · `missing_extinction_diameter` 61 · `missing_extinction_diameter+missing_burning_rate` 16 · `missing_pressure` 1 |

---

## قواعد التنظيف / Cleaning rules

- **`pressure_atm = pressure_mmHg / 760`** (تحويل وحدة فقط).
- **`burning_rate_mm2_s`** = القيم الأصلية كما هي (الوحدة mm²/s مؤكدة).
- **`quality_flag`**:
  - `ok` افتراضيًا.
  - `missing_pressure` لو `pressure_atm` فارغ أو = `0` (قيمة `0 mmHg` غير فيزيائية — اختبار 114).
  - `missing_extinction_diameter` لو `extinction_diameter_mm` فارغ.
  - `missing_burning_rate` لو `burning_rate_mm2_s` فارغ.
  - لو أكتر من شرط اتحقق → الدمج بعلامة `+`.
  - **لا يُحذف أي صف** — الـ274 صفًا كلها موجودة.
- العلامة `–` (en‑dash) في الملف الخام = قيمة مفقودة → تُكتب كحقل فارغ.
- القيم المُقرَّبة `~6` / `~9` (زمن الاحتراق) حُفظت رقميًا كـ `6` / `9`.
- الخطأ الشائع: قراءة الملف الخام بـ UTF‑8 يفسد محرف `–` (بايت `0x96`) → اقرأ دائمًا بـ **cp1252**.

---

## شواذ معروفة / Known anomalies (من المصدر، لم تُعدَّل)

| Test | flex_id | Issue |
|------|---------|-------|
| 114 | `C11M201` | `pressure_atm = 0` (المصدر `mmHg = 0`) → `quality_flag = missing_pressure` (ضغط غير مُسجَّل) |
| 223 | `H01M104` | زمن احتراق تقريبي `~6` s |
| 224 | `H01H102` | زمن احتراق تقريبي `~9` s |

> **ملاحظة (زمن الاحتراق التقريبي):** الاختباران **223** (`H01M104`) و**224** (`H01H102`) زمن احتراقهما
> مُقرَّب في المصدر (`~6` و `~9` ثانية) وحُفظا رقميًا كـ `6` و `9` — أي لا توجد دقة أعلى من ذلك في المصدر.

> **ملاحظة (`extinction_diameter_mm = 0`):** القيمة `0` تعني **"لم يُقس قطر الانطفاء"** وليست قيمة
> فيزيائية حقيقية (قطر انطفاء صفري غير ممكن). لذلك تُعامل كبيانات غائبة عند التحليل/الرسم
> (يُستخدم فقط الصفوف ذات `extinction_diameter_mm > 0`).

---

## ملاحظات عدد الصفوف / Row-count notes

- الملف الرسمي = **274** صفًا (مُرقَّمة 1–274 بلا فجوات).
- واجهة PSI تعرض **275** (فرق 1).
- تقرير **NASA/TP-2015-216046** يذكر *"first 284 tests"* (يشمل ما قبل/بعد هذه المجموعة).

---

## الاستشهاد / Citation

NASA PSI-69 — *Flame Extinguishment Experiment (FLEX)* · DOI [10.60555/mbq8-0451](https://doi.org/10.60555/mbq8-0451) · License: **CC0‑1.0**.
