# feat(spec-035): Transparent Hybrid Knowledge Strategy

## 📋 Summary
기존의 "Strict RAG" 방식이 검색 결과 부재 시 답변을 거절하는 문제를 해결하기 위해, DB의 '검증된 팩트'와 LLM의 '일반 지식'을 조화롭게 융합하는 **Transparent Hybrid Knowledge Strategy**를 구현했습니다. "Sparse but Powerful" 철학을 적용하여 데이터가 적더라도 확실한 근거가 있다면 이를 답변의 핵심으로 삼고, 부족한 맥락은 AI 지식으로 보강하되 출처를 투명하게 표기합니다.

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

### Manual Verification
- Playground에서 "일론 머스크와 스티브 잡스 비교" 질문 시, DB에 있는 정보에는 `[1]`이 붙고 없는 설명에는 번호가 붙지 않음을 확인.
- 하단 Reference 리스트의 링크를 클릭하여 원본 소스로 이동 가능함을 확인.

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
