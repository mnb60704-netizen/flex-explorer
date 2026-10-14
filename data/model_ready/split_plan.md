# FLEX — Split Plan (for future training)

**Goal:** define *now* how the data will be split later, so evaluation stays honest.
**Status:** plan only — **no training is run.**

---

## Splitting strategy

- **Method:** `GroupKFold(n_splits=5)` on **`campaign_id`**.
- **Grouping unit:** a whole *campaign* (a batch of tests from the same run/conditions)
  must stay in a single fold — never split its rows across train/test.
- **No random splitting at the row level** (avoids leakage between near-identical tests).
- **`random_state = 42`** wherever a seed is needed.

## Deriving `campaign_id`

`campaign_id` is **not** in the files; it is derived at training time. Two equivalent options:

1. **From `test_date`** → use year/month (e.g. `2010-09`) or just the year (`2010`).
   - `test_date` is `M/D/YYYY` in the raw source (e.g. `9/6/2010`).
2. **From the `flex_id` prefix** → take the leading campaign code.
   - e.g. `20CAL08` → `20CAL`, `H19H101` → `H19`, `C08H301` → `C08`.

> Choose **one** derivation and document it. Prefer the `flex_id` prefix when available
> (it encodes the test campaign directly); fall back to `test_date` otherwise.

## Why group by campaign (not by row)

Tests inside one campaign share the same fuel, pressure, and ambient composition.
A random row-level split would put siblings in both train and test → optimistic scores.
Grouping keeps every campaign intact on one side of the split.

## Illustrative sketch (NOT executed)

```python
# plan only — do not run yet
import pandas as pd
from sklearn.model_selection import GroupKFold

train = pd.read_csv("data/model_ready/flex_train.csv")
tgt   = pd.read_csv("data/model_ready/flex_targets.csv")

# campaign_id from the flex_id prefix (fallback: test_date month)
campaign = train["flex_id"].str.extract(r"^([A-Za-z0-9]+?)(?=\d{2,}$)", expand=False)

gkf = GroupKFold(n_splits=5)
for fold, (tr, te) in enumerate(gkf.split(train, groups=campaign)):
    ...  # train on tr, evaluate on te
```

## Reminders

- Keep targets **separate**: merge `flex_targets.csv` back by `test_id` inside the split.
- Decide per target whether to filter (`quality_flag`, `extinction_diameter_mm = 0`) — filter
  **after** splitting to preserve the group structure, and document the rule.
