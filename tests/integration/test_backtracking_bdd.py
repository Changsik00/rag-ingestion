
from app.domain.ingestion.state import Attempt, IngestionState, StrategyType, ValidationConstraints, ValidationFeedback
from app.infrastructure.brain.logic import select_strategy
from app.infrastructure.brain.nodes import construct_extraction_prompt

# BDD Style Integration Test using Logic & Prompt Units
# NOTE: Complete Graph integration with Mock LLM is complex,
# so we simulate the "Loop Logic" here to verify the Architectural Flow.

class TestBacktrackingScenarios:

    def test_scenario_1_partial_retry_flow(self):
        """
        Scenario 1: Partial Retry (Level 2 Reasoning Retry)
        Given: Validator fails due to missing 'title'
        When: Logic Resolver is called
        Then:
            1. Strategy becomes CORRECTION
            2. Prompt contains 'TARGET FIELDS: title'
        """
        # Given
        current_state: IngestionState = {
            "retry_count": 0,
            "current_strategy": StrategyType.STANDARD,
            "attempt_history": [],
            "last_feedback": None,
            "max_retries": 3,
            "error": None,
            "steps_history": [],
            "original_url": "",
            "raw_content": "",
            "metadata": None,
            "active_constraints": ValidationConstraints(),
            "predicted_category": None
        }

        # Validator Fails
        feedback = ValidationFeedback(
            source="validator",
            message="Title is missing",
            target_fields=["title"]
        )

        # When: Logic Step
        next_strategy = select_strategy(
            retry_count=current_state["retry_count"],
            feedbacks=[feedback]
        )

        # Then: Check Strategy
        assert next_strategy == StrategyType.CORRECTION

        # When: Extractor Step (Prompt Construction)
        prompt = construct_extraction_prompt(
            strategy=next_strategy,
            feedback=feedback,
            constraints=current_state["active_constraints"]
        )

        # Then: Check Prompt
        assert "CRITICAL FEEDBACK" in prompt
        assert "Title is missing" in prompt
        assert "TARGET FIELDS: ['title']" in prompt # Partial Retry Trigger

    def test_scenario_2_relaxation_flow(self):
        """
        Scenario 2: Constraint Relaxation (Level 3 Backtracking)
        Given: Validator fails repeatedly (2+ times) on 'entities'
        When: Logic Resolver is called
        Then:
            1. Strategy becomes RELAXATION
            2. Prompt contains 'RELAXATION MODE'
        """
        # Given
        current_state: IngestionState = {
            "retry_count": 2, # Critical Threshold
            "current_strategy": StrategyType.CORRECTION,
            "attempt_history": [
                Attempt(attempt_number=1, strategy=StrategyType.STANDARD),
                Attempt(attempt_number=2, strategy=StrategyType.CORRECTION)
            ],
            "last_feedback": None,
            # ... other fields ignored for logic test
        }

        feedbacks = [
            ValidationFeedback(source="validator", message="Too many entities"),
            ValidationFeedback(source="validator", message="Too many entities")
        ]

        # When: Logic Step
        next_strategy = select_strategy(
            retry_count=current_state["retry_count"],
            feedbacks=feedbacks
        )

        # Then: Check Strategy Switch
        assert next_strategy == StrategyType.RELAXATION

        # When: Extractor Step
        prompt = construct_extraction_prompt(
            strategy=next_strategy,
            feedback=feedbacks[-1],
            constraints=ValidationConstraints()
        )

        # Then: Check Prompt
        assert "RELAXATION MODE: Enabled" in prompt
        assert "be less strict" in prompt
