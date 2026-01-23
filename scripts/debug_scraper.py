import os
import sys

# Create a fake module structure to allow imports if running from script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.infrastructure.scrapers.trafilatura_scraper import TrafilaturaWebScraper


def test_scraper(url):
    print(f"Testing Scraper for: {url}")
    scraper = TrafilaturaWebScraper()
    try:
        result = scraper.scrape(url)
        print("✅ Scrape Successful!")
        print(f"Title: {result.metadata.get('title')}")
        print(f"URL: {result.url}")
        print(f"Meta: {result.metadata}")
        print("-" * 40)
        print("Markdown Preview (First 500 chars):")
        print(result.markdown[:500])
        print("-" * 40)

        # Check for specific expected content (e.g. "Elon Musk")
        if "일론" in result.markdown or "Musk" in result.markdown:
             print("✅ Content verification: Found '일론' or 'Musk' in text.")
        else:
             print("⚠️ Content verification: Keywords not found. Might be empty or blocked.")

    except Exception as e:
        print(f"❌ Scrape Failed: {e}")

if __name__ == "__main__":
    target_url = "https://namu.wiki/w/%EC%9D%BC%EB%A1%A0%20%EB%A8%B8%EC%8A%A4%ED%81%AC"
    if len(sys.argv) > 1:
        target_url = sys.argv[1]

    test_scraper(target_url)
