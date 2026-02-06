"""
RAG Pipeline의 LangGraph State 정의.

이 모듈은 RAG 파이프라인의 전체 상태를 관리하는 TypedDict를 정의합니다.
Design Guide 005의 3-Layer 아키텍처를 구현합니다:
- Brain (LLM): Intent Classification, Query Rewriting
- Nervous System (LangGraph): State 기반 흐름 제어
- Memory/Body (Repository): 물리적 검색 및 필터 강제
"""

from typing import Annotated, TypedDict

from app.domain.value_objects.chunk import Chunk
from app.domain.value_objects.intent import UserIntent


class RAGGraphState(TypedDict):
    """
    RAG Pipeline의 전체 상태를 관리하는 TypedDict.
    모든 Graph Node는 이 상태를 공유하고 필요한 필드를 업데이트합니다.

    Spec 033: LangGraph State Management
    - Intent Classifier의 결정을 State에 명시적으로 저장
    - 의사결정 과정을 추적 가능하게 함
    - HITL(Human-in-the-Loop) 및 Checkpointer 지원
    """

    # === Input (사용자 요청) ===
    query: str
    """원본 사용자 질문"""

    history: list[dict]
    """대화 이력 (Query Rewriting에 사용)"""

    manual_filters: dict | None
    """사용자가 명시적으로 지정한 필터 (우선순위 최고)"""

    # === Brain Layer (LLM 의사결정) ===
    user_intent: UserIntent | None
    """Intent Classifier가 분석한 사용자 의도"""

    rewritten_query: str | None
    """Query Rewriter가 대화 이력을 반영하여 재작성한 질문"""

    # === Nervous System (라우팅 결정) ===
    auto_filters: dict | None
    """Intent → Filters 변환 결과 (자동 도출)"""

    final_filters: dict | None
    """Manual Filters + Auto Filters 병합 결과 (실제 검색에 사용)"""

    # === Memory/Body (검색 결과) ===
    vector_chunks: Annotated[list[Chunk], lambda x, y: y]
    """Vector DB(ChromaDB) MMR 검색 결과"""

    keyword_chunks: Annotated[list[Chunk], lambda x, y: y]
    """Neo4j Keyword 검색 결과"""

    graph_data: Annotated[list[dict], lambda x, y: y]
    """Neo4j Graph Traversal 결과 (Entity 관계)"""

    rerank_strategy: Annotated[str, lambda x, y: y]
    """사용될 리랭킹 전략 (pointwise, listwise)"""

    reranked_chunks: list[Chunk]
    """LLM Reranker에 의해 정렬 및 필터링된 최종 청크들"""

    rerank_log: Annotated[list[dict], lambda x, y: y]
    """리랭킹 과정의 상세ログ (score, reasoning 등) - 매 실행 시 덮어쓰기 위해 Annotated[list, lambda x, y: y] 사용"""

    # === Output (최종 결과) ===
    fallback_triggered: Annotated[bool, lambda x, y: y]
    """필터 검색 실패로 인해 전역 검색(Fallback)이 수행되었는지 여부"""

    reasoning_log: Annotated[list[str], lambda x, y: y]
    """각 노드의 사고 과정 및 의사결정 로그"""

    full_context: Annotated[str, lambda x, y: y]
    """LLM에게 제공할 포맷팅된 컨텍스트 (Citations 포함)"""

    citations: Annotated[list[dict], lambda x, y: y]
    """답변에 사용된 출처 정보 (index, source, url, title 등 포함)"""

    final_answer: Annotated[str, lambda x, y: y]
    """LLM이 생성한 최종 답변"""
