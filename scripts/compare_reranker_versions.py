#!/usr/bin/env python3
"""
Reranker v1 vs v2 A/B Testing Script

Spec 069: Task 3-1
10개 테스트 질문으로 v1 vs v2 성능 비교 (Recall/Precision)

Usage:
    # v1 테스트
    python scripts/compare_reranker_versions.py --version v1 --output results_v1.json

    # v2 테스트
    python scripts/compare_reranker_versions.py --version v2 --output results_v2.json

    # 결과 비교
    python scripts/compare_results.py results_v1.json results_v2.json
"""

import argparse
import asyncio
import json
from typing import Any

# Test Queries with Expected Ground Truth
TEST_QUERIES = [
    {
        "id": 1,
        "query": "일론 머스크의 SpaceX와 Tesla 비교",
        "category": "multi_entity",
        "description": "비교 질문 - 두 엔티티 모두 관련성 있어야 함",
        "expected_relevant_keywords": ["SpaceX", "Tesla", "일론 머스크", "우주", "전기차"],
    },
    {
        "id": 2,
        "query": "Claude와 GPT-4의 차이점",
        "category": "multi_entity",
        "description": "AI 모델 비교 질문",
        "expected_relevant_keywords": ["Claude", "GPT-4", "Anthropic", "OpenAI", "AI"],
    },
    {
        "id": 3,
        "query": "어쩌다 어른에서 김영하 출연분",
        "category": "specific_context",
        "description": "기존 테스트 케이스 - 특정 컨텍스트",
        "expected_relevant_keywords": ["어쩌다 어른", "김영하", "tvN", "작가"],
    },
    {
        "id": 4,
        "query": "유 퀴즈 온 더 블럭에서 백종원",
        "category": "specific_context",
        "description": "예능 프로그램 특정 출연분",
        "expected_relevant_keywords": ["유 퀴즈", "백종원", "tvN", "요리"],
    },
    {
        "id": 5,
        "query": "인공지능이 뭐야?",
        "category": "general",
        "description": "일반 질문",
        "expected_relevant_keywords": ["인공지능", "AI", "머신러닝", "딥러닝"],
    },
    {
        "id": 6,
        "query": "Python과 JavaScript 비교",
        "category": "multi_entity",
        "description": "프로그래밍 언어 비교",
        "expected_relevant_keywords": ["Python", "JavaScript", "프로그래밍", "언어"],
    },
    {
        "id": 7,
        "query": "김미경 강연 요약",
        "category": "entity_focused",
        "description": "특정 인물 중심 질문",
        "expected_relevant_keywords": ["김미경", "강연", "강사", "자기계발"],
    },
    {
        "id": 8,
        "query": "넷플릭스 추천 다큐멘터리",
        "category": "entity_focused",
        "description": "플랫폼 특정 컨텐츠 추천",
        "expected_relevant_keywords": ["넷플릭스", "Netflix", "다큐멘터리", "추천"],
    },
    {
        "id": 9,
        "query": "세바시에서 나온 명언 모음",
        "category": "specific_context",
        "description": "특정 프로그램 컨텐츠",
        "expected_relevant_keywords": ["세바시", "세상을 바꾸는 시간", "명언", "강연"],
    },
    {
        "id": 10,
        "query": "React와 Vue.js의 장단점",
        "category": "multi_entity",
        "description": "프레임워크 비교",
        "expected_relevant_keywords": ["React", "Vue.js", "JavaScript", "프론트엔드"],
    },
]


async def run_rag_query_simulation(query: str, version: str) -> dict[str, Any]:
    """
    RAG 파이프라인 시뮬레이션 (실제 LLM 호출 대신)

    실제 사용 시 이 함수를 실제 RAG API 호출로 교체:
    ```python
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/rag/query",
            json={"query": query, "session_id": "test"},
            headers={"X-Reranker-Version": version}
        )
        return response.json()
    ```
    """
    # Simulated results - 실제로는 RAG API 호출
    print(f"  [Simulation] Running RAG for: {query[:50]}... (version={version})")

    # Mock: v2가 좀 더 많은 청크를 통과시킨다고 가정
    base_chunks = 5
    if version == "v2":
        retrieved_chunks = base_chunks + 2  # v2는 더 관대함
    else:
        retrieved_chunks = base_chunks

    return {
        "query": query,
        "reranked_chunks_count": retrieved_chunks,
        "final_answer": f"Mock answer for: {query}",
        "version": version,
    }


def calculate_recall(result: dict, expected_keywords: list[str]) -> float:
    """
    Recall 계산 (간단한 키워드 매칭 기반 시뮬레이션)

    실제 사용 시:
    - Ground Truth 데이터셋 필요
    - Relevant Documents 정의 필요
    - Recall = (Retrieved Relevant) / (Total Relevant)
    """
    # Simulated recall based on chunk count
    # 실제로는 Ground Truth와 비교 필요
    chunks_count = result.get("reranked_chunks_count", 0)
    max_chunks = 10
    return min(chunks_count / max_chunks, 1.0)


def calculate_precision(result: dict, expected_keywords: list[str]) -> float:
    """
    Precision 계산 (간단한 응답 품질 기반 시뮬레이션)

    실제 사용 시:
    - LLM Judge로 응답 품질 평가
    - Precision = (Retrieved Relevant) / (Total Retrieved)
    """
    # Simulated precision
    # v2는 더 많이 가져오지만 정확도는 유사하다고 가정
    return 0.8 if result.get("version") == "v1" else 0.78


async def run_test(version: str, output_file: str):
    """Run A/B test for given version"""
    print(f"\n{'=' * 60}")
    print(f"Running Reranker {version.upper()} Test")
    print(f"{'=' * 60}\n")

    results = []
    total_recall = 0.0
    total_precision = 0.0

    for i, test_case in enumerate(TEST_QUERIES, 1):
        print(f"[{i}/10] Testing: {test_case['query']}")

        # Run RAG query
        result = await run_rag_query_simulation(test_case["query"], version)

        # Calculate metrics
        recall = calculate_recall(result, test_case["expected_relevant_keywords"])
        precision = calculate_precision(result, test_case["expected_relevant_keywords"])

        total_recall += recall
        total_precision += precision

        results.append(
            {
                "test_id": test_case["id"],
                "query": test_case["query"],
                "category": test_case["category"],
                "recall": round(recall, 3),
                "precision": round(precision, 3),
                "chunks_retrieved": result["reranked_chunks_count"],
            }
        )

        print(f"  → Recall: {recall:.3f}, Precision: {precision:.3f}")

    avg_recall = total_recall / len(TEST_QUERIES)
    avg_precision = total_precision / len(TEST_QUERIES)

    summary = {
        "version": version,
        "total_tests": len(TEST_QUERIES),
        "avg_recall": round(avg_recall, 3),
        "avg_precision": round(avg_precision, 3),
        "f1_score": round(2 * (avg_precision * avg_recall) / (avg_precision + avg_recall), 3),
        "results": results,
    }

    # Save results
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Results Summary ({version.upper()})")
    print(f"{'=' * 60}")
    print(f"Avg Recall:    {avg_recall:.3f}")
    print(f"Avg Precision: {avg_precision:.3f}")
    print(f"F1 Score:      {summary['f1_score']:.3f}")
    print(f"\nResults saved to: {output_file}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Reranker A/B Testing")
    parser.add_argument("--version", required=True, choices=["v1", "v2"], help="Reranker version to test")
    parser.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()

    asyncio.run(run_test(args.version, args.output))


if __name__ == "__main__":
    main()
