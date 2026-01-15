import pytest
from src.application.workflow import create_workflow

def test_full_pipeline_execution():
    """전체 파이프라인(Workflow)이 에러 없이 실행되고 결과 상태가 예상대로인지 통합 검증"""
    # Given
    app = create_workflow()
    input_urls = ["https://integration-test.com/1", "https://integration-test.com/2"]
    
    # When
    result = app.invoke({"urls": input_urls})
    
    # Then
    # 1. 상태 확인
    assert result["status"] == "extracted"
    
    # 2. Source 객체 개수 확인 (2개 URL -> 2개 Source)
    assert len(result["sources"]) == 2
    
    # 3. 각 Source가 Chunk를 가지고 있는지 확인
    for source in result["sources"]:
        assert source.chunks is not None
        assert len(source.chunks) > 0
        assert "dummy content" in source.raw_content
