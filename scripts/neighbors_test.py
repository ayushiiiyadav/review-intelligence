import sys

import numpy as np
import pandas as pd

vectors = np.load("data/review_vectors.npy")
reviews = pd.read_csv("data/review_index.csv").iloc[: len(vectors)]

i = int(sys.argv[1]) if len(sys.argv) > 1 else 0
scores = vectors @ vectors[i]
top = np.argsort(-scores)[:6]

print("Review", i, ":", reviews.iloc[i]["content"][:250], "\n")
print("Most similar reviews:\n")
for j in top[1:]:
    r = reviews.iloc[j]
    print(f"[{r['app']} | {r['score']} stars | similarity {scores[j]:.2f}] {r['content'][:220]}\n")