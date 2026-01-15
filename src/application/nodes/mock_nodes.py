from typing import List
from src.domain.state import GraphState
from src.domain.models.source import Source, Chunk

def fetch_source_node(state: GraphState) -> GraphState:
    """
    [MOCK] URL 목록에서 Source 객체를 생성하는 더미 노드.
    실제 크롤링 대신 더미 콘텐츠를 채웁니다.
    """
    urls = state.get("urls", [])
    sources = state.get("sources", [])
    
    new_sources = []
    for url in urls:
        # 이미 처리된 URL은 건너뛰는 로직이 있을 수 있지만, 여기선 단순 추가
        source = Source(
            url=url,
            title="Dummy Title",
            raw_content=f"This is dummy content for {url}"
        )
        new_sources.append(source)
    
    return {
        "sources": sources + new_sources,
        "status": "fetched"
    }

def extract_content_node(state: GraphState) -> GraphState:
    """
    [MOCK] Source 객체에서 Chunk를 생성하는 더미 노드.
    """
    sources = state.get("sources", [])
    
    for source in sources:
        if not source.chunks:
            # 더미 청킹 로직
            chunk1 = Chunk(content=f"Chunk 1 from {source.raw_content}", metadata={"index": 0})
            chunk2 = Chunk(content=f"Chunk 2 from {source.raw_content}", metadata={"index": 1})
            source.chunks = [chunk1, chunk2]
            
    return {
        "sources": sources,
        "status": "extracted"
    }
