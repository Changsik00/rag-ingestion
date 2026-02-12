# 리팩토링 제안: 지능형 자산 공유 및 3-Layer 정제 (Spec 076)

## 1. 개요
최근 수행한 RAG 3계층 리팩토링(Spec 075)의 성과를 바탕으로, 시스템 전체의 일관성을 확보하고 `Ingest`와 `Chat`이 공통의 지능적 역량을 효율적으로 공유할 수 있도록 구조를 정제합니다. 기존에 확립된 **Brain, Retrieval, Orchestration** 용어를 유지하면서 클린 아키텍처의 원칙을 더 엄격히 적용합니다.

---

## 2. 핵심 원칙
1. **용어 유지 및 확장**: 기존의 3-Layer 용어(`Brain`, `Retrieval`, `Orchestration`)를 그대로 사용하되, 특정 기능(RAG)에 국한되지 않는 범용적 역량으로 확장합니다.
2. **지능형 자산의 중앙화**: `Ingest`와 `Chat`이 각각 LLM 로직을 구현하지 않고, 공통의 `Brain`과 `Retrieval` 서비스를 사용합니다.
3. **폴더 구조 정비**: `rag/`라는 중간 폴더를 제거하고, 역량(Brain, Retrieval)과 유즈케이스(Chat, Ingest)를 최상위 계층에서 관리합니다.

---

## 3. 용어 및 계층 정의 (Ubiquitous Language)

| 용어 | 역할 | 위치 |
| :--- | :--- | :--- |
| **Brain** | 판단, 분류, 재작성, 생성 등 LLM 기반의 핵심 추론 역량 | `domain/brain`, `infrastructure/brain` |
| **Retrieval** | 벡터, 키워드, 그래프 등 지식을 찾아내는 역량 | `domain/retrieval`, `infrastructure/retrieval` |
| **Orchestration** | 특정 목적(Chat, Ingest)을 위해 각 역량을 조합하는 흐름 | `application/chat`, `application/ingest` |

---

## 4. 제안하는 구조 (Proposed Directory Structure)

```text
app/
├── domain/                  # 핵심 인터페이스 및 데이터 모델
│   ├── brain/               # Brain 관련 인터페이스
│   └── retrieval/           # Retrieval 관련 인터페이스
├── application/             # 유즈케이스 조율 (Orchestration)
│   └── orchestration/       # 3-Layer 중 Orchestration 계층
│       ├── chat/            # 대화형 질문/답변 흐름
│       └── ingest/           # 데이터 가공/입고 흐름
└── infrastructure/          # 구체적 구현부
    ├── brain/               # 실제 프롬프트 및 LLM 호출
    ├── retrieval/           # DB별 검색 구현
    └── ai/                  # LangGraph 워크플로우 정의
```

---

## 5. 실행 계획 (Roadmap)

### Phase 1: 기반 구조 공용화
- [ ] `app/domain/brain` 및 `app/domain/retrieval`로 인터페이스 추출
- [ ] 프롬프트와 구체적인 구현 로직을 `infrastructure/brain`으로 이동
- [ ] `rag/` 폴더에 종속된 명칭들을 범용적인 명칭으로 리네이밍

### Phase 2: Orchestration 독립 및 강화
- [ ] `app/application/orchestration/chat`을 독립적 유즈케이스로 정립
- [ ] `app/application/orchestration/ingest` 흐름 재정의 및 통합
- [ ] LangGraph 의존성을 `infrastructure/ai`로 격리하여 흐름 제어와 기능 호출을 분리

### Phase 3: Ingest 통합
- [ ] 현재 `Ingest`에서 사용하는 LLM 로직을 공용 `Brain` 역량으로 전환
- [ ] `Ingest`와 `Chat`이 동일한 `Retrieval` 인프라를 사용하도록 통합

---

## 6. 기대 효과
- **일관성**: 프로젝트 전반에서 동일한 3-Layer 언어를 사용하여 소통이 원활해집니다.
- **재사용성**: 새로운 AI 기능 개발 시 기존의 Brain/Retrieval 자산을 즉시 활용할 수 있습니다.
- **유연성**: 외부 라이브러리(LangGraph 등)의 변경이 비즈니스 로직에 미치는 영향을 최소화합니다.
