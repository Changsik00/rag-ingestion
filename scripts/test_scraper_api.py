import json
import sys

import requests


def run_scraper_api_test(url: str):
    """
    Test the /debug/scrape endpoint which bypasses the database.
    """
    api_endpoint = "http://localhost:8000/debug/scrape"
    payload = {"url": url}

    print(f"📡 Sending request to {api_endpoint}...")
    print(f"🔗 Target URL: {url}")

    try:
        resp = requests.post(api_endpoint, json=payload, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            print("\n✅ Scraper Success!")
            print("=" * 60)
            print(f"📄 Title: {data.get('metadata', {}).get('title', 'N/A')}")
            print(f"🔗 Source: {data.get('url')}")
            print("=" * 60)

            markdown = data.get('markdown', '')
            preview_len = 500
            print(f"\n📝 Content Preview (First {preview_len} chars):\n")
            print(markdown[:preview_len])
            if len(markdown) > preview_len:
                print("\n... (truncated)")

            print("\n" + "=" * 60)
            print("MetaData:")
            print(json.dumps(data.get('metadata'), indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ Request Failed: {resp.status_code}")
            print(resp.text)

    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API.")
        print("💡 Hint: Ensure 'rag-backend' is running and mapped to port 8000.")
        print("   Run: docker-compose up -d backend")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_scraper_api.py <URL>")
        print("Example: python test_scraper_api.py https://example.com")
        sys.exit(1)

    target_url = sys.argv[1]
    run_scraper_api_test(target_url)
