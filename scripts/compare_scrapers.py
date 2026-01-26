import argparse
import asyncio
import os
import time

from dotenv import load_dotenv

from app.infrastructure.scrapers.checker import ScrapingQualityChecker
from app.infrastructure.scrapers.firecrawl_scraper import FirecrawlWebScraper
from app.infrastructure.scrapers.trafilatura_scraper import TrafilaturaWebScraper

# Load environment variables
load_dotenv()


async def compare_scrapers(url: str, output_dir: str = "comparison_results"):
    print(f"\n🚀 Comparing scrapers for URL: {url}\n")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    trafilatura_scraper = TrafilaturaWebScraper()
    firecrawl_scraper = FirecrawlWebScraper()
    quality_checker = ScrapingQualityChecker()

    results = {}

    # 1. Trafilatura
    print("--- [1/2] Running Trafilatura ---")
    start_time = time.time()
    try:
        t_result = trafilatura_scraper.scrape(url)
        t_duration = time.time() - start_time
        results["trafilatura"] = {
            "result": t_result,
            "duration": t_duration,
            "is_poor": quality_checker.is_poor(t_result),
        }
        with open(f"{output_dir}/trafilatura_result.md", "w", encoding="utf-8") as f:
            f.write(t_result.markdown)
        print(f"✅ Trafilatura Done ({t_duration:.2f}s)")
    except Exception as e:
        print(f"❌ Trafilatura Failed: {e}")
        results["trafilatura"] = {"error": str(e)}

    # 2. Firecrawl
    print("\n--- [2/2] Running Firecrawl ---")
    start_time = time.time()
    try:
        f_result = firecrawl_scraper.scrape(url)
        f_duration = time.time() - start_time
        results["firecrawl"] = {
            "result": f_result,
            "duration": f_duration,
            "is_poor": quality_checker.is_poor(f_result),
        }
        with open(f"{output_dir}/firecrawl_result.md", "w", encoding="utf-8") as f:
            f.write(f_result.markdown)
        print(f"✅ Firecrawl Done ({f_duration:.2f}s)")
    except Exception as e:
        print(f"❌ Firecrawl Failed: {e}")
        results["firecrawl"] = {"error": str(e)}

    # Summary Table
    print("\n" + "=" * 50)
    print(f"{'Metric':<20} | {'Trafilatura':<15} | {'Firecrawl':<15}")
    print("-" * 50)

    def get_val(engine, key, subkey=None):
        data = results.get(engine)
        if not data or "error" in data:
            return "N/A"
        if subkey:
            return (
                getattr(data["result"], subkey)
                if hasattr(data["result"], subkey)
                else data["result"].get(subkey, "N/A")
            )
        return data.get(key, "N/A")

    def get_meta(engine, key):
        data = results.get(engine)
        if not data or "error" in data:
            return "N/A"
        return data["result"].metadata.get(key, "N/A")

    print(
        f"{'Status':<20} | {'Success' if 'result' in results['trafilatura'] else 'Fail':<15} | {'Success' if 'result' in results['firecrawl'] else 'Fail':<15}"
    )
    print(
        f"{'Duration (s)':<20} | {results['trafilatura'].get('duration', 0):<15.2f} | {results['firecrawl'].get('duration', 0):<15.2f}"
    )

    t_len = len(results["trafilatura"]["result"].markdown) if "result" in results["trafilatura"] else 0
    f_len = len(results["firecrawl"]["result"].markdown) if "result" in results["firecrawl"] else 0
    print(f"{'Content Length':<20} | {t_len:<15} | {f_len:<15}")

    t_poor = results["trafilatura"].get("is_poor", "N/A")
    f_poor = results["firecrawl"].get("is_poor", "N/A")
    print(f"{'Is Poor?':<20} | {str(t_poor):<15} | {str(f_poor):<15}")

    print("-" * 50)
    print(
        f"{'Title':<20} | {str(get_meta('trafilatura', 'title'))[:12] + '...':<15} | {str(get_meta('firecrawl', 'title'))[:12] + '...':<15}"
    )
    print(
        f"{'Author':<20} | {str(get_meta('trafilatura', 'author'))[:12] + '...':<15} | {str(get_meta('firecrawl', 'author'))[:12] + '...':<15}"
    )

    print("=" * 50)
    print(f"\n📂 Results saved in directory: {output_dir}/")
    print(
        f"Compare them side-by-side: code --diff {output_dir}/trafilatura_result.md {output_dir}/firecrawl_result.md\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare Trafilatura and Firecrawl scrapers.")
    parser.get_settings = parser.add_argument("url", help="URL to scrape and compare")
    parser.add_argument("--output", default="comparison_results", help="Directory to save output files")

    args = parser.parse_args()

    asyncio.run(compare_scrapers(args.url, args.output))
