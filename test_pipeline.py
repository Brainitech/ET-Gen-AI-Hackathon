import sys
from pprint import pprint
from app.services.rss_service import poll_et_feeds, init_db

def run_test():
    print("Starting pipeline test...")
    # Polling 1 article per feed to quickly verify the pipeline
    articles = poll_et_feeds(max_per_feed=1)
    print(f"\nExtracted {len(articles)} articles!")
    
    for idx, art in enumerate(articles, 1):
        print(f"\n--- Article {idx} ---")
        print(f"Title: {art.get('title')}")
        print(f"URL: {art.get('url')}")
        print(f"Category: {art.get('category')}")
        print(f"Publish Date: {art.get('publish_date')}")
        text = art.get('full_text', '')
        print(f"Text length: {len(text)} chars")
        if text:
            print(f"Preview: {text[:200]}...")
        else:
            print("FAILED TO EXTRACT TEXT")

if __name__ == "__main__":
    run_test()
