import re
from collections import Counter
import pandas as pd

STOP = set("""the a an and or but is are was were it its i my me you your to of in on for with this that
not no so very too just have has had be been at as by from app they them we our get got can will would
do does did if all there when what which hai hain ka ki ke se ko ne bhi bahut aur hi nahi""".split())

for name in ["zomato", "swiggy"]:
    df = pd.read_csv(f"data/{name}_sentiment.csv")
    print("=" * 50)
    print(name.upper(), "-", len(df), "reviews with text")

    print("\nSentiment (%):")
    print((df["sentiment"].value_counts(normalize=True) * 100).round(1))

    print("\nAverage stars by predicted sentiment:")
    print(df.groupby("sentiment")["score"].mean().round(2))

    # reviews where model and stars disagree
    clash = df[((df["sentiment"] == "positive") & (df["score"] <= 2)) |
               ((df["sentiment"] == "negative") & (df["score"] >= 4))]
    print("\nModel and stars disagree:", round(len(clash) / len(df) * 100, 1), "%")

    # most common words in negative reviews
    neg = df[df["sentiment"] == "negative"]["content"].str.lower()
    words = Counter(
        w for text in neg for w in re.findall(r"[a-z]{3,}", text) if w not in STOP
    )
    print("\nTop words in negative reviews:")
    print(words.most_common(15))