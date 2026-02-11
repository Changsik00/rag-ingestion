"""
Intent Classifier Quality Test

Purpose:
    YAML 기반 50개 테스트 케이스로 Intent Classifier의 품질을 자동 검증합니다.

Test Strategy:
    - Parametrized Test: 각 케이스를 개별적으로 실행하여 실패 추적 용이
    - Fuzzy Match: Targets는 포함 관계로 검증 (expected ⊆ actual)
    - Accuracy 계산: 전체 테스트 실행 후 메트릭 출력

Usage:
    # 전체 테스트 실행
    uv run pytest tests/prompt/test_intent_classifier_quality.py -v

    # 특정 카테고리만 테스트
    uv run pytest tests/prompt/test_intent_classifier_quality.py -v -k "general_query"

    # 실패 케이스만 재실행
    uv run pytest tests/prompt/test_intent_classifier_quality.py --lf
"""

from pathlib import Path

import pytest
import yaml

from app.domain.interfaces.llm import LLMInterface
from app.domain.services.intent_classifier import IntentClassifier
from app.infrastructure.factories.llm_factory import LLMFactory

# Load Test Cases
TEST_CASES_PATH = Path(__file__).parent / "intent_test_cases.yaml"
with open(TEST_CASES_PATH) as f:
    data = yaml.safe_load(f)
    TEST_CASES = data["test_cases"]


# Fixture: LLM Interface (Temperature=0 for reproducibility)
@pytest.fixture(scope="module")
def llm() -> LLMInterface:
    """Intent Classifier 테스트용 LLM Interface (Temperature 0)"""
    return LLMFactory.get_llm_adapter(temperature=0.0)


# Fixture: Intent Classifier
@pytest.fixture(scope="module")
def intent_classifier(llm: LLMInterface) -> IntentClassifier:
    """Intent Classifier Instance"""
    return IntentClassifier(llm=llm)


# Parametrized Test: 50 Cases
@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda tc: f"{tc['id']}_{tc['category']}")
async def test_intent_classification_accuracy(test_case: dict, intent_classifier: IntentClassifier):
    """
    Intent Classifier 품질 테스트 (50개 케이스)

    Given: 테스트 질문 및 예상 결과
    When: Intent Classifier 실행
    Then: Intent Type과 Targets가 예상과 일치

    Args:
        test_case: YAML 테스트 케이스 (id, query, expected_intent, expected_targets)
        intent_classifier: IntentClassifier 인스턴스
    """
    # Given
    test_id = test_case["id"]
    query = test_case["query"]
    expected_intent = test_case["expected_intent"]
    expected_targets = set(test_case["expected_targets"])

    # When
    result = await intent_classifier.classify(query, history=[])

    # Then: Intent Type 검증 (다중 정답 허용 로직)
    if isinstance(expected_intent, list):
        assert result.intent.value in expected_intent, (
            f"[{test_id}] Intent mismatch for query: '{query}'\n"
            f"Expected one of: {expected_intent}\n"
            f"Got: {result.intent.value}\n"
            f"Reasoning: {result.reasoning}"
        )
    else:
        assert result.intent.value == expected_intent, (
            f"[{test_id}] Intent mismatch for query: '{query}'\n"
            f"Expected: {expected_intent}\n"
            f"Got: {result.intent.value}\n"
            f"Reasoning: {result.reasoning}"
        )

    # Then: Targets 검증 (Fuzzy Match - 각 expected target이 actual target 중 하나와 부분 일치하면 통과)
    result_targets = set([t.lower() for t in result.targets])  # 대소문자 무시
    expected_targets_lower = set([t.lower() for t in expected_targets])

    # Edge Case: expected_targets가 비어있으면 검증 스킵
    if expected_targets:
        missing_targets = []
        for expected in expected_targets_lower:
            found = False
            for actual in result_targets:
                # Substring matching (e.g., 'embedding' matches 'embedding model')
                if expected in actual or actual in expected:
                    found = True
                    break
            if not found:
                missing_targets.append(expected)

        assert not missing_targets, (
            f"[{test_id}] Targets mismatch for query: '{query}'\n"
            f"Expected (at least one matching for each): {expected_targets}\n"
            f"Got: {result.targets}\n"
            f"Missing (no fuzzy match found for these): {missing_targets}\n"
            f"Reasoning: {result.reasoning}"
        )


# Test Summary Hook (pytest plugin)
def pytest_sessionfinish(session, exitstatus):
    """
    전체 테스트 실행 후 Accuracy 계산 및 출력
    """
    # Collect test results
    total = 0
    passed = 0
    failed_cases = []

    for item in session.items:
        if "test_intent_classification_accuracy" in item.nodeid:
            total += 1

            # Check if test passed
            if item.nodeid in session.testsfailed:
                failed_cases.append(item.callspec.params["test_case"]["id"])
            else:
                passed += 1

    if total > 0:
        accuracy = (passed / total) * 100

        print("\n" + "=" * 60)
        print("📊 Intent Classification Quality Test Summary")
        print("=" * 60)
        print(f"Total Test Cases: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Accuracy: {accuracy:.1f}%")

        if failed_cases:
            print(f"\nFailed Cases: {', '.join(failed_cases)}")

        # Threshold Check
        accuracy_threshold = 80.0
        if accuracy < accuracy_threshold:
            print(f"\n⚠️  WARNING: Accuracy ({accuracy:.1f}%) is below threshold ({accuracy_threshold}%)")
        else:
            print(f"\n✅ SUCCESS: Accuracy ({accuracy:.1f}%) meets threshold ({accuracy_threshold}%)")

        print("=" * 60 + "\n")
