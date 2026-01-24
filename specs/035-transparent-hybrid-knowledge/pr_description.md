# feat(spec-035): Transparent Hybrid Knowledge Strategy

## 📋 Summary
기존 RAG 시스템은 정보가 부족하거나 검색 필터가 너무 엄격할 경우 "답변할 수 없습니다"라고 응답하여 사용성을 저해했습니다. 

이번 PR에서는 **"Sparse but Powerful"** 전략을 도입하여 이 문제를 해결합니다. 
- **DB(Context) 정보 우선**: 단 한 줄의 데이터라도 DB에 있다면 이를 답변의 핵심 근거로 삼고 인라인 출처(`[n]`)를 표기합니다. 
- **AI 일반 지식 보강**: DB 정보가 빈약할 경우 AI의 자체 지식으로 맥락을 보강하여 풍부한 답변을 완성하되, 출처 표기를 생략하여 신뢰의 경계를 명확히 합니다.
- **투명한 출처 노출**: 모든 답변 하단에 클릭 가능한 참조 문헌(References) 리스트를 제공하여 사용자가 팩트 체크를 즉시 수행할 수 있도록 합니다.

## 🎯 Key Review Points
1. **Hybrid Knowledge Mixing**: `nodes.py`의 시스템 프롬프트가 DB 컨텍스트를 절대적으로 우선시하면서도 자연스럽게 일반 지식과 섞이도록 설계되었습니다.
2. **Granular Citation Parsing**: 답변 내 `[1]` 등의 인덱스를 regex로 추출하여 `citations` 상태에 실제 문서 제목과 URL을 매핑하는 로직이 정확하게 동작합니다.
3. **Transparent UI**: Playground 하단에 출처별 클릭 가능한 링크 리스트를 제공하여 지식의 경계를 명확히 했습니다.

## 🧪 Verification
### Automated Tests
```bash
# Unit Tests (State schema & Citation parsing)
uv run pytest tests/unit/domain/rag/test_state.py
uv run pytest tests/unit/infrastructure/rag/test_citation_parsing.py

# Integration Tests (Hybrid Reasoning BDD Scenarios)
uv run pytest tests/integration/bdd/test_hybrid_knowledge.py
```

### Manual Verification (Admin Playground 가이드)
**[페이지 이동]**: `Admin App` > `🎮 RAG Playground`

#### 시나리오 1: Full RAG (데이터 충분)
1. **준비**: 특정 주제(예: '삼성 S24')에 대한 문서를 수집합니다.
2. **질문**: "삼성 S24의 사양은?"
3. **확인**: 답변의 거의 모든 문장에 `[1]`, `[2]`와 같은 번호가 붙고, 하단 Reference 섹션에 문서 링크가 나타나는지 확인합니다.

#### 시나리오 2: Hybrid Mixed (일부 데이터 존재)
1. **준비**: 삼성 정보만 있고 애플 정보는 없는 상태를 만듭니다.
2. **질문**: "삼성과 애플의 대표 모델을 비교해줘."
3. **확인**: 
   - 삼성 설명 문장 끝에는 `[1]`이 붙습니다. 
   - 애플 설명 문장에는 번호가 붙지 않으며, AI의 지식으로 자연스럽게 설명되는지 확인합니다.
   - 하단 캡션에 "번호가 없는 문장은 AI 일반 지식"임이 안내되는지 확인합니다.

#### 시나리오 3: Global Fallback (데이터 전무)
1. **준비**: 시스템에 전혀 없는 엉뚱한 주제를 상정합니다.
2. **질문**: "2025년 화성 이주 계획에 대해 알려줘."
3. **확인**: 
   - "지식 베이스에 관련 정보가 없어 일반 지식을 바탕으로 답한다"는 안내가 상단에 표시됩니다.
   - 답변에 인라인 번호가 전혀 없으며 Reference 섹션이 나타나지 않는지 확인합니다.

## 📦 Files Changed

### 🆕 New Files
- `docs/design_guides/006-hybrid-knowledge-mixing.md`: "Sparse but Powerful" 설계 전략 문서.
- `tests/unit/domain/rag/test_state.py`: State 필드 추가 검증 테스트.
- `tests/unit/infrastructure/rag/test_citation_parsing.py`: Citation 파싱 로직 테스트.
- `tests/integration/bdd/test_hybrid_knowledge.py`: 3개 BDD 시나리오 통합 테스트.

### 🛠 Modified Files
- `app/domain/rag/state.py` (+3, -0): `citations` 필드 추가.
- `app/domain/services/rag_service.py` (+3, -0): Citation 메타데이터 전달 로직 추가.
- `app/infrastructure/rag/nodes.py` (+30, -9): 하이브리드 프롬프트 및 파싱 로직 구현.
- `app/admin/pages/4_RAG_Playground.py` (+25, -0): 참조 문헌 섹션 UI 구현.

**Total:** 8 files changed

## ✅ Definition of Done
- [x] "Sparse but Powerful" 전략 문서화 완료
- [x] Hybrid Reasoning & Citation 파싱 로직 구현 완료
- [x] Admin UI 참조 문헌 리스트 렌더링 완료
- [x] 3개 BDD 시나리오 테스트 통과
- [x] PR Description 작성 완료
