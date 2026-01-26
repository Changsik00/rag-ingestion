import logging
import re

from app.schemas.ingest import IngestResponse

logger = logging.getLogger(__name__)


class ScrapingQualityChecker:
    """
    수집된 마크다운 결과물의 품질을 휴리스틱하게 검사하여 부실 여부를 판단함.
    """

    def __init__(self, min_length: int = 300):
        self.min_length = min_length
        # JS 차단 및 클라우드플레어 관련 키워드
        self.blocked_keywords = [
            "javascript를 활성화해주세요",
            "please enable javascript",
            "enable cookies",
            "cloudflare",
            "captcha",
            "access denied",
            "forbidden",
            "attention required",
        ]

    def is_poor(self, result: IngestResponse) -> bool:
        """
        결과물이 부실하면 True, 충분하면 False 반환
        """
        content = result.markdown
        metadata = result.metadata

        # 1. Minimum Length 체크
        if len(content) < self.min_length:
            logger.warning(f"Content too short: {len(content)} characters (min: {self.min_length})")
            return True

        # 2. JS Blocked / 차단 키워드 체크
        content_lower = content.lower()
        for kw in self.blocked_keywords:
            if kw in content_lower:
                logger.warning(f"Blocked keyword detected: {kw}")
                return True

        # 3. Structure Failure 체크 (제목이나 단락이 거의 없는 경우)
        # 마크다운 헤더(#) 개수 파악
        headers = re.findall(r"^#+ ", content, re.MULTILINE)
        # 단락(두 줄 개행) 개수 파악
        paragraphs = re.findall(r"\n\s*\n", content)

        if len(headers) == 0 and len(paragraphs) < 2:
            logger.warning("Structure failure: No headers and very few paragraphs detected.")
            return True

        # 4. Empty Metadata 체크 (제목 누락)
        if not metadata.get("title") or metadata["title"] == "Untitled Document":
            logger.warning("Empty metadata: Title is missing or default.")
            return True

        return False
