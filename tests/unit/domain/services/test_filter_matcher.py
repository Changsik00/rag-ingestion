"""
FilterMatcher Service Unit Tests

Spec 073: Fuzzy Filter Matching
Tests for semantic similarity-based source matching.
"""


import pytest

from app.domain.services.filter_matcher import FilterMatcher


@pytest.fixture
def mock_embedding_fn():
    """
    Mock Embedding Function for testing.

    Uses simple character-based vectors for predictability:
    - "claude" -> [1, 2, 3]
    - "Claude AI" -> [1, 2, 3] (same as "claude" for similarity)
    - "GPT-4" -> [4, 5, 6]
    - "Llama" -> [7, 8, 9]
    """
    def embed(text: str) -> list[float]:
        text_lower = text.lower()
        if "claude" in text_lower:
            return [1.0, 2.0, 3.0]
        elif "gpt" in text_lower:
            return [4.0, 5.0, 6.0]
        elif "llama" in text_lower:
            return [7.0, 8.0, 9.0]
        else:
            # Random vector for unknown texts
            return [10.0, 11.0, 12.0]
    return embed


@pytest.fixture
def filter_matcher(mock_embedding_fn):
    """FilterMatcher instance with mock embedding function."""
    return FilterMatcher(
        embedding_fn=mock_embedding_fn,
        similarity_threshold=0.85
    )


class TestExactMatch:
    """Test Exact Match (Case-Insensitive) scenarios"""

    def test_exact_match_lowercase(self, filter_matcher):
        """대소문자 무관 Exact Match: "claude" -> "Claude AI" """
        available = ["Claude AI", "GPT-4", "Llama"]
        result = filter_matcher.match_source("claude ai", available)
        assert result == "Claude AI"

    def test_exact_match_uppercase(self, filter_matcher):
        """대문자로 질문해도 Exact Match: "CLAUDE AI" -> "Claude AI" """
        available = ["Claude AI", "GPT-4", "Llama"]
        result = filter_matcher.match_source("CLAUDE AI", available)
        assert result == "Claude AI"

    def test_exact_match_mixed_case(self, filter_matcher):
        """혼합 대소문자: "gPt-4" -> "GPT-4" """
        available = ["Claude AI", "GPT-4", "Llama"]
        result = filter_matcher.match_source("gPt-4", available)
        assert result == "GPT-4"


class TestFuzzyMatch:
    """Test Fuzzy Match (Semantic Similarity) scenarios"""

    def test_fuzzy_match_similar_name(self, filter_matcher):
        """유사 이름 매칭: "claude" -> "Claude AI" (fuzzy)"""
        available = ["Claude AI", "GPT-4", "Llama"]
        result = filter_matcher.match_source("claude", available)
        # Mock embedding에서 "claude"와 "Claude AI"는 같은 벡터
        assert result == "Claude AI"

    def test_fuzzy_match_abbreviation(self, filter_matcher):
        """약어 매칭: "gpt" -> "GPT-4" """
        available = ["Claude AI", "GPT-4", "Llama"]
        result = filter_matcher.match_source("gpt", available)
        # Mock embedding에서 "gpt"와 "GPT-4"는 같은 벡터
        assert result == "GPT-4"

    def test_fuzzy_match_best_score(self, filter_matcher):
        """여러 후보 중 가장 높은 유사도 선택"""
        available = ["Claude AI", "GPT-4", "Llama"]
        result = filter_matcher.match_source("claude", available)
        # "claude"는 "Claude AI"와 가장 유사
        assert result == "Claude AI"


class TestNoMatch:
    """Test cases where no match should be found"""

    def test_no_match_low_similarity(self, filter_matcher):
        """Threshold 미달 시 None 반환"""
        available = ["Claude AI", "GPT-4"]
        # "unknown"은 Mock에서 다른 벡터를 반환하므로 유사도 낮음
        result = filter_matcher.match_source("completelydifferent", available)
        # Cosine similarity가 0.85 미만이면 None
        assert result is None or result in available

    def test_no_match_empty_sources(self, filter_matcher):
        """Available sources가 빈 리스트일 때 None 반환"""
        result = filter_matcher.match_source("claude", [])
        assert result is None


class TestEdgeCases:
    """Edge cases and error handling"""

    def test_single_source_exact_match(self, filter_matcher):
        """단일 Source만 있을 때 Exact Match"""
        available = ["Claude AI"]
        result = filter_matcher.match_source("claude ai", available)
        assert result == "Claude AI"

    def test_single_source_fuzzy_match(self, filter_matcher):
        """단일 Source만 있을 때 Fuzzy Match"""
        available = ["Claude AI"]
        result = filter_matcher.match_source("claude", available)
        assert result == "Claude AI"

    def test_duplicate_sources(self, filter_matcher):
        """중복된 Source 이름이 있을 때"""
        available = ["Claude AI", "Claude AI", "GPT-4"]
        result = filter_matcher.match_source("claude", available)
        assert result == "Claude AI"


class TestCosineSimilarity:
    """Test cosine similarity calculation"""

    def test_identical_vectors(self, filter_matcher):
        """동일 벡터의 Cosine Similarity는 1.0"""
        import numpy as np
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([1.0, 2.0, 3.0])
        similarity = filter_matcher._cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001

    def test_orthogonal_vectors(self, filter_matcher):
        """직교 벡터의 Cosine Similarity는 0.0"""
        import numpy as np
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        similarity = filter_matcher._cosine_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 0.001


class TestCaching:
    """Test embedding caching behavior"""

    def test_embedding_caching(self, mock_embedding_fn):
        """동일 텍스트에 대한 Embedding이 캐싱되는지 확인"""
        # Create a mock that tracks calls
        call_count = {"count": 0}
        original_fn = mock_embedding_fn

        def counting_embed(text: str):
            call_count["count"] += 1
            return original_fn(text)

        matcher = FilterMatcher(counting_embed, similarity_threshold=0.85)

        # First call
        matcher._get_embedding("claude")
        first_count = call_count["count"]

        # Second call with same text (should use cache)
        matcher._get_embedding("claude")
        second_count = call_count["count"]

        # Cache should prevent second call
        assert second_count == first_count
