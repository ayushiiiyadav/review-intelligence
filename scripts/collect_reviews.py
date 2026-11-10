from google_play_scraper import reviews, Sort
import pandas as pd

apps = {
    "zomato": "com.application.zomato",
    "swiggy": "in.swiggy.android",
}

for name, app_id in apps.items():
    result, _ = reviews(
        app_id,
        lang="en",
        country="in",
        sort=Sort.NEWEST,
        count=2000,
    )
    df = pd.DataFrame(result)[["content", "score", "at", "thumbsUpCount"]]
    df.to_csv(f"data/{name}_reviews.csv", index=False)
    print(name, len(df), "reviews saved")