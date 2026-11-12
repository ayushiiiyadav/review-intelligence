import re
import pandas as pd

ASPECTS = {
    "delivery": ["delivery", "deliver", "delivered", "late", "delay", "delayed", "rider", "partner", "slow"],
    "food_quality": ["food", "taste", "cold", "stale", "quality", "packing", "packaging", "missing", "wrong"],
    "support": ["support", "customer care", "customer service", "service", "chat", "agent", "executive", "helpline"],
    "refund_payment": ["refund", "money", "payment", "charged", "wallet", "cancel", "cancelled", "deducted"],
    "pricing_offers": ["price", "prices", "expensive", "fee", "fees", "charges", "offer", "offers", "discount", "coupon", "cashback"],
    "app_bugs": ["bug", "crash", "glitch", "hang", "update", "login", "error", "loading"],
}

rows = []
for name in ["zomato", "swiggy"]:
    df = pd.read_csv(f"data/{name}_sentiment.csv")
    text = df["content"].fillna("").str.lower()
    for aspect, kws in ASPECTS.items():
        pattern = r"\b(" + "|".join(re.escape(k) for k in kws) + r")\b"
        mask = text.str.contains(pattern, regex=True)
        sub = df[mask]
        rows.append({
            "app": name,
            "aspect": aspect,
            "pct_of_reviews": round(mask.mean() * 100, 1),
            "pct_negative": round((sub["sentiment"] == "negative").mean() * 100, 1) if len(sub) else None,
        })

out = pd.DataFrame(rows)
print(out.pivot(index="aspect", columns="app", values=["pct_of_reviews", "pct_negative"]))
out.to_csv("data/aspects_summary.csv", index=False)