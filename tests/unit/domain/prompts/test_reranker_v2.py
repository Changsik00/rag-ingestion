"""
Reranker v2 Prompt 검증 테스트

Spec 069: Task 1-2
프롬프트 형식 검증 및 JSON 파싱 테스트
"""
import json
import pytest


def test_reranker_v2_prompt_exists():
    """reranker_v2.py 모듈 import 확인"""
    from app.domain.services.prompts.reranker_v2 import RERANKER_PROMPT_V2
    
    assert RERANKER_PROMPT_V2 is not None
    assert len(RERANKER_PROMPT_V2) > 0


def test_reranker_v2_prompt_format():
    """v2 프롬프트가 올바른 형식으로 파싱되는지 확인"""
    from app.domain.services.prompts.reranker_v2 import RERANKER_PROMPT_V2
    
    # Given: 테스트 질문과 청크
    query = "일론 머스크의 SpaceX와 Tesla 비교"
    chunk_text = "SpaceX는 일론 머스크가 설립한 우주 탐사 기업입니다."
    
    # When: 프롬프트 포맷팅
    prompt = RERANKER_PROMPT_V2.format(query=query, chunk_text=chunk_text)
    
    # Then: 필수 요소 포함 확인
    assert "Context-Aware" in prompt
    assert "Multi-Entity Queries" in prompt
    assert "Self-Verification" in prompt
    assert query in prompt
    assert chunk_text in prompt
    
    # PENALTY 규칙이 제거되었는지 확인
    assert "PENALTY" not in prompt
    assert "Heavily penalize" not in prompt


def test_reranker_v2_response_format():
    """v2 프롬프트 응답 형식 검증 (JSON 파싱)"""
    # Given: LLM 응답 (Mock)
    mock_response = '{"score": 8, "reasoning": "SpaceX에 대한 상세한 정보를 제공하므로 관련성 높음"}'
    
    # When: JSON 파싱
    result = json.loads(mock_response)
    
    # Then: 필수 필드 존재 및 타입 확인
    assert "score" in result
    assert "reasoning" in result
    assert isinstance(result["score"], int)
    assert isinstance(result["reasoning"], str)
    assert 0 <= result["score"] <= 10


def test_reranker_v2_multi_entity_guideline():
    """Multi-Entity Query 가이드라인 존재 확인"""
    from app.domain.services.prompts.reranker_v2 import RERANKER_PROMPT_V2
    
    # Given/When: 프롬프트 내용 확인
    # Then: Multi-Entity 가이드라인 포함
    assert "A와 B 비교" in RERANKER_PROMPT_V2
    assert "SpaceX와 Tesla" in RERANKER_PROMPT_V2
    

def test_reranker_v2_name_mention_guideline():
    """Name Mentions 가이드라인 존재 확인"""
    from app.domain.services.prompts.reranker_v2 import RERANKER_PROMPT_V2
    
    # Given/When: 프롬프트 내용 확인
    # Then: Name Mentions 가이드라인 포함
    assert "SPECIFIC CONTEXT" in RERANKER_PROMPT_V2
    assert "SOMEWHAT RELEVANT" in RERANKER_PROMPT_V2
    assert "score 4-6" in RERANKER_PROMPT_V2
    assert "어쩌다 어른" in RERANKER_PROMPT_V2  # 기존 테스트 케이스 예시


def test_reranker_v2_self_verification_guideline():
    """Self-Verification 가이드라인 존재 확인"""
    from app.domain.services.prompts.reranker_v2 import RERANKER_PROMPT_V2
    
    # Given/When: 프롬프트 내용 확인
    # Then: Self-Verification 가이드라인 포함
    assert "Self-Verification" in RERANKER_PROMPT_V2
    assert "Does this chunk help answer the query?" in RERANKER_PROMPT_V2
