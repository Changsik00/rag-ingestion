import asyncio
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from app.infrastructure.scrapers.youtube_scraper import YouTubeScraper

load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("YouTubeVerify")


async def verify_video(scraper: YouTubeScraper, url: str, label: str, force_stt: bool = False):
    logger.info(f"\n{'=' * 50}\n[TEST] {label}\nURL: {url}\n{'=' * 50}")

    try:
        if force_stt:
            logger.info("Force STT mode enabled: Bypassing YouTubeTranscriptApi...")
            # Monkeypatch _get_transcript to return None
            original_get = scraper._get_transcript

            async def mock_get(vid):
                return None

            scraper._get_transcript = mock_get

        result = await scraper.scrape(url)

        if force_stt:
            # Restore
            scraper._get_transcript = original_get

        output_dir = Path("data/verification")
        output_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{label.lower().replace(' ', '_')}_{result.metadata.get('video_id', 'unknown')}.md"
        output_path = output_dir / file_name

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.markdown)

        logger.info(f"✅ Success! Result saved to: {output_path}")
        logger.info(f"Summary Preview: {result.markdown[:200]}...")

    except Exception as e:
        logger.error(f"❌ Failed to verify {label}: {str(e)}")


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Scraper Verification Script")
    parser.add_argument("--url", type=str, help="YouTube video URL to scrape")
    parser.add_argument("--force-stt", action="store_true", help="Force Whisper STT by bypassing API")
    args = parser.parse_args()

    scraper = YouTubeScraper()

    if args.url:
        # 단일 URL 테스트
        await verify_video(scraper, args.url, "Custom URL", force_stt=args.force_stt)
    else:
        # 기본 테스트 케이스 실행
        videos = [
            {
                "url": "https://www.youtube.com/watch?v=aircAruvnKk",  # 3Blue1Brown
                "label": "With Subtitles (3Blue1Brown)",
            },
            {
                "url": "https://www.youtube.com/watch?v=aircAruvnKk",
                "label": "Force STT (3Blue1Brown)",
                "force_stt": True,
            },
        ]

        for video in videos:
            await verify_video(scraper, video["url"], video["label"], force_stt=video.get("force_stt", False))


if __name__ == "__main__":
    asyncio.run(main())
