import os
import time

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-embedding-001"
DIM = 768
BATCH = 20   
PAUSE = 13   
INDEX = "data/review_index.csv"
VECS = "data/review_vectors.npy"
MAX_PER_RUN = 900  

if os.path.exists(INDEX):
    reviews = pd.read_csv(INDEX)
else:
    frames = []
    for app in ["zomato", "swiggy"]:
        df = pd.read_csv(f"data/{app}_sentiment.csv")
        df["app"] = app
        frames.append(df[["app", "content", "score", "at", "sentiment"]])
    reviews = pd.concat(frames, ignore_index=True)
    reviews["content"] = reviews["content"].fillna("").str.strip().str.slice(0, 1000)
    reviews = reviews[reviews["content"] != ""].copy()
    reviews["words"] = reviews["content"].str.split().str.len()
    reviews = (
        reviews.sort_values("words", ascending=False, kind="mergesort")
        .drop(columns="words")
        .reset_index(drop=True)
    )
    reviews.to_csv(INDEX, index=False)

texts = reviews["content"].tolist()
vectors = list(np.load(VECS)) if os.path.exists(VECS) else []
print(f"{len(texts)} reviews in total, {len(vectors)} already embedded")

config = types.EmbedContentConfig(output_dimensionality=DIM, task_type="RETRIEVAL_DOCUMENT")


def save():
    np.save(VECS, np.array(vectors, dtype="float32"))
    print(f"Saved {len(vectors)} of {len(texts)} reviews")


def embed(batch):
    for _ in range(3):
        try:
            res = client.models.embed_content(model=MODEL, contents=batch, config=config)
        except Exception as err:
            print("  waiting 65 seconds:", str(err)[:200])
            time.sleep(65)
            continue
        vecs = [e.values for e in res.embeddings]
        if len(vecs) != len(batch):
            raise SystemExit(f"Expected {len(batch)} embeddings but got {len(vecs)}.")
        return vecs
    return None


i = len(vectors)
start = i
try:
    while i < len(texts) and i - start < MAX_PER_RUN:
        batch = texts[i : i + BATCH]
        vecs = embed(batch)
        if vecs is None:
            print("Still blocked, probably the daily limit. Run this again later and it will continue.")
            break
        for v in vecs:
            v = np.array(v, dtype="float32")
            vectors.append(v / np.linalg.norm(v))
        i += len(batch)
        print(f"  {i}/{len(texts)}")
        time.sleep(PAUSE)
finally:
    save()