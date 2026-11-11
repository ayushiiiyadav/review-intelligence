import pandas as pd

dfs = {}
for name in ["zomato", "swiggy"]:
    df = pd.read_csv(f"data/{name}_reviews.csv", parse_dates=["at"])
    df["content"] = df["content"].fillna("").str.strip()
    df["word_count"] = df["content"].str.split().str.len()
    dfs[name] = df

# use the same time window for both apps
start = max(df["at"].min() for df in dfs.values())
end = min(df["at"].max() for df in dfs.values())
print("Common window:", start, "to", end)

for name, df in dfs.items():
    df = df[(df["at"] >= start) & (df["at"] <= end)]
    df["has_text"] = df["word_count"] >= 5   # long enough for text analysis
    df.to_csv(f"data/{name}_clean.csv", index=False)
    print(name, "total:", len(df), "| usable for text analysis:", df["has_text"].sum())