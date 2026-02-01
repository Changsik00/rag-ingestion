import os

import pytest

from app.core.config import get_settings
from app.domain.services.query_rewriter import QueryRewriter
from app.infrastructure.ai.extractors.langchain_extractor import LangChainExtractor

pytestmark = pytest.mark.skip(reason="Requires infrastructure setup - see specs/integration-test-improvement.md")


@pytest.mark.integration
class TestQueryRewriteFlow:
    @pytest.fixture
    def rewriter(self):
        from dotenv import load_dotenv

        load_dotenv()

        # Real LLM Adapter (requires GEMINI_API_KEY in env)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("GEMINI_API_KEY not found")

        from langchain_google_genai import ChatGoogleGenerativeAI

        base_llm = ChatGoogleGenerativeAI(model=get_settings().GEMINI_MODEL_NAME, temperature=0, google_api_key=api_key)
        llm = LangChainExtractor(llm=base_llm)
        return QueryRewriter(llm)

    @pytest.mark.asyncio
    async def test_multi_turn_context_maintenance(self, rewriter):
        """
        사용자가 지적한 '대화가 길어질 때 문맥 유지 실패' 현상을 재현하고 검증.
        Steps:
        1. 일론 머스크 질문 (Conext Establish)
        2. 다른 주제 질문 (Distraction)
        3. 다시 일론 머스크 지칭 질문 (Recall)
        """
        # 1. Turn 1: Establish Context
        query1 = "일론 머스크가 다닌 고등학교는 어디야?"
        history1 = []

        rewrite1 = await rewriter.rewrite(query1, history1)
        print(f"\n[Turn 1] Input: {query1} -> Rewritten: {rewrite1}")
        assert "일론" in rewrite1 or "Musk" in rewrite1

        # 2. Turn 2: Distraction (Car topic)
        # Simulate that Turn 1 was answered
        history2 = [
            {"role": "user", "content": query1},
            {"role": "assistant", "content": "그는 프리토리아 남학교를 다녔습니다."},
        ]
        query2 = "그가 만든 자동차 회사는?"

        rewrite2 = await rewriter.rewrite(query2, history2)
        print(f"\n[Turn 2] Input: {query2} -> Rewritten: {rewrite2}")
        assert "자동차" in rewrite2 or "Car" in rewrite2
        assert "일론" in rewrite2 or "Musk" in rewrite2  # Should resolve 'He'

        # 3. Turn 3: Recall (The problematic step)
        # Simulate Turn 2 answered
        history3 = history2 + [
            {"role": "user", "content": query2},
            {"role": "assistant", "content": "그는 테슬라(Tesla)를 창립했습니다."},
        ]
        query3 = "그가 다닌 그 학교는?"  # Refers back to Turn 1 'School', ignoring Turn 2 'Car'

        rewrite3 = await rewriter.rewrite(query3, history3)
        print(f"\n[Turn 3] Input: {query3} -> Rewritten: {rewrite3}")

        # Critical Assertion: Does it still know 'He' is Musk and 'School' is Pretoria/School context?
        assert "성" not in rewrite3  # Should not be about Tesla 'Castle'(?) - ensuring no hallucination
        assert "일론" in rewrite3 or "Musk" in rewrite3
        assert "학교" in rewrite3 or "School" in rewrite3

    @pytest.mark.asyncio
    async def test_rewriter_value_add_verification(self, rewriter):
        """
        검증: 'Rewriter가 없으면 정말 못 맞추나?'
        """
        # Scenario: Context is about Elon Musk
        query = "Where is his school?"

        # 1. Raw LLM (No Context) - "Rewriter 없이 질문만 던졌을 때"
        base_llm = rewriter.llm.llm
        raw_prompt = f"Rewrite this query to be standalone: {query}"
        raw_result = base_llm.invoke(raw_prompt).content

        print(f"\n[Case 1: No Rewriter (Raw)] Input: '{query}' -> Output: '{raw_result}'")

        # 2. Raw LLM (With Manual History) - "Rewriter 흉내내서 히스토리를 줬을 때"
        manual_context_prompt = f"""
        Chat History:
        User: Tell me about Elon Musk.
        Assistant: He is the CEO of Tesla.

        Follow Up Input: {query}
        Standalone Question:
        """
        manual_result = base_llm.invoke(manual_context_prompt).content
        print(f"\n[Case 2: Manual Context] Input: (History + '{query}') -> Output: '{manual_result}'")

        # 3. QueryRewriter Service - "우리가 만든 서비스 사용"
        # (This automates Case 2)
        history = [
            {"role": "user", "content": "Tell me about Elon Musk."},
            {"role": "assistant", "content": "He is the CEO of Tesla."},
        ]
        service_result = await rewriter.rewrite(query, history)
        print(f"\n[Case 3: QueryRewriter Service] -> Output: '{service_result}'")

        # Assertions
        assert "Elon" not in raw_result, "Case 1 should fail to know Elon"
        assert "Elon" in manual_result, "Case 2 should work (proving context is key)"
        assert "Elon" in service_result, "Case 3 should work (service automation)"
