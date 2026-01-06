import requests
import json

def test_news_api(symbol):
    print(f"Testing API for {symbol}...")
    try:
        url = f"http://localhost:8000/api/stock/news/{symbol}"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            print(f"Success! Got {len(data)} items.")
            # Check if titles resemble the company name
            for item in data[:2]:
                print(f"Title: {item['title']}")
                print(f"Link: {item['link']}")
        else:
            print(f"Failed: {res.status_code} {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_news_api("NVDA")
