# Recommendations: RAG System Improvement Roadmap

> 이 문서는 **Spec 068**의 실행 계획으로, **Root Cause Analysis**에서 도출된 문제들을 해결하기 위한 구체적인 액션 플랜을 제시합니다.

---

## 🎯 개선 전략 Principles

### 1. Impact First (영향도 우선)
- Critical → High → Medium → Low 순서로 해결
- 사용자 경험에 즉각적 영향을 주는 문제 우선

### 2. Quick Wins 먼저
- 1~3일 내 완료 가능한 작업을 먼저 처리하여 momentum 확보
- 대규모 리팩토링은 Quick Wins 이후 착수

### 3. Test-Driven Improvement
- 모든 개선 사항은 **측정 가능한 Metric**으로 검증
- Before/After 비교 리포트 필수

### 4. Incremental Refactoring
- "Big Bang" 리팩토링 금지
- 작은 단위로 나누어 점진적 개선

---

## 📊 우선순위 매트릭스

```mermaid
quadrantChart
    title Impact vs Effort Matrix
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Plan Carefully
    quadrant-2 Do First (Quick Wins)
    quadrant-3 Low Priority
    quadrant-4 Avoid
    
    Reranker 독소조항 제거: [0.2, 0.8]
    Prompt Test Cases 작성: [0.3, 0.7]
    Deduplication 완성: [0.6, 0.9]
    Clean Architecture 리팩토링: [0.8, 0.6]
    Semantic Chunking POC: [0.4, 0.4]
    Saga Pattern 도입: [0.9, 0.85]
```

---

## 🚀 Phase 1: Quick Wins (1주 내 완료)

### Task 1.1: Reranker 독소조항 제거 ⭐⭐⭐
**Priority**: P0  
**Effort**: 1일  
**Impact**: 🟠 High (Over-filtering 해결)

#### 목표
- PENALTY 규칙 제거
- Context-Aware 프롬프트로 교체
- A/B 테스트로 성능 검증

#### 구체적 작업
```python
# 1. 새 프롬프트 버전 작성
# app/domain/services/prompts/reranker_v2.py
RERANKER_PROMPT_V2 = """
[독소조항 제거, Context-Aware 평가 기준 추가]
"""

# 2. Feature Flag 추가
# config/admin_config.py
RERANKER_VERSION = "v1"  # "v1" or "v2" 선택 가능

# 3. A/B 테스트 스크립트
# scripts/compare_reranker_versions.py
test_queries = [
    "일론 머스크의 SpaceX와 Tesla 비교",
    "Claude와 GPT-4의 차이점",
    ...
]
results_v1 = run_reranker(test_queries, version="v1")
results_v2 = run_reranker(test_queries, version="v2")
compare_metrics(results_v1, results_v2)
```

#### Definition of Done
- [ ] `reranker_v2.py` 작성 완료
- [ ] A/B 테스트 10개 질문으로 실행
- [ ] v2가 v1보다 Recall +10% 이상 확인
- [ ] 기본값을 v2로 변경

---

### Task 1.2: Prompt Test Dataset 구축 ⭐⭐⭐
**Priority**: P0  
**Effort**: 2일  
**Impact**: 🟠 High (프롬프트 품질 검증 인프라)

#### 목표
- Intent Classifier 테스트 케이스 50개 수집
- Pytest 기반 자동 검증 스크립트 작성

#### 구체적 작업
```python
# 1. 테스트 케이스 정의
# tests/prompts/intent_test_cases.yaml
test_cases:
  - query: "어쩌다 어른에 대해 알려줘"
    expected_intent: "general_query"
    expected_targets: ["어쩌다 어른"]
    
  - query: "알쓸신잡 요약해줘"
    expected_intent: "summarize"
    expected_targets: ["알쓸신잡"]
    
  - query: "세바시에서 김미경 강연 찾아줘"
    expected_intent: "filter_by_topic"
    expected_targets: ["세바시", "김미경"]
  
  # ... 50개 이상

# 2. 자동 테스트
# tests/prompts/test_intent_classifier_quality.py
@pytest.mark.parametrize("case", load_test_cases())
def test_intent_classification(case):
    result = intent_classifier.classify(case.query, [])
    
    assert result.intent == case.expected_intent, \
        f"Expected {case.expected_intent}, got {result.intent}"
    
    assert set(result.targets) == set(case.expected_targets), \
        f"Expected {case.expected_targets}, got {result.targets}"

# 3. Coverage 리포트
# scripts/measure_prompt_quality.py
def measure_accuracy():
    total = len(test_cases)
    passed = run_tests()
    accuracy = passed / total * 100
    print(f"Intent Classification Accuracy: {accuracy}%")
```

#### Definition of Done
- [ ] 50개 테스트 케이스 작성 (다양한 도메인)
- [ ] Pytest 자동 검증 통과율 측정
- [ ] 현재 Accuracy 측정 (Baseline 수립)
- [ ] CI/CD에 Prompt Quality Test 추가

---

### Task 1.3: ChromaDB Upsert 로직 추가 ⭐⭐
**Priority**: P1  
**Effort**: 1일  
**Impact**: 🟡 Medium (중복 저장 방지)

#### 목표
- `collection.add` → `collection.upsert`로 변경
- Document ID 기반 중복 방지

#### 구체적 작업
```python
# Before
# app/infrastructure/repositories/chroma.py
def save_chunks(self, chunks: list[Chunk]):
    self.collection.add(
        ids=[c.id for c in chunks],
        documents=[c.text for c in chunks],
        ...
    )

# After
def save_chunks(self, chunks: list[Chunk]):
    # Upsert: 기존 ID가 있으면 업데이트, 없으면 추가
    self.collection.upsert(
        ids=[c.id for c in chunks],
        documents=[c.text for c in chunks],
        ...
    )
```

#### Definition of Done
- [ ] Chroma `upsert` 메서드 적용
- [ ] 동일 문서 2번 수집 시 중복 생성 안 되는지 테스트
- [ ] Integration Test 추가

---

## 🔧 Phase 2: Core Improvements (2~3주)

### Task 2.1: Deduplication Service 완성 ⭐⭐⭐
**Priority**: P0  
**Effort**: 5일  
**Impact**: 🔴 Critical (중복 수집 방지)

#### 목표
- 4가지 Strategy (ID/Metadata/TTL/Contents) 실제 구현
- Ingestion Graph에 Dedup Node 추가
- Admin UI에서 Strategy 선택 가능

#### Architecture
```python
# 1. Strategy Interface
# app/domain/interfaces/deduplication.py
class DeduplicationStrategy(Protocol):
    async def is_duplicate(self, job: IngestionJob) -> bool:
        """중복 여부 판단"""
        ...

# 2. Concrete Strategies
# app/domain/services/deduplication/strategies.py
class IDCheckingStrategy:
    async def is_duplicate(self, job: IngestionJob) -> bool:
        # Source URL이 이미 COMPLETED 상태인지 확인
        existing = await self.job_repo.get_by_source(job.source_url)
        return existing and existing.status == JobStatus.COMPLETED

class MetadataCheckStrategy:
    async def is_duplicate(self, job: IngestionJob) -> bool:
        # File Size + Modified Time 비교
        existing = await self.job_repo.get_by_source(job.source_url)
        if not existing:
            return False
        return (
            job.metadata.get("size") == existing.metadata.get("size") and
            job.metadata.get("modified_time") == existing.metadata.get("modified_time")
        )

class TTLStrategy:
    async def is_duplicate(self, job: IngestionJob) -> bool:
        # 마지막 수집 시간 + TTL 체크
        existing = await self.job_repo.get_by_source(job.source_url)
        if not existing:
            return False
        ttl = timedelta(hours=job.metadata.get("ttl_hours", 24))
        return (datetime.now() - existing.created_at) < ttl

class ContentsHashStrategy:
    async def is_duplicate(self, job: IngestionJob) -> bool:
        # Content Hash 비교
        current_hash = hashlib.sha256(job.content.encode()).hexdigest()
        existing = await self.doc_repo.get_by_source(job.source_url)
        if not existing:
            return False
        return existing.metadata.get("content_hash") == current_hash

# 3. Factory
# app/domain/services/deduplication/factory.py
class DeduplicationFactory:
    @staticmethod
    def get_strategy(source_type: str) -> DeduplicationStrategy:
        if source_type == "youtube":
            return IDCheckingStrategy()
        elif source_type == "file":
            return MetadataCheckStrategy()
        elif source_type == "news":
            return TTLStrategy()
        else:
            return ContentsHashStrategy()

# 4. Ingestion Graph 통합
# app/infrastructure/ingestion/nodes.py
async def check_duplicate(state: IngestionState) -> IngestionState:
    job = state["job"]
    strategy = DeduplicationFactory.get_strategy(job.source_type)
    
    is_dup = await strategy.is_duplicate(job)
    if is_dup:
        logger.info(f"Duplicate detected: {job.source_url}")
        return {"status": "skipped", "reason": "duplicate"}
    
    return state

# app/infrastructure/ingestion/graph.py
graph.add_node("check_duplicate", check_duplicate)
graph.add_edge("collect_data", "check_duplicate")
graph.add_conditional_edges(
    "check_duplicate",
    lambda state: "skip" if state.get("status") == "skipped" else "proceed",
    {"skip": END, "proceed": "extract"}
)
```

#### Definition of Done
- [ ] 4가지 Strategy 클래스 구현
- [ ] Factory Pattern 적용
- [ ] Ingestion Graph에 `check_duplicate` 노드 추가
- [ ] Admin UI에서 Strategy 선택 및 Force Refresh 옵션 제공
- [ ] 테스트: 동일 문서 재수집 시 Skip 확인

---

### Task 2.2: Fuzzy Filter Matching ⭐⭐
**Priority**: P1  
**Effort**: 3일  
**Impact**: 🟠 High (필터 매칭 실패 방지)

#### 목표
- Source Filter 적용 시 Exact Match가 아닌 Semantic Similarity 사용
- "Claude" ↔ "claude", "GPT-4" ↔ "gpt4" 등 매칭

#### Architecture
```python
# 1. Filter Matcher Service
# app/domain/services/filter_matcher.py
class FilterMatcher:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.similarity_threshold = 0.85
    
    async def match_source(self, target: str, available_sources: list[str]) -> str | None:
        """
        Target을 Available Sources 중 가장 유사한 것과 매칭
        
        Example:
          target="claude"
          available_sources=["Claude AI", "GPT-4", "Llama"]
          → Returns "Claude AI" (similarity > 85%)
        """
        if target in available_sources:
            return target  # Exact Match
        
        # Semantic Matching
        target_emb = await self.embedding_model.embed(target)
        best_match = None
        best_score = 0
        
        for source in available_sources:
            source_emb = await self.embedding_model.embed(source)
            similarity = cosine_similarity(target_emb, source_emb)
            
            if similarity > best_score:
                best_score = similarity
                best_match = source
        
        if best_score >= self.similarity_threshold:
            logger.info(f"Fuzzy matched '{target}' → '{best_match}' (score: {best_score})")
            return best_match
        
        return None

# 2. RAG Graph에 적용
# app/infrastructure/repositories/rag_nodes.py
async def route_decision(state: RAGGraphState) -> RAGGraphState:
    intent = state["user_intent"]
    manual_filters = state.get("manual_filters")
    
    auto_filters = {}
    if intent.targets:
        # Fuzzy Matching 적용
        matcher = FilterMatcher(embedding_model)
        available_sources = await doc_repo.get_all_source_names()
        
        matched_sources = []
        for target in intent.targets:
            match = await matcher.match_source(target, available_sources)
            if match:
                matched_sources.append(match)
            else:
                logger.warning(f"No match found for target: {target}")
        
        auto_filters["source"] = matched_sources
    
    # Manual Filters 우선
    final_filters = {**auto_filters, **(manual_filters or {})}
    
    return {**state, "auto_filters": auto_filters, "final_filters": final_filters}
```

#### Definition of Done
- [ ] `FilterMatcher` Service 구현
- [ ] Unit Test: "claude", "Claude AI", "CLAUDE" 모두 매칭 확인
- [ ] RAG Graph의 `route_decision` 노드에 통합
- [ ] 실제 질문으로 검증: "Claude와 GPT 비교" → 정상 검색

---

### Task 2.3: LLMInterface 이동 (Clean Architecture) ⭐
**Priority**: P1  
**Effort**: 2일  
**Impact**: 🟡 Medium (Dependency Rule 준수)

#### 목표
- `app/application/interfaces/llm.py` → `app/domain/interfaces/llm.py`
- Dependency Rule 위반 해소

#### 작업 순서
```bash
# 1. 파일 이동
git mv app/application/interfaces/llm.py app/domain/interfaces/llm.py

# 2. Import 경로 일괄 수정
# app/domain/services/intent_classifier.py
- from app.application.interfaces.llm import LLMInterface
+ from app.domain.interfaces.llm_interface import LLMInterface

# 3. 모든 참조 업데이트
rg "from app.application.interfaces.llm" -l | xargs sd \
  "from app.application.interfaces.llm" \
  "from app.domain.interfaces.llm_interface"

# 4. 테스트 실행
pytest tests/
```

#### Definition of Done
- [ ] `LLMInterface` → `domain/interfaces/` 이동
- [ ] 모든 Import 경로 수정
- [ ] 테스트 전체 통과
- [ ] Dependency Rule 검증 스크립트 작성

---

## 🏗️ Phase 3: Major Refactoring (4~6주)

### Task 3.0: RAG 3-Layer Code Structure Refactoring ⭐⭐⭐⭐
**Priority**: P0 (Major Refactoring 최우선)  
**Effort**: 15일  
**Impact**: 🔴 Critical (아키텍처 문서와 코드 일치)

#### 목표
- **개념적으로만 존재하는 RAG 3-Layer를 실제 코드 구조에 반영**
- Brain / Orchestration / Retrieval 3개 Layer를 디렉토리로 분리
- Layer별 독립적인 테스트 및 재사용 가능하도록 설계

#### 현재 문제
```python
# ❌ 현재: 모든 Layer가 한 클래스에 혼재
app/infrastructure/ai/
├── rag_nodes.py (774 lines)  # Brain + Orchestration + Retrieval 모두 포함
└── rag_graph.py              # 단순 Node 연결만

class RAGNodes:
    def classify_intent(self, ...):    # Brain Layer
    def route_decision(self, ...):     # Orchestration Layer
    def retrieve_hybrid(self, ...):    # Retrieval Layer
    def rerank_results(self, ...):     # Brain Layer
    def generate_answer(self, ...):    # Brain Layer
```

#### 목표 구조
```python
# ✅ 목표: Layer별 디렉토리 분리

# 1. Brain Layer (Domain)
app/domain/rag/brain/
├── __init__.py
├── intent_classifier.py      # ✅ 이미 존재 (app/domain/services/)
├── query_rewriter.py          # ✅ 이미 존재 (app/domain/services/)
├── reranker.py                # ⚠️ 이동 필요 (prompts/ → brain/)
└── answer_generator.py        # 🆕 새로 생성 (generate_answer 로직 분리)

# 2. Orchestration Layer (Application)
app/application/rag/orchestration/
├── __init__.py
├── rag_orchestrator.py        # 🆕 High-level RAG Service
├── filter_router.py           # 🆕 route_decision 로직 분리
└── fallback_handler.py        # 🆕 Filter Fallback 전략

# 3. Retrieval Layer (Infrastructure)
app/infrastructure/rag/retrieval/
├── __init__.py
├── hybrid_retriever.py        # 🆕 retrieve_hybrid 로직 분리
├── vector_retriever.py        # 🆕 ChromaDB 검색 캡슐화
├── keyword_retriever.py       # 🆕 Neo4j Keyword 검색 캡슐화
└── graph_retriever.py         # 🆕 Neo4j Graph Traversal 캡슐화

# 4. Graph Builder (Infrastructure)
app/infrastructure/rag/
├── graph_builder.py           # ✅ 이미 존재 (rag_graph.py)
├── nodes.py                   # 🆕 Layer를 조합하여 LangGraph Node 생성
└── langgraph_adapter.py       # 🆕 LangGraph SDK Wrapper
```

#### 상세 작업 계획

##### Week 1: Brain Layer 분리 (5일)

**Day 1-2: Reranker 이동**
```python
# Before: app/domain/services/prompts/reranker.py (프롬프트만)
# After:  app/domain/rag/brain/reranker.py (완전한 Service)

# app/domain/rag/brain/reranker.py
class Reranker:
    """Reranking Logic (Brain Layer)"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
    
    async def rerank_pointwise(
        self, 
        query: str, 
        chunks: list[Chunk]
    ) -> list[ScoredChunk]:
        """Pointwise Reranking"""
        # Move from rag_nodes._rerank_pointwise()
        ...
    
    async def rerank_listwise(
        self, 
        query: str, 
        chunks: list[Chunk]
    ) -> list[ScoredChunk]:
        """Listwise Reranking (Spec 067)"""
        # Move from rag_nodes._rerank_listwise()
        ...
```

**Day 3-4: Answer Generator 분리**
```python
# app/domain/rag/brain/answer_generator.py
class AnswerGenerator:
    """Answer Generation Logic (Brain Layer)"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
    
    async def generate(
        self,
        query: str,
        context: str,
        history: list[dict]
    ) -> str:
        """Generate final answer from context"""
        # Move from rag_nodes.generate_answer()
        ...
    
    def _build_rag_prompt(
        self, 
        query: str, 
        context: str, 
        history: list[dict]
    ) -> str:
        """Build RAG Prompt"""
        ...
```

**Day 5: Brain Layer 통합 테스트**
```python
# tests/domain/rag/brain/test_brain_layer.py
def test_brain_layer_components():
    """Brain Layer 각 컴포넌트 독립 동작 확인"""
    
    # 1. Intent Classifier
    intent = await intent_classifier.classify("질문", [])
    assert intent.intent in IntentType
    
    # 2. Query Rewriter
    rewritten = await query_rewriter.rewrite("질문", intent)
    assert len(rewritten) > 0
    
    # 3. Reranker
    scored = await reranker.rerank_pointwise("질문", chunks)
    assert all(0 <= c.score <= 10 for c in scored)
    
    # 4. Answer Generator
    answer = await answer_generator.generate("질문", "컨텍스트", [])
    assert len(answer) > 0
```

---

##### Week 2: Retrieval Layer 분리 (5일)

**Day 1-2: Retriever 클래스 생성**
```python
# app/infrastructure/rag/retrieval/vector_retriever.py
class VectorRetriever:
    """Vector Search (ChromaDB)"""
    
    def __init__(self, chroma_repo):
        self.chroma = chroma_repo
    
    async def retrieve(
        self, 
        query: str, 
        limit: int = 5, 
        filters: dict | None = None
    ) -> list[Chunk]:
        """Vector MMR Search"""
        # Move from rag_nodes._search_vector()
        return await asyncio.to_thread(
            self.chroma.search_mmr, query, limit, filters
        )

# app/infrastructure/rag/retrieval/keyword_retriever.py
class KeywordRetriever:
    """Keyword Search (Neo4j)"""
    
    def __init__(self, neo4j_doc_repo):
        self.neo4j = neo4j_doc_repo
    
    async def retrieve(...) -> list[Chunk]:
        # Move from rag_nodes._search_keyword()
        ...

# app/infrastructure/rag/retrieval/graph_retriever.py
class GraphRetriever:
    """Graph Traversal (Neo4j)"""
    
    async def retrieve(...) -> list[dict]:
        # Move from rag_nodes._search_graph()
        ...
```

**Day 3-4: Hybrid Retriever 조합**
```python
# app/infrastructure/rag/retrieval/hybrid_retriever.py
class HybridRetriever:
    """Parallel Hybrid Search (Vector + Keyword + Graph)"""
    
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        keyword_retriever: KeywordRetriever,
        graph_retriever: GraphRetriever
    ):
        self.vector = vector_retriever
        self.keyword = keyword_retriever
        self.graph = graph_retriever
    
    async def retrieve(
        self, 
        query: str, 
        entities: list[str] | None = None,
        filters: dict | None = None
    ) -> HybridSearchResult:
        """Parallel execution of all retrievers"""
        # Move from rag_nodes.retrieve_hybrid()
        
        vector_task = self.vector.retrieve(query, filters=filters)
        keyword_task = self.keyword.retrieve(query, filters=filters)
        graph_task = self.graph.retrieve(query, entities=entities)
        
        # Parallel execution
        vector_chunks, keyword_chunks, graph_data = await asyncio.gather(
            vector_task, keyword_task, graph_task
        )
        
        return HybridSearchResult(
            vector_chunks=vector_chunks,
            keyword_chunks=keyword_chunks,
            graph_data=graph_data
        )
```

**Day 5: Retrieval Layer 통합 테스트**

---

##### Week 3: Orchestration Layer 분리 (5일)

**Day 1-3: Filter Router 분리**
```python
# app/application/rag/orchestration/filter_router.py
class FilterRouter:
    """Intent → Filters 변환 및 병합 (Orchestration Layer)"""
    
    def __init__(self, filter_matcher: FilterMatcher):
        self.matcher = filter_matcher
    
    async def route(
        self, 
        intent: UserIntent, 
        manual_filters: dict | None = None
    ) -> dict:
        """Convert Intent to Repository Filters"""
        # Move from rag_nodes.route_decision()
        
        auto_filters = await self._intent_to_filters(intent)
        
        # Manual Filters 우선
        final_filters = {**auto_filters, **(manual_filters or {})}
        
        return final_filters
```

**Day 4-5: RAG Orchestrator 생성**
```python
# app/application/rag/orchestration/rag_orchestrator.py
class RAGOrchestrator:
    """High-level RAG Service (Orchestration Layer)"""
    
    def __init__(
        self,
        # Brain Layer
        intent_classifier: IntentClassifier,
        query_rewriter: QueryRewriter,
        reranker: Reranker,
        answer_generator: AnswerGenerator,
        
        # Orchestration Layer
        filter_router: FilterRouter,
        fallback_handler: FallbackHandler,
        
        # Retrieval Layer
        hybrid_retriever: HybridRetriever
    ):
        self.brain = {...}
        self.retrieval = {...}
        self.orchestration = {...}
    
    async def query(
        self, 
        query: str, 
        history: list[dict],
        manual_filters: dict | None = None
    ) -> RAGResult:
        """Execute complete RAG pipeline"""
        
        # 1. Brain: Intent Classification
        intent = await self.brain.intent_classifier.classify(query, history)
        
        # 2. Brain: Query Rewriting
        rewritten_query = await self.brain.query_rewriter.rewrite(query, intent)
        
        # 3. Orchestration: Filter Routing
        filters = await self.orchestration.filter_router.route(intent, manual_filters)
        
        # 4. Retrieval: Hybrid Search
        search_result = await self.retrieval.hybrid_retriever.retrieve(
            rewritten_query, 
            entities=intent.entities, 
            filters=filters
        )
        
        # 5. Orchestration: Fallback if empty
        if search_result.is_empty():
            search_result = await self.orchestration.fallback_handler.handle(...)
        
        # 6. Brain: Reranking
        all_chunks = search_result.get_all_chunks()
        scored_chunks = await self.brain.reranker.rerank_pointwise(query, all_chunks)
        
        # 7. Brain: Answer Generation
        context = self._format_context(scored_chunks)
        answer = await self.brain.answer_generator.generate(query, context, history)
        
        return RAGResult(answer=answer, ...)
```

---

##### Week 4: LangGraph Integration (4일)

**Day 1-2: Nodes Adapter 생성**
```python
# app/infrastructure/rag/nodes.py
class RAGGraphNodes:
    """LangGraph Node Wrapper (RAGOrchestrator → LangGraph 변환)"""
    
    def __init__(self, orchestrator: RAGOrchestrator):
        self.orch = orchestrator
    
    async def classify_intent(self, state: RAGGraphState) -> RAGGraphState:
        """Node 1: Intent Classification"""
        intent = await self.orch.brain.intent_classifier.classify(
            state["query"], 
            state["history"]
        )
        return {**state, "user_intent": intent}
    
    async def retrieve_hybrid(self, state: RAGGraphState) -> RAGGraphState:
        """Node 3: Hybrid Retrieval"""
        result = await self.orch.retrieval.hybrid_retriever.retrieve(...)
        return {**state, "vector_chunks": result.vector_chunks, ...}
    
    # ... 나머지 Nodes
```

**Day 3-4: 기존 코드와 통합**
```python
# app/interfaces/api/dependencies.py
def get_rag_orchestrator() -> RAGOrchestrator:
    """RAG Orchestrator DI"""
    
    # Brain Layer
    intent_classifier = IntentClassifier(llm)
    query_rewriter = QueryRewriter(llm)
    reranker = Reranker(llm)
    answer_generator = AnswerGenerator(llm)
    
    # Retrieval Layer
    vector_retriever = VectorRetriever(chroma_repo)
    keyword_retriever = KeywordRetriever(neo4j_doc_repo)
    graph_retriever = GraphRetriever(neo4j_graph_repo)
    hybrid_retriever = HybridRetriever(vector_retriever, keyword_retriever, graph_retriever)
    
    # Orchestration Layer
    filter_router = FilterRouter(filter_matcher)
    fallback_handler = FallbackHandler()
    
    return RAGOrchestrator(
        intent_classifier=intent_classifier,
        query_rewriter=query_rewriter,
        reranker=reranker,
        answer_generator=answer_generator,
        filter_router=filter_router,
        fallback_handler=fallback_handler,
        hybrid_retriever=hybrid_retriever
    )

def get_rag_graph() -> CompiledStateGraph:
    """LangGraph Builder (기존 인터페이스 유지)"""
    orchestrator = get_rag_orchestrator()
    nodes = RAGGraphNodes(orchestrator)
    builder = RAGGraphBuilder(nodes)
    return builder.build()
```

---

#### Definition of Done

**코드 구조**:
- [ ] `app/domain/rag/brain/` 디렉토리 생성 및 4개 클래스 배치
- [ ] `app/application/rag/orchestration/` 디렉토리 생성 및 3개 클래스 배치
- [ ] `app/infrastructure/rag/retrieval/` 디렉토리 생성 및 4개 클래스 배치
- [ ] `app/infrastructure/ai/rag_nodes.py` (774 lines) 삭제

**테스트**:
- [ ] Brain Layer 독립 Unit Test (4개 컴포넌트)
- [ ] Retrieval Layer 독립 Integration Test (3개 Retriever)
- [ ] Orchestration Layer 통합 Test (RAGOrchestrator)
- [ ] 전체 E2E Test 통과 (기존 기능 유지 확인)

**문서**:
- [ ] `docs/architecture/rag_pipeline.md` 업데이트 (코드 구조 반영)
- [ ] ADR (Architecture Decision Record) 작성
- [ ] Layer별 README.md 생성

**검증**:
- [ ] 기존 API Endpoint 정상 동작 (/api/v1/rag/query)
- [ ] Admin UI Playground 정상 동작
- [ ] 성능 저하 없음 (Latency ±5% 이내)

---

### Task 3.1: RAG Graph → Application Layer 이동 ⭐⭐⭐
**Priority**: P2  
**Effort**: 10일  
**Impact**: 🟡 Medium (아키텍처 정렬)

#### 목표
- `infrastructure/repositories/rag_*.py` → `application/services/rag/`
- Infrastructure는 LangGraph SDK Wrapper만 유지

#### 단계별 Migration
```python
# Step 1: 새 디렉토리 구조 생성
app/application/services/rag/
├── __init__.py
├── nodes.py           # RAG Nodes (classify_intent, retrieve, etc.)
├── graph_builder.py   # Graph 구성
└── orchestrator.py    # High-level RAG Service

app/infrastructure/rag/
└── langgraph_adapter.py  # LangGraph SDK Wrapper

# Step 2: Nodes 하나씩 이동 (1~2일)
# app/application/services/rag/nodes.py
async def classify_intent(state: RAGGraphState) -> RAGGraphState:
    """Intent Classification Node"""
    # Move from infrastructure/repositories/rag_nodes.py
    ...

# Step 3: Graph Builder 이동 (2일)
# app/application/services/rag/graph_builder.py
class RAGGraphBuilder:
    def build(self) -> CompiledGraph:
        graph = StateGraph(RAGGraphState)
        graph.add_node("classify_intent", classify_intent)
        ...
        return graph.compile()

# Step 4: API Layer 업데이트 (1일)
# app/interfaces/api/v1/endpoints/rag.py
- from app.infrastructure.repositories.rag_graph import build_rag_graph
+ from app.application.services.rag.graph_builder import RAGGraphBuilder

async def query_rag(request: RAGRequest):
    graph = RAGGraphBuilder().build()
    ...
```

#### Definition of Done
- [ ] 모든 RAG Nodes → `application/services/rag/nodes.py`
- [ ] Graph Builder → `application/services/rag/graph_builder.py`
- [ ] API Endpoints 업데이트
- [ ] 모든 테스트 통과
- [ ] ADR (Architecture Decision Record) 작성

---

### Task 3.2: Saga Pattern for Ingestion ⭐⭐⭐
**Priority**: P3  
**Effort**: 10일  
**Impact**: 🔴 Critical (데이터 일관성 보장)

#### 목표
- Neo4j ↔ ChromaDB 간 Transaction Guarantee
- Partial Failure 시 Rollback

#### Architecture
```python
# 1. Saga Orchestrator
# app/application/services/ingestion/saga_orchestrator.py
class IngestionSaga:
    def __init__(self, neo4j_repo, chroma_repo, audit_logger):
        self.neo4j = neo4j_repo
        self.chroma = chroma_repo
        self.audit = audit_logger
    
    async def execute(self, doc: Document, chunks: list[Chunk]):
        saga_id = uuid.uuid4()
        steps = []
        
        try:
            # Step 1: Save to Neo4j
            await self.audit.log(saga_id, "start", "neo4j_save")
            await self.neo4j.save_document(doc)
            await self.neo4j.save_chunks(chunks)
            steps.append("neo4j")
            await self.audit.log(saga_id, "success", "neo4j_save")
            
            # Step 2: Save to ChromaDB
            await self.audit.log(saga_id, "start", "chroma_save")
            await self.chroma.save_chunks(chunks)
            steps.append("chroma")
            await self.audit.log(saga_id, "success", "chroma_save")
            
            # All steps succeeded
            await self.audit.log(saga_id, "complete", "ingestion")
            
        except Exception as e:
            # Compensate: Rollback completed steps
            await self.audit.log(saga_id, "failed", str(e))
            await self._compensate(doc.id, steps)
            raise IngestionError(f"Saga failed: {e}") from e
    
    async def _compensate(self, doc_id: str, completed_steps: list[str]):
        """Rollback in reverse order"""
        for step in reversed(completed_steps):
            try:
                if step == "chroma":
                    await self.chroma.delete_by_document_id(doc_id)
                elif step == "neo4j":
                    await self.neo4j.delete_document(doc_id)
                await self.audit.log(None, "compensated", step)
            except Exception as e:
                logger.error(f"Compensation failed for {step}: {e}")

# 2. Audit Logger
# app/infrastructure/monitoring/saga_audit_logger.py
class SagaAuditLogger:
    async def log(self, saga_id: str, status: str, details: str):
        record = {
            "saga_id": saga_id,
            "timestamp": datetime.now(),
            "status": status,
            "details": details
        }
        # Save to DB or file
        await self.repo.save_audit_log(record)
```

#### Definition of Done
- [ ] `IngestionSaga` Orchestrator 구현
- [ ] Audit Logging 인프라 구축
- [ ] Compensation Logic 테스트 (Neo4j 성공 → Chroma 실패 시나리오)
- [ ] Admin UI에서 Saga 실패 내역 조회 가능

---

## 📈 측정 지표 (Success Metrics)

### Phase 1 (Quick Wins) 목표
- [ ] Reranker Recall +10% 이상
- [ ] Intent Classification Accuracy 측정 (Baseline)
- [ ] 중복 저장 건수 0건 (ChromaDB)

### Phase 2 (Core Improvements) 목표
- [ ] Deduplication Skip Rate 측정 (불필요한 재수집 감소율)
- [ ] Filter Matching Success Rate 95% 이상
- [ ] Dependency Rule Violation 0건

### Phase 3 (Major Refactoring) 목표
- [ ] Clean Architecture Compliance 100%
- [ ] Ingestion Failure Rate \u003c 1% (Saga Pattern 적용 후)
- [ ] Rollback Success Rate 100%

---

## 🛠️ 프로세스 개선 (Constitution/Agent.md 업데이트)

### 1. Prompt Quality Standard 추가
```markdown
# constitution.md: Prompt Engineering Law

## Prompt Quality Requirements
1. **Test Coverage**: 모든 프롬프트는 최소 20개 테스트 케이스로 검증되어야 함
2. **Versioning**: 프롬프트 변경 시 v1, v2 등 버전 관리 필수
3. **No Hard-coded Examples**: 특정 예시에 과도하게 의존 금지
4. **Metric-based**: Before/After 성능 비교 데이터 제시
```

### 2. Research Spec 카테고리 추가
```markdown
# agent.md: Research Spec Protocol

## Research Spec (실험 및 POC)
Production 배포가 목적이 아닌, "적용 여부 결정"을 위한 실험 Spec.

### Definition of Done
- ❌ Production Code 배포 불필요
- ✅ Trade-off 측정 데이터 확보
- ✅ "Go/No-Go" 의사결정 근거 제시

### Example: Spec 072 - Semantic Chunking POC
- Goal: Semantic Chunking의 비용 vs 품질 측정
- Tasks:
  - [ ] 10개 샘플 문서로 비교 실험
  - [ ] Metric: Chunk Quality, API Cost, Latency
  - [ ] 리포트 작성 → 사용자 의사결정
```

---

## ✅ Next Steps: User Decision Required

### 즉시 착수 가능한 Quick Wins
1. **Reranker 독소조항 제거** (1일)
2. **Prompt Test Dataset 구축** (2일)
3. **ChromaDB Upsert** (1일)

### 의사결정 필요한 Major Tasks
1. **Deduplication Service**: 어떤 Strategy를 우선 구현할지?  
   → 추천: ID Checking (YouTube) + Contents Hash (General Web)
   
2. **Saga Pattern**: Transaction Guarantee가 필수인지?  
   → 추천: 우선순위 낮춤, Quick Wins 먼저 처리 후 재검토
   
3. **Clean Architecture Refactoring**: 언제 시작할지?  
   → 추천: Phase 2 완료 후 (2~3주 후)

### 리뷰 요청 사항
- [ ] 우선순위 동의 여부 (P0 → P1 → P2 순서)
- [ ] Quick Wins 3개 Task 승인
- [ ] Constitution/Agent.md 프로세스 개선 승인
