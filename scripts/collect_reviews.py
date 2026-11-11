import time
from google_play_scraper import reviews, Sort
import pandas as pd

apps = {
    "zomato": "com.application.zomato",
    "swiggy": "in.swiggy.android",
}

TARGET = 10000

for name, app_id in apps.items():
    all_reviews = []
    token = None
    while len(all_reviews) < TARGET:
        batch, token = reviews(
            app_id,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=200,
            continuation_token=token,
        )
        if not batch:
            break
        all_reviews.extend(batch)
        print(name, len(all_reviews))
        time.sleep(1)

    df = pd.DataFrame(all_reviews)[["content", "score", "at", "thumbsUpCount"]]
    df = df.drop_duplicates(subset=["content", "at"])
    df.to_csv(f"data/{name}_reviews.csv", index=False)
    print(name, len(df), "reviews saved")