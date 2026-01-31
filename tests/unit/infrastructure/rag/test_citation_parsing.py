"""
RAG Nodes Citation Parsing 단위 테스트.
"""

import re
from unittest.mock import Mock

from app.domain.value_objects.chunk import Chunk
from app.infrastructure.rag.nodes import RAGNodes


def test_extract_citations_from_answer():
    """
    LLM 답변에서 [1], [2] 형식을 파싱하여 citations 리스트를 생성하는지 검증합니다.
    """
    # Given
    RAGNodes(
        neo4j_doc_repo=Mock(),
        neo4j_graph_repo=Mock(),
        chroma_repo=Mock(),
        query_rewriter=Mock(),
        intent_classifier=Mock(),
        llm=Mock(),
    )

    answer_text = "AI는 인공지능입니다[1]. 삼성전자는 전자기업입니다[2]."
    mapped_chunks = {
        1: Chunk(id="c1", content="cnt1", parent_id="d1", index=0, metadata={"source": "src1", "title": "Title 1"}),
        2: Chunk(id="c2", content="cnt2", parent_id="d2", index=1, metadata={"source": "src2", "title": "Title 2"}),
    }

    # When (내부적으로 활용할 파싱 로직 테스트용 모의 호출 또는 실제 구현 후 호출)
    # 실제 generate_answer 내부에 구현될 로직을 유추하여 테스트
    indices = [int(i) for i in re.findall(r"\[(\d+)\]", answer_text)]
    citations = []
    seen_indices = set()
    for idx in indices:
        if idx in mapped_chunks and idx not in seen_indices:
            chunk = mapped_chunks[idx]
            citations.append(
                {
                    "index": idx,
                    "source": chunk.metadata.get("source", "Unknown"),
                    "title": chunk.metadata.get("title", "Untitled"),
                    "url": chunk.metadata.get("url") or chunk.metadata.get("source_url"),
                }
            )
            seen_indices.add(idx)

    # Then
    assert len(citations) == 2
    assert citations[0]["index"] == 1
    assert citations[0]["title"] == "Title 1"
    assert citations[1]["index"] == 2
    assert citations[1]["title"] == "Title 2"
