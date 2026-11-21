import os
import sys

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-embedding-001"
vectors = np.load("data/review_vectors.npy")
reviews = pd.read_csv("data/review_index.csv")

question = " ".join(sys.argv[1:]) or "Why are people angry about refunds?"
res = client.models.embed_content(
    model=MODEL,
    contents=question,
    config=types.EmbedContentConfig(output_dimensionality=768, task_type="RETRIEVAL_QUERY"),
)
q = np.array(res.embeddings[0].values, dtype="float32")
q /= np.linalg.norm(q)

scores = vectors @ q
top = np.argsort(-scores)[:6]
print("\nQuestion:", question, "\n")
for i in top:
    r = reviews.iloc[i]
    print(f"[{r['app']} | {r['score']} stars | match {scores[i]:.2f}] {r['content'][:220]}\n")