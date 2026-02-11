import json
import logging

from app.domain.interfaces.llm import LLMInterface
from app.domain.value_objects.intent import IntentType, UserIntent

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    사용자 쿼리의 의도(Intent)를 분석하여 검색 전략을 결정하는 Domain Service.

    LLM을 사용하여 다음을 수행:
    1. 의도 분류 (GENERAL_QUERY, COMPARE, SUMMARIZE, FILTER_BY_TOPIC)
    2. 검색 대상(targets) 추출 (Document ID, Entity Name 등)
    3. 구조화된 결과 반환 (Pydantic UserIntent)
    """

    def __init__(self, llm: LLMInterface):
        self.llm = llm

    async def classify(self, query: str, history: list[dict], max_retries: int = 3) -> UserIntent:
        """
        사용자 쿼리와 대화 히스토리를 분석하여 의도를 분류한다. (Retry 로직 포함)
        """
        import asyncio
        import random

        # 1. 히스토리 포맷팅 (최근 10턴 사용)
        history_text = self._format_history(history[-10:])
        prompt = self._build_prompt(query, history_text)

        last_error = None
        for attempt in range(max_retries):
            try:
                # 2. LLM 호출
                logger.info(f"Classifying intent (Attempt {attempt + 1}/{max_retries}) for query: {query}")
                raw_response_obj = await self.llm.agenerate(prompt)
                raw_response = str(raw_response_obj).strip()

                # 3. JSON 파싱 및 Pydantic 검증
                json_start = raw_response.find("{")
                json_end = raw_response.rfind("}") + 1
                
                if json_start == -1 or json_end == 0:
                    raise ValueError(f"No JSON found in LLM response: {raw_response}")

                json_str = raw_response[json_start:json_end]
                intent_data = json.loads(json_str)
                user_intent = UserIntent(**intent_data)

                logger.info(f"Intent classified: {user_intent.intent.value}, targets: {user_intent.targets}")
                return user_intent

            except (json.JSONDecodeError, ValueError, Exception) as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed for query '{query}': {e}")
                
                # Exponential backoff with jitter
                if attempt < max_retries - 1:
                    wait_time = (2**attempt) + random.uniform(0, 1)
                    await asyncio.sleep(wait_time)
                continue

        logger.error(f"Intent classification failed after {max_retries} attempts: {last_error}")
        if last_error:
            raise last_error
        
        raise ValueError("Intent classification failed with unknown error")

    def _format_history(self, history: list[dict]) -> str:
        """대화 히스토리를 프롬프트용 텍스트로 변환"""
        if not history:
            return ""

        lines = []
        for msg in history:
            role = "Human" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def _build_prompt(self, query: str, history_text: str) -> str:
        """Intent Classification을 위한 LLM Prompt 생성"""
        return f"""You are an expert intent classifier for a RAG (Retrieval Augmented Generation) system.

Your task is to analyze the user's query and determine:
1. **Intent Type**: What is the user trying to do?
2. **Targets**: Which specific documents, entities, or topics should be retrieved?

**Intent Types:**
- `general_query`: General question without specific targets (search entire knowledge base)
- `compare`: User wants to compare multiple specific items/documents
- `summarize`: User wants to summarize a specific document
- `filter_by_topic`: User wants to filter by topic/category/entity type

**Instructions:**
1. Read the chat history to understand context and previously mentioned entities.
2. Analyze the current query.
3. Identify specific targets (document names, URLs, entity names) if mentioned.
4. Extract key entities (people, organizations, locations) for Graph Search.
5. Output ONLY a valid JSON object with this structure:

```json
{{
  "intent": "one of [general_query, compare, summarize, filter_by_topic]",
  "targets": ["list", "of", "specific", "targets (e.g., document titles, URLs, program names)"],
  "entities": ["list", "of", "extracted", "entities", "and", "aliases"],
  "reasoning": "brief explanation of your decision"
}}
```

**CRITICAL**: If the user mentions a specific program (e.g., "어쩌다 어른", "세바시"), entity, or document title, YOU MUST include it in the `targets` list.

**Examples:**

User: "인공지능이 뭐야?"
→ {{"intent": "general_query", "targets": [], "reasoning": "No specific target mentioned"}}

User: "Claude와 GPT-4를 비교해줘"
→ {{"intent": "compare", "targets": ["claude", "gpt-4"], "reasoning": "User wants comparison"}}

User: "이 문서 요약해줘" (after discussing LangChain)
→ {{"intent": "summarize", "targets": ["langchain"], "reasoning": "User refers to previously discussed document"}}

User: "Python 관련된 것만 보여줘"
→ {{"intent": "filter_by_topic", "targets": ["python"], "reasoning": "User wants to filter by topic"}}

User: "어쩌다 어른에 대해서 알려줘"
→ {{"intent": "general_query", "targets": ["어쩌다 어른"], "reasoning": "User is asking about a specific program"}}

---

**Chat History:**
{history_text if history_text else "(No previous conversation)"}

**Current Query:**
{query}

**Output (JSON only):**"""
