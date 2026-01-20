from app.domain.ingestion.state import StrategyType, ValidationConstraints, ValidationFeedback
from app.infrastructure.brain.logic import select_strategy
from app.infrastructure.brain.nodes import construct_extraction_prompt

# BDD Style Integration Test using Logic & Prompt Units
# NOTE: Complete Graph integration with Mock LLM is complex,
# so we simulate the "Loop Logic" here to verify the Architectural Flow.


class TestLogicResolverScenarios:
    def test_should_trigger_correction_strategy_on_partial_failure(self):
        """
        Scenario 1: Partial Retry (Level 2 Reasoning Retry)
        Given: Validator fails due to missing 'title'
        When: Logic Resolver is called
        Then:
            1. Strategy becomes CORRECTION
            2. Prompt contains 'TARGET FIELDS: title'
        """
        # Given
        retry_count = 0
        feedbacks = [ValidationFeedback(source="validator", message="Title is missing", target_fields=["title"])]

        # When
        next_strategy = select_strategy(retry_count, feedbacks)
        prompt = construct_extraction_prompt(
            strategy=next_strategy, feedback=feedbacks[-1], constraints=ValidationConstraints()
        )

        # Then
        assert next_strategy == StrategyType.CORRECTION
        assert "CRITICAL FEEDBACK" in prompt
        assert "TARGET FIELDS: ['title']" in prompt  # Partial Retry Trigger

    def test_should_trigger_relaxation_strategy_on_repeated_failure(self):
        """
        Scenario 2: Constraint Relaxation (Level 3 Backtracking)
        Given: Validator fails repeatedly (2+ times) on 'entities'
        When: Logic Resolver is called
        Then:
            1. Strategy becomes RELAXATION
            2. Prompt contains 'RELAXATION MODE'
        """
        # Given
        retry_count = 2
        feedbacks = [
            ValidationFeedback(source="validator", message="Too many entities"),
            ValidationFeedback(source="validator", message="Too many entities"),
        ]

        # When
        next_strategy = select_strategy(retry_count, feedbacks)
        prompt = construct_extraction_prompt(
            strategy=next_strategy, feedback=feedbacks[-1], constraints=ValidationConstraints()
        )

        # Then
        assert next_strategy == StrategyType.RELAXATION
        assert "RELAXATION MODE: Enabled" in prompt
        assert "be less strict" in prompt

    def test_should_maintain_standard_strategy_if_no_feedback(self):
        """
        Scenario 3: No Feedback provided (Edge Case)
        Given: No feedback from validator
        When: Logic Resolver is called
        Then: Strategy remains STANDARD (Fallback)
        """
        # Given
        retry_count = 1
        feedbacks = []

        # When
        next_strategy = select_strategy(retry_count, feedbacks)

        # Then
        assert next_strategy == StrategyType.STANDARD

    def test_should_suggest_relaxation_on_max_retry(self):
        """
        Scenario 4: Max Retries Exceeded Logic Check
        Given: Retry count reached Max (3)
        When: Logic Router is called
        Then: Strategy is RELAXATION (Logic layer logic)
        Note: Actual Graph loop termination is handled by Conditional Edge,
        but Logic Resolver should still provide valid strategy.
        """
        # Given
        retry_count = 3
        feedbacks = [ValidationFeedback(source="validator", message="Error")]

        # When
        next_strategy = select_strategy(retry_count, feedbacks)

        # Then
        assert next_strategy == StrategyType.RELAXATION
