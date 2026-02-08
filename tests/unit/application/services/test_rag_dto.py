from app.application.services.rag import RAGResult


def test_rag_result_contains_rerank_log():
    """Test that RAGResult can hold rerank_log information."""
    # Given
    answer = "Hello"
    rerank_log = [
        {"id": "chunk1", "score": 0.9, "status": "passed"},
        {"id": "chunk2", "score": 0.4, "status": "dropped"},
    ]

    # When
    result = RAGResult(
        answer=answer,
        rewritten_query="Hi",
        vector_chunks=[],
        keyword_chunks=[],
        graph_data=[],
        full_context="",
        rerank_log=rerank_log,  # This should fail if the field doesn't exist
    )

    # Then
    assert result.answer == answer
    assert result.rerank_log == rerank_log
