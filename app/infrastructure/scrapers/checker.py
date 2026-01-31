import logging
import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.domain.interfaces.llm import LLMInterface

logger = logging.getLogger(__name__)


class ScrapingQualityChecker:
    """
    수집된 마크다운 결과물의 품질을 휴리스틱 및 시맨틱 분석을 통해 검사하여 부실 여부를 판단함.
    """

    def __init__(self, min_length: int = 300, llm: Optional["LLMInterface"] = None):
        self.min_length = min_length
        self.llm = llm
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

    async def is_poor_async(self, markdown: str) -> bool:
        """
        결과물이 부실하면 True, 충분하면 False 반환 (비동기 분석 지원)
        
        Args:
            markdown: 검사할 마크다운 문자열
        """
        # 1. Sync Heuristic Checks
        if self.is_poor(markdown):
            return True

        content = markdown

        # 2. Morphological Analysis (Heuristics for Navigation/Disjointed text)
        if self._is_navigation_heavy(content):
            logger.warning("Content seems to be a list of nouns or navigation menu.")
            return True

        # 3. Semantic Coherence Check (Optional LLM)
        if self.llm and len(content) > self.min_length:
            try:
                # LLM을 활용한 한영 혼용 및 문맥 정합성 최종 판독
                prompt = (
                    "Below is a scraped markdown content. Determine if it is a coherent informative text "
                    "or just a collection of navigation menus/disjointed fragments. "
                    "Answer only 'COHERENT' or 'DISJOINTED'.\n\n"
                    f"Content Snippet (first 1000 chars):\n{content[:1000]}"
                )
                judgment = await self.llm.agenerate(prompt)
                if "DISJOINTED" in judgment.upper():
                    logger.warning("LLM judged the content as disjointed/navigation-heavy.")
                    return True
            except Exception as e:
                logger.warning(f"Semantic quality check failed: {e}")

        return False

    def is_poor(self, markdown: str) -> bool:
        """
        동적 로직 없이 단순 휴리스틱만 검사 (Sync)
        
        Args:
            markdown: 검사할 마크다운 문자열
        """
        content = markdown

        # 1. Minimum Length 및 내용 밀도 체크
        if len(content) < self.min_length:
            logger.warning(f"Content too short: {len(content)} characters (min: {self.min_length})")
            return True

        # 2. JS Blocked / 차단 키워드 체크
        content_lower = content.lower()
        for kw in self.blocked_keywords:
            if kw in content_lower:
                logger.warning(f"Blocked keyword detected: {kw}")
                return True

        # 3. Structure Failure 체크
        headers = re.findall(r"^#+ ", content, re.MULTILINE)
        paragraphs = re.findall(r"\n\s*\n", content)
        if len(headers) == 0 and len(paragraphs) < 2:
            logger.warning("Structure failure: No headers and very few paragraphs detected.")
            return True

        return False

    def _is_navigation_heavy(self, text: str) -> bool:
        """
        텍스트가 문장형이 아닌 단순 명사 나열(메뉴 등)인지 판별.
        종결 기호(. ? ! 다 요)의 빈도가 낮으면 부실한 것으로 판단.
        """
        if len(text) < 500:
            return False

        # 종결 문자 패턴
        end_markers = re.findall(r"[.!?다요]\s", text)

        # 텍스트 길이 대비 종결 기호 비율이 극도로 낮으면 메뉴성 리스트로 판단
        ratio = len(end_markers) / (len(text) / 1000)
        if ratio < 3:
            return True
        return False
