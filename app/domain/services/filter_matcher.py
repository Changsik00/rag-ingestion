"""
FilterMatcher Service

Spec 073: Fuzzy Filter Matching
Semantic Similarity 기반 Source Filter 매칭 서비스.
"""

from collections.abc import Callable
from functools import lru_cache

import numpy as np

from app.core.logger import setup_logger

logger = setup_logger(__name__)


class FilterMatcher:
    """
    Source Filter Fuzzy Matching Service.

    Exact Match를 우선하고, 실패 시 Semantic Similarity로 매칭합니다.

    Example:
        >>> matcher = FilterMatcher(embedding_fn, similarity_threshold=0.85)
        >>> matcher.match_source("claude", ["Claude AI", "GPT-4"])
        "Claude AI"  # similarity: 0.92
    """

    def __init__(self, embedding_fn: Callable[[str], list[float]], similarity_threshold: float = 0.85):
        """
        Args:
            embedding_fn: Embedding 함수 (예: chroma_repo._embedding_function.embed_query)
            similarity_threshold: 유사도 임계값 (0.85 = 85%)
        """
        self.embedding_fn = embedding_fn
        self.similarity_threshold = similarity_threshold

    def match_source(self, target: str, available_sources: list[str]) -> str | None:
        """
        Target을 Available Sources 중 가장 유사한 것과 매칭합니다.

        Args:
            target: 사용자 질문에서 추출된 타겟 (예: "claude")
            available_sources: DB에 실제 존재하는 Source 목록

        Returns:
            str: 매칭된 Source 이름
            None: 매칭 실패 (Threshold 미달 또는 빈 목록)

        Example:
            >>> matcher.match_source("claude", ["Claude AI", "GPT-4"])
            "Claude AI"  # similarity: 0.92
        """
        if not available_sources:
            logger.warning("Available sources list is empty")
            return None

        # 1. Exact Match (Case-Insensitive) - Performance Optimization
        for source in available_sources:
            if target.lower() == source.lower():
                logger.info(f"✅ Exact match found: '{target}' -> '{source}'")
                return source

        # 2. Semantic Similarity (Fuzzy Matching)
        try:
            target_emb = self._get_embedding(target)
            best_match = None
            best_score = 0.0

            for source in available_sources:
                source_emb = self._get_embedding(source)
                similarity = self._cosine_similarity(target_emb, source_emb)

                if similarity > best_score:
                    best_score = similarity
                    best_match = source

            if best_score >= self.similarity_threshold:
                logger.info(f"🔍 Fuzzy match found: '{target}' -> '{best_match}' (similarity: {best_score:.2f})")
                return best_match
            else:
                logger.warning(
                    f"❌ No match for '{target}'. Best candidate: '{best_match}' "
                    f"(similarity: {best_score:.2f} < threshold: {self.similarity_threshold})"
                )
                return None

        except Exception as e:
            logger.error(f"Fuzzy matching failed for '{target}': {e}")
            return None

    @lru_cache(maxsize=256)
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Embedding을 캐싱하여 재계산 방지.

        Args:
            text: 임베딩할 텍스트

        Returns:
            np.ndarray: Embedding 벡터
        """
        return np.array(self.embedding_fn(text))

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        코사인 유사도 계산.

        Args:
            vec1: 첫 번째 벡터
            vec2: 두 번째 벡터

        Returns:
            float: 코사인 유사도 (0.0 ~ 1.0)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        # Avoid division by zero
        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))
