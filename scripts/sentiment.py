import pandas as pd
from transformers import pipeline

clf = pipeline(
    "text-classification",
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    truncation=True,
    max_length=128,
)

for name in ["zomato", "swiggy"]:
    df = pd.read_csv(f"data/{name}_clean.csv")
    df = df[df["has_text"]].copy()

    results = clf(df["content"].tolist(), batch_size=32)
    df["sentiment"] = [r["label"].lower() for r in results]
    df["confidence"] = [r["score"] for r in results]

    df.to_csv(f"data/{name}_sentiment.csv", index=False)
    print(name.upper())
    print((df["sentiment"].value_counts(normalize=True) * 100).round(1))
    print()