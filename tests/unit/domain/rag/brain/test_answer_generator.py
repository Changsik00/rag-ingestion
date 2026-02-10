import pytest
import logging
from unittest.mock import AsyncMock, MagicMock
from app.domain.rag.brain.answer_generator import AnswerGenerator
from app.domain.value_objects.chunk import Chunk

@pytest.fixture
def mock_llm():
    return MagicMock()

@pytest.fixture
def generator(mock_llm):
    return AnswerGenerator(mock_llm)

@pytest.mark.asyncio
async def test_generate_answer(generator, mock_llm):
    # Setup
    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = MagicMock(content="This is a test answer [1].")
    mock_llm.bind.return_value = mock_runnable
    
    # Execute
    answer = await generator.generate_answer(
        query="query",
        rewritten_query="rewritten",
        context_str="context",
        config={},
        temperature=0.0
    )
    
    # Verify
    assert "This is a test answer" in answer
    mock_llm.bind.assert_called_with(temperature=0.0)

def test_format_and_parse_citation(generator):
    chunk1 = Chunk(
        id="1", 
        content="Text1", 
        parent_id="d1", 
        index=0, 
        metadata={"source": "s1", "title": "t1"}
    )
    chunk2 = Chunk(
        id="2", 
        content="Text2", 
        parent_id="d2", 
        index=0, 
        metadata={"source": "s2", "title": "t2"} 
    )
    graph_data = [{"source": "s1", "relationship": "REL", "target": "s2"}]
    
    # 1. Format Context
    context, mapped = generator.format_context([chunk1], [chunk2], graph_data)
    
    # Verify Formatting
    assert "Graph Facts:" in context
    assert "- (s1) -[REL]-> (s2)" in context
    assert "Document Context:" in context
    assert "[1] Source: s1" in context
    assert "[2] Source: s2" in context
    assert len(mapped) == 2
    
    # 2. Parse Citation
    answer_text = "Analysis based on [1] and some [2]."
    citations = generator.parse_citations(answer_text, mapped)
    
    # Verify Citations
    assert len(citations) == 2
    assert citations[0]["index"] == 1
    assert citations[0]["source"] == "s1"
    assert citations[1]["index"] == 2
    assert citations[1]["source"] == "s2"
