import math
import re
import pandas as pd

ASPECTS = {
    "overall": None,
    "delivery": ["delivery", "deliver", "delivered", "late", "delay", "delayed", "rider", "partner", "slow"],
    "food_quality": ["food", "taste", "cold", "stale", "quality", "packing", "packaging", "missing", "wrong"],
    "support": ["support", "customer care", "customer service", "service", "chat", "agent", "executive", "helpline"],
    "refund_payment": ["refund", "money", "payment", "charged", "wallet", "cancel", "cancelled", "deducted"],
    "pricing_offers": ["price", "prices", "expensive", "fee", "fees", "charges", "offer", "offers", "discount", "coupon", "cashback"],
    "app_bugs": ["bug", "crash", "glitch", "hang", "update", "login", "error", "loading"],
}


def wilson(k, n, z=1.96):
    """95% confidence interval for a percentage."""
    if n == 0:
        return None, None
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return center - margin, center + margin


data = {name: pd.read_csv(f"data/{name}_sentiment.csv") for name in ["zomato", "swiggy"]}

rows = []
for aspect, kws in ASPECTS.items():
    row = {"aspect": aspect}
    ci = {}
    for name, df in data.items():
        if kws is None:
            sub = df
        else:
            pattern = r"\b(?:" + "|".join(re.escape(k) for k in kws) + r")\b"
            text = df["content"].fillna("").str.lower()
            sub = df[text.str.contains(pattern, regex=True)]
        n = len(sub)
        k = int((sub["sentiment"] == "negative").sum())
        ci[name] = wilson(k, n)
        row[f"{name}_n"] = n
        row[f"{name}_neg_pct"] = round(k / n * 100, 1) if n else None

    sw, zo = ci["swiggy"], ci["zomato"]
    if None in sw or None in zo:
        verdict = "not enough data"
    elif sw[0] > zo[1]:
        verdict = "swiggy more negative"
    elif zo[0] > sw[1]:
        verdict = "zomato more negative"
    else:
        verdict = "no clear difference"
    row["verdict"] = verdict
    rows.append(row)

out = pd.DataFrame(rows)
print(out.to_string(index=False))
out.to_csv("data/aspects_summary.csv", index=False)