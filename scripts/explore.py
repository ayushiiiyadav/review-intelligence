import pandas as pd

for name in ["zomato", "swiggy"]:
    df = pd.read_csv(f"data/{name}_reviews.csv")
    print("=" * 50)
    print(name.upper())
    print("Rows:", len(df))
    print("Date range:", df["at"].min(), "to", df["at"].max())
    print("\nStar rating spread (%):")
    print((df["score"].value_counts(normalize=True).sort_index() * 100).round(1))
    print("\nAverage rating:", round(df["score"].mean(), 2))
    print("\nEmpty reviews:", df["content"].isna().sum())
    print("\n5 random reviews:")
    for text in df["content"].dropna().sample(5, random_state=1):
        print("-", text[:200])