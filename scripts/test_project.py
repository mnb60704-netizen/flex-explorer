"""Verification suite for the FLEX Explorer project.

Run from the project root (or anywhere):

    python scripts/test_project.py

What it checks (no network, no writes — the training loops are re-run in memory
only and compared against the stored reports):

1. Data integrity
   - data/flex_data.csv   matches the sha256 recorded in data/provenance.csv
   - data/flex_clean.csv  matches the sha256 documented in index.html / README
   - shape 274 x 16 and the headline distributions (fuel / outcome / diluent)
2. Regression reproducibility
   - re-running the GroupKFold(5) OOF loop of scripts/train_regression.py
     reproduces reports/regression_metrics.json (tol 1e-9)
3. Classification reproducibility
   - same for scripts/train_classification.py vs reports/classification_metrics.json
4. Report artifacts
   - reports/feature_importance.json is complete, ranked, and internally consistent
   - reports/figures/*.png exist (they are rendered in the ML section)
5. Site contract (index.html)
   - single-file, CDN-only (chart.js + papaparse), no API keys / no remote data calls
   - every asset it fetches (CSV, JSON, PNG) exists in the repo
   - the honesty strings are present (DOI, space-vs-ground caveat, model limits)
"""
import hashlib
import json
import os
import re
import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJ, "scripts"))

import train_classification as tcl  # noqa: E402
import train_regression as tr  # noqa: E402

CLEAN_SHA = "16f300da016b0d06c6e4a579008b1307799663ec7192cdd1f352d15818d431e2"
TOL = 1e-9

FAILURES = []


def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {name}" + (f"  -> {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(f"{name}: {detail}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(rel):
    with open(os.path.join(PROJ, rel), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- 1. data ----
def test_data_integrity():
    print("\n== 1. data integrity ==")

    prov = pd.read_csv(os.path.join(PROJ, "data", "provenance.csv")).iloc[0]
    raw = os.path.join(PROJ, "data", prov["file"])
    check("raw sha256 == provenance.csv", sha256(raw) == prov["sha256"], sha256(raw))

    clean_path = os.path.join(PROJ, "data", "flex_clean.csv")
    clean_sha = sha256(clean_path)
    check("clean sha256 == documented", clean_sha == CLEAN_SHA, clean_sha)
    index_html = open(os.path.join(PROJ, "index.html"), encoding="utf-8").read()
    check("index.html quotes the clean sha256", CLEAN_SHA in index_html)

    df = pd.read_csv(clean_path)
    check("shape == (274, 16)", df.shape == (274, 16), str(df.shape))

    fuels = df["fuel"].value_counts().to_dict()
    check("fuel counts", fuels == {"Methanol": 157, "Heptane": 117}, str(fuels))

    ends = df["test_end"].value_counts().to_dict()
    check(
        "test_end counts",
        ends == {"Extinction": 186, "Disruption": 61, "Completion": 27},
        str(ends),
    )

    dil = np.where(df["x_co2"] > 0, "CO2", np.where(df["x_he"] > 0, "He", "N2"))
    counts = {k: int((dil == k).sum()) for k in ("N2", "CO2", "He")}
    check("derived diluent counts", counts == {"N2": 101, "CO2": 123, "He": 50}, str(counts))

    zero_p = df.loc[df["pressure_atm"] == 0, "test_id"].tolist()
    check("exactly one row with pressure_atm == 0 (test 114)", zero_p == [114], str(zero_p))

    check("missing burning_rate_mm2_s == 16", int(df["burning_rate_mm2_s"].isna().sum()) == 16)
    check(
        "missing extinction_diameter_mm == 77",
        int(df["extinction_diameter_mm"].isna().sum()) == 77,
    )


# ------------------------------------------------------- 2. reproducibility ---
def _oof_regression():
    df, n_total = tr.load()
    y = df["y"].to_numpy(dtype=float)
    X = tr.build_X(df)
    groups = df["campaign_id"].to_numpy()
    gkf = GroupKFold(n_splits=tr.N_SPLITS)
    out = {}
    for name, factory in tr.SPECS.items():
        oof = np.full(len(df), np.nan)
        for itr, ite in gkf.split(X, y, groups):
            Xtr, Xte = tr.impute(X.iloc[itr], X.iloc[ite])
            oof[ite] = factory().fit(Xtr, y[itr]).predict(Xte)
        out[name] = tr.metrics(y, oof)
    meta = {
        "n_total_rows": n_total,
        "n_rows_used": int(len(df)),
        "n_campaigns": int(df["campaign_id"].nunique()),
    }
    return out, meta


def test_regression_reproducible():
    print("\n== 2. regression metrics reproduce reports/regression_metrics.json ==")
    stored = read_json("reports/regression_metrics.json")
    got, meta = _oof_regression()

    check("n_rows_used", stored["n_rows_used"] == meta["n_rows_used"] == 258,
          f"stored={stored['n_rows_used']} recomputed={meta['n_rows_used']}")
    check("n_campaigns", stored["n_campaigns"] == meta["n_campaigns"] == 78,
          f"stored={stored['n_campaigns']} recomputed={meta['n_campaigns']}")
    check("random_state == 42", stored["random_state"] == 42)
    check("cv string", stored["cv"] == "GroupKFold(5) on campaign_id", stored["cv"])

    for name in tr.SPECS:
        for key in ("mae", "rmse", "r2"):
            a, b = stored["models"][name]["oof"][key], got[name][key]
            check(f"{name}.{key} within {TOL}", abs(a - b) <= TOL, f"stored={a} recomputed={b}")

    check("selected_model == random_forest", stored["selected_model"] == "random_forest",
          stored["selected_model"])
    base = stored["models"]["baseline_fuel_mean"]["oof"]["mae"]
    best = stored["models"]["random_forest"]["oof"]["mae"]
    check("RF beats the baseline by >40%", (base - best) / base > 0.40,
          f"gain={(base - best) / base * 100:.1f}%")


def _oof_classification():
    df, n_total = tcl.load_cls()
    y = df["yc"].to_numpy()
    X = tr.build_X(df)
    groups = df["campaign_id"].to_numpy()
    labels = sorted(np.unique(y))
    gkf = GroupKFold(n_splits=tr.N_SPLITS)
    out = {}
    for name, factory in tcl.SPECS.items():
        oof = np.full(len(df), "", dtype=object)
        for itr, ite in gkf.split(X, y, groups):
            Xtr, Xte = tr.impute(X.iloc[itr], X.iloc[ite])
            oof[ite] = factory().fit(Xtr, y[itr]).predict(Xte)
        out[name] = tcl.metrics(y, oof, labels)
    return out, {"n_total_rows": n_total, "n_rows_used": int(len(df)),
                 "n_campaigns": int(df["campaign_id"].nunique())}


def test_classification_reproducible():
    print("\n== 3. classification metrics reproduce reports/classification_metrics.json ==")
    stored = read_json("reports/classification_metrics.json")
    got, meta = _oof_classification()

    check("n_rows_used == 274", stored["n_rows_used"] == meta["n_rows_used"] == 274,
          f"stored={stored['n_rows_used']} recomputed={meta['n_rows_used']}")
    check("n_campaigns == 81", stored["n_campaigns"] == meta["n_campaigns"] == 81,
          f"stored={stored['n_campaigns']} recomputed={meta['n_campaigns']}")
    check("random_state == 42", stored["random_state"] == 42)
    check("class_support", stored["class_support"] ==
          {"Extinction": 186, "Disruption": 61, "Completion": 27}, str(stored["class_support"]))

    for name in tcl.SPECS:
        for key in ("balanced_accuracy", "macro_f1"):
            a, b = stored["models"][name]["oof"][key], got[name][key]
            check(f"{name}.{key} within {TOL}", abs(a - b) <= TOL, f"stored={a} recomputed={b}")
        a, b = stored["models"][name]["oof"]["confusion_matrix"], got[name]["confusion_matrix"]
        check(f"{name}.confusion_matrix identical", a == b, f"stored={a} recomputed={b}")

    check("selected_model == logistic_regression",
          stored["selected_model"] == "logistic_regression", stored["selected_model"])
    base = stored["models"]["baseline_most_frequent"]["oof"]["balanced_accuracy"]
    best = stored["models"]["logistic_regression"]["oof"]["balanced_accuracy"]
    check("logreg beats the baseline by >50%", (best - base) / base > 0.50,
          f"gain={(best - base) / base * 100:.1f}%")


# ----------------------------------------------------------- 4. artifacts ----
def test_reports():
    print("\n== 4. report artifacts ==")
    fi = read_json("reports/feature_importance.json")
    feats = fi["features"]
    check("7 ranked features", len(feats) == 7 and [f["rank"] for f in feats] == list(range(1, 8)))
    check("top feature is x_o2", feats[0]["feature"] == "x_o2", feats[0]["feature"])
    check("gini values positive", all(f["gini"] > 0 for f in feats))
    check("gini sums to ~1", abs(sum(f["gini"] for f in feats) - 1) < 0.02,
          f"sum={sum(f['gini'] for f in feats):.4f}")
    check("gini is non-increasing", all(feats[i]["gini"] >= feats[i + 1]["gini"]
                                        for i in range(len(feats) - 1)))
    check("feature list matches regression features",
          {f["feature"] for f in feats} ==
          set(read_json("reports/regression_metrics.json")["features"]))

    for png in ("feature_importance.png", "actual_vs_predicted.png", "residuals_vs_predicted.png"):
        p = os.path.join(PROJ, "reports", "figures", png)
        check(f"reports/figures/{png} exists", os.path.isfile(p) and os.path.getsize(p) > 5000,
              f"{os.path.getsize(p) if os.path.isfile(p) else 'missing'} bytes")

    for rel in ("reports/regression_report.md", "reports/classification_report.md",
                "data/model_ready/flex_train.csv", "data/model_ready/flex_targets.csv"):
        check(f"{rel} exists", os.path.isfile(os.path.join(PROJ, rel)))


# ---------------------------------------------------------------- 5. site ----
def test_site():
    print("\n== 5. site contract (index.html) ==")
    html_path = os.path.join(PROJ, "index.html")
    html = open(html_path, encoding="utf-8").read()

    check("no remote data/API calls",
          not re.search(r"fetch\(\s*['\"]https?://|Bearer\s+[A-Za-z0-9]|sk-[A-Za-z0-9]{8,}"
                        r"|api[_-]?key\s*[:=]\s*['\"]|openai|anthropic", html, re.I))
    hosts = set(re.findall(r'<script[^>]+src="https://([^/"]+)', html)) | \
            set(re.findall(r'<link[^>]+href="https://([^/"]+)', html))
    check("CDN-only script/link hosts", hosts == {"cdn.jsdelivr.net"}, str(hosts))

    for rel in set(re.findall(r'fetch\("([^"]+)"\)', html)):
        check(f"asset exists: {rel}", os.path.isfile(os.path.join(PROJ, rel)))
    for rel in set(re.findall(r'<img[^>]+src="([^"]+)"', html)):
        check(f"asset exists: {rel}", os.path.isfile(os.path.join(PROJ, rel)))
    check("loads data/flex_clean.csv", "data/flex_clean.csv" in html)
    check("canvas per chart", all(c in html for c in
          ('id="c-d2"', 'id="c-k"', 'id="c-scatter"', 'id="c-outcome"', 'id="c-compare"')))

    check("DOI present", "10.60555/mbq8-0451" in html)
    check("source URL present", "psi.nasa.gov/physci/repo/data/investigations/PSI-69" in html)
    check("raw sha256 present", "37c88ce8ae9391b7544ff630a45ce87543d04d317cdbfbed104fe7d5c27e1b96" in html)
    check("CC0 license present", "CC0" in html)
    check("space-vs-ground caveat present",
          re.search(r"لا يميّز أي سجل أُجري في الفضاء", html) is not None and
          re.search(r"لا\s*[^<]{0,40}(يصف|نصف) أي (صف|سجل) بأنه تجربة", html) is not None)
    check("no-fire-prediction disclaimer present",
          "لا يستطيع التنبؤ بحريق داخل مركبة" in html)
    check("campaign split documented", "GroupKFold" in html and "campaign_id" in html)
    check("leakage guards documented",
          "burn_time_s" in html and "extinction_diameter_mm" in html)
    check("limits ranges documented", "0.12–0.34" in html and "0.5–3.1" in html)
    check("missing-value counts documented", "16" in html and "77" in html)
    check("intro / 30-second section", "in 30 seconds" in html)
    check("QA assistant is deterministic (no LLM call)",
          "ليس نموذجًا لغويًا" in html)
    check("no per-row space-experiment claim in code",
          not re.search(r"isSpace|space_experiment|in_space", html))


def main():
    print("FLEX Explorer — verification suite")
    test_data_integrity()
    test_regression_reproducible()
    test_classification_reproducible()
    test_reports()
    test_site()

    print("\n" + "=" * 70)
    if FAILURES:
        print(f"{len(FAILURES)} check(s) FAILED:")
        for f in FAILURES:
            print("  - " + f)
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
