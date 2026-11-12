import re
import pandas as pd

M = 50  # prior weight: how many "imaginary" average reviews are added

ASPECTS = {
    "delivery": ["delivery", "deliver", "delivered", "late", "delay", "delayed", "rider", "partner", "slow"],
    "food_quality": ["food", "taste", "cold", "stale", "quality", "packing", "packaging", "missing", "wrong"],
    "support": ["support", "customer care", "customer service", "service", "chat", "agent", "executive", "helpline"],
    "refund_payment": ["refund", "money", "payment", "charged", "wallet", "cancel", "cancelled", "deducted"],
    "pricing_offers": ["price", "prices", "expensive", "fee", "fees", "charges", "offer", "offers", "discount", "coupon", "cashback"],
    "app_bugs": ["bug", "crash", "glitch", "hang", "update", "login", "error", "loading"],
}


def bayes(avg, n, prior, m=M):
    return (n * avg + m * prior) / (n + m)


apps = ["zomato", "swiggy"]
clean = {a: pd.read_csv(f"data/{a}_clean.csv") for a in apps}
sent = {a: pd.read_csv(f"data/{a}_sentiment.csv") for a in apps}

C = pd.concat(clean.values())["score"].mean()
print("Global average stars:", round(C, 2))

print("\nOVERALL (all reviews in the shared time window)")
for a, df in clean.items():
    n, avg = len(df), df["score"].mean()
    print(f"{a}: raw {avg:.2f} from {n} reviews -> adjusted {bayes(avg, n, C):.2f}")

print("\nBY ASPECT (star ratings of text reviews that mention each topic)")
rows = []
for aspect, kws in ASPECTS.items():
    pattern = r"\b(?:" + "|".join(re.escape(k) for k in kws) + r")\b"
    row = {"aspect": aspect}
    for a, df in sent.items():
        text = df["content"].fillna("").str.lower()
        sub = df[text.str.contains(pattern, regex=True)]
        n = len(sub)
        row[f"{a}_n"] = n
        if n:
            row[f"{a}_stars"] = round(bayes(sub["score"].mean(), n, df["score"].mean()), 2)
        else:
            row[f"{a}_stars"] = None
    rows.append(row)

out = pd.DataFrame(rows)
print(out.to_string(index=False))
out.to_csv("data/ranking_summary.csv", index=False)

print("\nWhy this matters:")
for label, avg, n in [("App A", 4.8, 20), ("App B", 4.7, 50000)]:
    print(label, "raw", avg, "with", n, "reviews -> adjusted", round(bayes(avg, n, 4.0, m=100), 2))