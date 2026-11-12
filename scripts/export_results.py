import json
import os
import pandas as pd

apps = ["zomato", "swiggy"]
clean = {a: pd.read_csv(f"data/{a}_clean.csv", parse_dates=["at"]) for a in apps}

overall = {
    a: {"reviews": int(len(df)), "avg_stars": round(float(df["score"].mean()), 2)}
    for a, df in clean.items()
}
start = max(df["at"].min() for df in clean.values())
end = min(df["at"].max() for df in clean.values())

aspects = pd.read_csv("data/aspects_summary.csv")
ranking = pd.read_csv("data/ranking_summary.csv").drop(columns=["zomato_n", "swiggy_n"])
merged = aspects.merge(ranking, on="aspect", how="left")

result = {
    "window": f"{start.date()} to {end.date()}",
    "overall": overall,
    "aspects": json.loads(merged.to_json(orient="records")),
}

os.makedirs("backend", exist_ok=True)
with open("backend/results.json", "w") as f:
    json.dump(result, f, indent=2)
print("Saved backend/results.json")