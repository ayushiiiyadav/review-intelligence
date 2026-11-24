import os

import numpy as np
import pandas as pd
import psycopg
from dotenv import load_dotenv

load_dotenv()
vectors = np.load("data/review_vectors.npy")
reviews = pd.read_csv("data/review_index.csv").iloc[: len(vectors)]
print("Loading", len(reviews), "reviews")

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.execute("DROP TABLE IF EXISTS reviews")
    conn.execute(
        """CREATE TABLE reviews (
            id SERIAL PRIMARY KEY,
            app TEXT NOT NULL,
            score INT NOT NULL,
            posted TEXT,
            sentiment TEXT,
            content TEXT NOT NULL,
            embedding vector(768) NOT NULL
        )"""
    )
    rows = [
        (r.app, int(r.score), str(r.at), r.sentiment, r.content,
         "[" + ",".join(f"{x:.6f}" for x in v) + "]")
        for r, v in zip(reviews.itertuples(index=False), vectors)
    ]
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO reviews (app, score, posted, sentiment, content, embedding) "
            "VALUES (%s, %s, %s, %s, %s, %s::vector)",
            rows,
        )
    conn.commit()
    n = conn.execute("SELECT count(*) FROM reviews").fetchone()[0]
    print("Rows in database:", n)