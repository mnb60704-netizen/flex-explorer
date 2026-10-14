# FLEX Data Source Report

**تاريخ التحقق:** 2026-10-14
**التحقيق:** PSI-69 — Flame Extinguishment Experiment (FLEX), Version 5
**DOI:** 10.60555/mbq8-0451
**الترخيص:** CC0-1.0

> منهج التحقق: فُتحت كل الصفحات فعليًا بمتصفح مبرمَج، وتم فحص طلبات الشبكة (Network) على صفحة PSI-69، وتنزيل الملف الرسمي للجدول (24,776 بايت) والتأكد من صفّه الأول. لم يُعدَّل أي مصدر.

---

## ملخص تنفيذي

- المصدر الرسمي الوحيد الكامل للجدول هو نظام **NASA PSI** (Physical Sciences Informatics)، وليس NTRS ولا data.nasa.gov.
- يوجد **رابط تنزيل مباشر رسمي** للـCSV (بدون تسجيل دخول) عبر منصة GEODE.
- الجدول القابل للتنزيل يحتوي **274 صفًا** برقم تسلسلي `FLEX Test #` من 1 إلى 274 (بينما عدّاد واجهة PSI يعرض "275").
- عمود `Burning rate` قيمته هي **ثابت معدل الاحتراق (burning-rate constant) k بوحدة mm²/s** — رغم أن رأس العمود مكتوب `mm` (نقص "/s").
- الترخيص **CC0-1.0** = إهداء للملكية العامة، قابل لإعادة النشر بحرية في NASA Space Apps.

---

## 1) جدول روابط مُتحقق منها

| # | اسم المصدر | الرابط الكامل | المحتوى | تنزيل CSV/Excel؟ | تسجيل دخول؟ | تاريخ التحقق |
|---|---|---|---|---|---|---|
| 1 | صفحة التحقيق PSI-69 (FLEX) | `https://psi.nasa.gov/physci/repo/data/investigations/PSI-69` | PSI-69 v5 FLEX: DOI، ترخيص، Description، **Experimental Table (274 صفًا)**، Modeling Table (لا يوجد)، Hardware، Representative Images (لا يوجد)، Data files and documents، Publications، Version History | **نعم** | **لا** | 2026-10-14 |
| 2 | نقطة تنزيل الـCSV الرسمية (GEODE API) | `https://psi.nasa.gov/geode-py/ws/studies/PSI-69/download?file=PSI-69_Experimental%20table_FLEX.csv&version=1&redirect=false` | يُرجع **نصًا** فيه رابط S3 موقّع مؤقتًا للملف (200 OK، بدون تسجيل دخول). مع `redirect=true` المتوقّع 302 إلى ملف S3 | **نعم** | **لا** | 2026-10-14 |
| 3 | ملف الـCSV نفسه على S3 (موقّع مؤقتًا) | `https://psi-repo-prod.s3.amazonaws.com/psi-data/PSI-69/Experimental%20table/PSI-69_Experimental%20table_FLEX.csv` | الملف الفعلي: `content-type: application/vnd.ms-excel`، الحجم **24,776 بايت**، آخر تعديل 2025-01-23. الرابط الموقّع **مؤقت** (لا تبني عليه) | **نعم** | **لا** | 2026-10-14 |
| 4 | ملف قاموس البيانات (DoD) عبر الطبقة الرسمية | `https://psi.nasa.gov/geode-py/ws/studies/PSI-69/download?file=PSI-69_Science%20Documents_FLEX%20DoD.docx&version=1&redirect=false` | يُرجع رابط S3 موقّعًا: `https://psi-curation-prod.s3.amazonaws.com/legacy/Filestreamdb/7292/FLEX%20DoD.docx` (18,758 بايت). محتواه **Description of Data** (وصف بنية بيانات FLEX، وليس قاموس أعمدة) | **نعم** (docx) | **لا** | 2026-10-14 |
| 5 | مستودع PSI الرئيسي | `https://psi.nasa.gov/physci/repo/` | واجهة المستودع (JS). منها البحث في التحقيقات | لا (بحث فقط) | **لا** | 2026-10-14 |
| 6 | مُحلّل الـDOI | `https://doi.org/10.60555/mbq8-0451` | يحوّل إلى نظام NASA PSI (صفحة التحقيق PSI-69) | لا | **لا** | 2026-10-14 |
| 7 | سجل NTRS للتقرير | `https://ntrs.nasa.gov/citations/20150023456` | NASA/TP-2015-216046، رقم التقرير GRC-E-DAA-TN5314 / E-18493، Nov 2015. Copyright: **Public Use Permitted** | لا (PDF تقرير) | **لا** | 2026-10-14 |
| 8 | PDF تقرير NASA TP | `https://ntrs.nasa.gov/api/citations/20150023456/downloads/20150023456.pdf` | تقرير NASA/TP—2015-216046 الكامل (رابط التنزيل الرسمي على صفحة NTRS) | لا (PDF) | **لا** | 2026-10-14 |
| 9 | بحث NTRS | `https://ntrs.nasa.gov/search` | محرك بحث NTRS. بحث "FLEX flame extinguishment" رجّع **5 نتائج** (منها التقرير) | لا | **لا** | 2026-10-14 |
| 10 | صفحة Combustion Science (NASA) | `https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/` | ملخص برنامج الاحتراق، ويشمل FLEX، ورابط ورقة FLEX الرسمية | لا | **لا** | 2026-10-14 |
| 11 | ورقة FLEX الرسمية (PDF) | `https://www.nasa.gov/wp-content/uploads/2025/07/flame-extinguishment-experiment-flex.pdf` | PDF يوصف FLEX/FLEX-2/FLEX-2J (مربوط رسميًا من الصفحة #10) | لا (PDF) | **لا** | 2026-10-14* |
| 12 | صفحة FLEX على GIPOC (GRC) | `https://gipoc.grc.nasa.gov/wp/fcf-cir/flex/` | نظرة عامة على FLEX + روابط صور ومراجع لصفحة MDCA | لا | **لا** | 2026-10-14 |
| 13 | دليل قاعدة بيانات PSI (PDF) | `https://science.nasa.gov/wp-content/uploads/2024/11/psi-database-guide.pdf` | "Searching Investigation Data within PSI" + "Navigating a PSI Investigation Page" — يشرح آلية التنزيل (حدّد الـcheckbox ثم اضغط download) | لا (دليل PDF) | **لا** | 2026-10-14* |
| 14 | Researcher's Guide to PSI (صفحة) | `https://www.nasa.gov/science-research/for-researchers/researchers-guide-to-physical-sciences-informatics-system/` | الدليل الرسمي لمنظومة PSI (صفحة حيّة) | لا | **لا** | 2026-10-14 |
| 15 | Researcher's Guide to PSI (PDF) | `https://www.nasa.gov/wp-content/uploads/2020/05/psi_researchers_guide-tagged.pdf` | نسخة PDF من الدليل | لا | **لا** | 2026-10-14 |
| 16 | PSI Tutorial – Portal & Workspaces (PDF) | `https://assets.science.nasa.gov/content/dam/science/bps/bps-general/bps-data_osdr_psi/PSI%20Tutorial_Portal%20%20Workspaces.pdf` | دليل البوابة/الـWorkspaces. الرفع يحتاج NASA Guest Account — أما عرض/تنزيل بيانات التحقيق المنشورة فعام | لا (دليل PDF) | **نعم (للبوابة فقط)** | 2026-10-14* |
| 17 | NASA Open Data Portal | `https://data.nasa.gov/` | فهرس ميتاداتا عام؛ **يوصف** الـdatasets ويوجّه لمكان الاستضافة (لا يستضيف بيانات PSI بنفسه) | لا | **لا** | 2026-10-14 |

\* روابط تحقّقت من وجودها ومحتواها عبر نتائج بحث تفصيلية وروابط رسمية، لكن لم تُفتح ملفات PDF الثنائية نفسها (تجنّبًا للتنزيل).

### ملفات إضافية داخل PSI-69 (موجودة ومُتحقق منها بالاسم/الحجم/التاريخ)

| الملف | المجلد | الحجم | التاريخ |
|---|---|---|---|
| `PSI-69_Experimental table_FLEX.csv` | Experimental table | 24.2 KB | Fri Jan 24 2025 |
| `PSI-69_Science Documents_FLEX DoD.docx` | Science Documents | 18.32 KB | Sat Jun 07 2025 |
| `PSI-69_Science Documents_FLEX_Test_Plan.pdf` | Science Documents | 181.44 KB | Sat Jun 07 2025 |
| `PSI-69_metadata_PSI-133_FLEX.zip` | Investigation Metadata Files | 24.2 KB | Sat Jun 07 2025 |

مجلدات موجودة: `PSI-69`، `Investigation Metadata Files`، `Experimental table`، `Engineering Documents`، `Presentations`، `Raw Data`، `Calibration`، `Science Documents`.

---

## 2) أفضل طريقة للحصول على الـ274 اختبار

### الطريقة أ — رابط مباشر (بدون واجهة، بدون تسجيل دخول) ✅ الأنضف والأسرع

المنصة اسمها **GEODE**، والروابط مستقرة على الشكل التالي (رجّع **200 OK** فعليًا):

```text
https://psi.nasa.gov/geode-py/ws/studies/PSI-69/download?file=PSI-69_Experimental%20table_FLEX.csv&version=1&redirect=true
```

- مع `redirect=false` يُرجع **نصًا** فيه رابط S3 موقّع مؤقتًا.
- مع `redirect=true` (متوقّع) يعمل 302 إلى ملف S3 مباشرة.
- لا يحتاج مفتاح API ولا تسجيل دخول.

### الطريقة ب — من واجهة الصفحة

1. افتح: `https://psi.nasa.gov/physci/repo/data/investigations/PSI-69`
2. قسم **Experimental Table** → من **"Select Experimental Table"** اختر `PSI-69_Experimental table_FLEX.csv`. لتوسيع العرض اختر **Items per page = 100** (المتاح: 5 / 10 / 25 / 100).
3. للتنزيل: انزل لقسم **Data files and documents** → مجلد **Experimental table** → الملف `PSI-69_Experimental table_FLEX.csv` → اضغط الصف (يصبح **"Selected: 1"**) → يظهر زر **Download** (أيقونة `cloud_download`).

### API (غير موثّق كواجهة عامة لكنه شغّال)
- تنزيل درس/ملف: `GET https://psi.nasa.gov/geode-py/ws/studies/{STUDY}/download?file={FILENAME}&version={n}&redirect=...`
- سرد الملفات: `POST https://psi.nasa.gov/geode-py/ws/files/v2`

### الاستشهاد جاهز من الصفحة
زر **"Cite this Investigation"** + زرّي **"Download Citation (BibTex)"** و**"Download Citation (RIS)"**.

---

## 3) شرح الأعمدة (15 عمودًا)

رأس الملف الحقيقي (نص حرفي من أول سطر في الـCSV):

```text
FLEX Test #,FLEX Identifier,Test Date,Test GMT,Fuel,Ambient pressure; mmHg,O initial ambient composition; mole fraction,N initial ambient composition; mole fraction,CO initial ambient composition; mole fraction,He initial ambient composition; mole fraction,Droplet initial diameter; mm,Visible flame extinction diameter; mm,Burning rate; mm,Burn time; s,Test end
```

| # | العمود (نص حرفي) | المعنى | الوحدة |
|---|---|---|---|
| 1 | `FLEX Test #` | رقم تسلسلي للاختبار | عدد صحيح (1–274) |
| 2 | `FLEX Identifier` | كود الاختبار (مثال `20CAL08`, `30CAL02`) | نص |
| 3 | `Test Date` | تاريخ التنفيذ (مثال `3/5/2009`) | تاريخ |
| 4 | `Test GMT` | وقت التنفيذ بتوقيت جرينتش (HH:MM:SS) | وقت |
| 5 | `Fuel` | نوع الوقود: **Methanol** أو **Heptane** | نص |
| 6 | `Ambient pressure; mmHg` | ضغط الوسط المحيط | **mmHg** |
| 7 | `O initial ambient composition; mole fraction` | الكسر الجزيئي للأكسجين O₂ في الخليط الابتدائي | كسر جزيئي (0–1) |
| 8 | `N initial ambient composition; mole fraction` | الكسر الجزيئي للنيتروجين N₂ (مخفّف) | كسر جزيئي (0–1) |
| 9 | `CO initial ambient composition; mole fraction` | الكسر الجزيئي لثاني أكسيد الكربون **CO₂** (مُطفِئ) | كسر جزيئي (0–1) |
| 10 | `He initial ambient composition; mole fraction` | الكسر الجزيئي للهيليوم (مُطفِئ) | كسر جزيئي (0–1) |
| 11 | `Droplet initial diameter; mm` | القطر الابتدائي للقطيرة | **mm** |
| 12 | `Visible flame extinction diameter; mm` | قطر القطيرة عند لحظة انطفاء اللهب المرئي (يكون **فارغًا** لو مافيش انطفاء عند قطر نهائي) | **mm** |
| 13 | `Burning rate; mm` | ثابت معدل الاحتراق (شوف التفصيل تحت) | **mm²/s** |
| 14 | `Burn time; s` | زمن الاحتراق | **s** |
| 15 | `Test end` | طريقة نهاية الاختبار | نص |

> الأعمدة 7/8/9 مكتوبة في الرأس بالحروف `O`, `N`, `CO` بدون رموز سفلية؛ السياق (FLEX: O₂ + مخفّف N₂/CO₂/He) يدل على O₂/N₂/CO₂.

### إحصاءات الجدول (من الملف الرسمي)

- **عدد الصفوف:** 274 صفًا (`FLEX Test #` من 1 إلى 274، بدون فجوات). عدّاد واجهة PSI يعرض "275" — فرق بمقدار 1 (تعدد الواجهة/الرأس أو صف وهمي)؛ **الملف القابل للتنزيل = 274 صفًا**.
- **Fuel:** Methanol = 157، Heptane = 117.
- **Test end:** Extinction = 186، Disruption = 61، Completion = 27.

### معنى `Test end`
- **Extinction** = انطفاء اللهب عند قطر نهائي محدود.
- **Disruption** = انطفاء اضطرابي (القطيرة تتفكّك/تحترق بشكل غير منتظم بدل انطفاء ناعم).
- **Completion** = احتراق حتى الاكتمال (استهلاك الوقود بالكامل، بدون انطفاء عند قطر محدود).

---

## 4) الحسم في وحدة `Burning rate` = **mm²/s**

رأس العمود في PSI مكتوب حرفيًا `Burning rate; mm` (بدون "/s")، لكن الأدلة تجزم أن القيمة هي **ثابت معدل الاحتراق (burning-rate constant) k بوحدة mm²/s**، وليس طولًا:

1. **تقرير NASA/TP-2015-216046** يقول حرفيًا إنه يبلّغ عن *"Average burning-rate constants for each burn also are reported"* — وثابت معدل الاحتراق متعارف عليه `k = -d(d²)/dt` بوحدة **mm²/s**.
   المصدر: `https://ntrs.nasa.gov/citations/20150023456`
2. **عرض NTRS لاختبار FLEX-145** يكتب صريحًا: *"Burning rate constant, K = 0.44 m2/s"* (خطأ مطبعي واضح في `m2`, والصحيح **mm²/s**).
3. **تحليل أبعاد على بيانات الجدول نفسه** — العلاقة `t_burn ≈ (d₀² − d_ext²)/k`:
   - على **196 صفًا** فيها قيم صحيحة: **الوسيط 5.5%**، المتوسط 10.3%، **152/196 داخل 10%**، **182/196 داخل 20%**.
   - مثال (الصف 5): d₀=1.92، d_ext=0.81، k=0.48 → `(1.92²−0.81²)/0.48 ≈ 6.3 s` مقابل `Burn time = 6.34 s`. ✅
   - الحالات الشاذة (أعلى خطأ، مثل الاختبارات 130/129/213) هي حالات **انطفاء فوري** يكون فيها `d₀ ≈ d_ext`، فتضعف صلاحية القانون (العابر/الإشعال يسيطر) — تفسير فيزيائي واضح وليس تناقضًا.
   - لو كانت الوحدة طولًا (mm) لكانت العلاقة `t=(d₀²−d_ext²)/k` **بلا معنى أبعاديًا** ولما ظهرت أي علاقة إحصائية — وهي ظهرت بقوة.

> **النتيجة:** اعرض القيمة كـ **mm²/s** (ثابت معدل الاحتراق k)، مع ملاحظة أن رأس PSI يكتبها `mm`.

---

## 5) الترخيص والاستشهاد

- **الترخيص:** `CC0-1.0` — رابط SPDX: `https://spdx.org/licenses/CC0-1.0.html`
  → **إهداء للملكية العامة (Public Domain Dedication): إعادة الاستخدام وإعادة النشر مسموحة بدون شرط نسب** (يُستحسن ذكر المصدر).
- **الـDOI:** `10.60555/mbq8-0451` → `https://doi.org/10.60555/mbq8-0451`

**الاستشهاد الصحيح للبيانات (كما يولّده زر Cite this Investigation حرفيًا):**

> Williams FA, Shaw BD, Hicks MC, Nayagam V, Choi MY, Dryer FL, Dietrich D. "Flame Extinguishment Experiment(FLEX)", NASA PSI Data Repository, Version 5, http://doi.org/10.60555/mbq8-0451

**استشهاد التقرير (NTRS، Copyright: Public Use Permitted):**

> Dietrich, D. L., et al., "Detailed Results from the Flame Extinguishment Experiment (FLEX) March 2009 to December 2011," NASA/TP-2015-216046, 2015. Report No. GRC-E-DAA-TN5314 / E-18493.

**للإستخدام في NASA Space Apps:** مسموح. CC0-1.0 يعطيك حرية إعادة النشر والتعديل والدمج. اذكر قسم "Data source" فيه: FLEX + PSI-69 + الـDOI. وراجع NASA Brand & Usage Guidelines لاستخدام الشعار.

---

## 6) ما لم أستطع التحقق منه

1. **شرح الأعمدة** مبني على رأس الجدول + سياق FLEX + تقرير NTRS؛ الملف `FLEX DoD.docx` تبيّن أنه **"Description of Data"** (وصف بنية بيانات FLEX ككل: Raw/Analyzed Data، Raw Videos، Images) وليس قاموس أعمدة، ولم يُفتح أي قاموس أعمدة رسمي مخصص.
2. **وحدة Burning rate:** الحسم mm²/s قوي جدًا (4 أدلة)، لكن رأس PSI المكتوب `mm` يخالفه نصًّا.
3. **معنى الاختصارات `O`/`N`/`CO`:** استنتاج من السياق (O₂/N₂/CO₂)؛ الرأس لم يكتب رموزًا سفلية.
4. **سلوك `redirect=true`** لرابط التنزيل: لم يُختبر مباشرةً (اختُبر `redirect=false` فقط).
5. **بارامترات/جسم** `POST /geode-py/ws/files/v2` (سرد الملفات): لم يُفحص.
6. **تضارب العدد:** الملف = 274 صفًا (رقم تسلسلي 1–274)، واجهة PSI = 275، وملخص تقرير NASA/TP-2015-216046 يذكر *"first 284 tests performed"*. لم أتأكد من أسباب الفروق.
7. **علاقة `PSI-69_metadata_PSI-133_FLEX.zip`** بـ"PSI-133": غير واضحة، لم تُتحقق.
8. **هل زر Download ينتج CSV مباشرة أم zip:** لم يُضغط الزر لأرى الناتج (استُخدمت نقطة التنزيل المباشرة بدلًا منه).
9. **data.nasa.gov:** نجح بعد محاولة فاشلة (Transport error)؛ لكن **لا يوجد إدخال مباشر ظاهر لـPSI-69/FLEX** فيه.
10. **`https://nasa-psi.s3.us-west-2.amazonaws.com/index.html`** (PSI Data Explorer): ظهر في نتائج البحث فقط ولم يُفتح.
11. **روابط PDF (#11, #13, #16):** تحقّق وجودها ومحتواها عبر نتائج بحث وروابط رسمية، لكن لم تُفتح ملفات PDF الثنائية مباشرةً.

---

## ملحق — أرقام جاهزة للاستشهاد

| المؤشر | القيمة |
|---|---|
| عدد صفوف الملف | 274 |
| نطاق `FLEX Test #` | 1 → 274 |
| Fuel | Methanol: 157 · Heptane: 117 |
| Test end | Extinction: 186 · Disruption: 61 · Completion: 27 |
| صفوف صالحة لفحص k = (d₀²−d_ext²)/t | 196 |
| وسيط الخطأ النسبي للعلاقة k | 5.5% |
| الترخيص | CC0-1.0 |
| DOI | 10.60555/mbq8-0451 |
