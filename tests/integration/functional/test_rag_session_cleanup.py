import uuid

import pytest


@pytest.mark.asyncio
async def test_session_creation_and_cleanup(api_client):
    """
    Test flow:
    1. Create a session by asking a question.
    2. Verify checkpoints exist in DB.
    3. Call reset endpoint.
    4. Verify checkpoints are deleted.
    """
    # 0. Setup
    thread_id = f"test-cleanup-{uuid.uuid4()}"
    payload = {
        "message": "Hello, this is a cleanup test.",
        "filters": {},
        "hitl_enabled": False,
        "advanced_settings": {
            "top_k": 3,
            "temperature": 0.5,
            "search_strategy": "vector"
        }
    }

    # 1. Create Session (Ask)
    response = api_client.post(f"/v1/rag/sessions/{thread_id}/ask", json=payload)
    # 202 or 200 acceptable
    assert response.status_code in [200, 202]

    # 2. Verify Data Exists
    # Verify via Trace endpoint
    res_trace = api_client.get(f"/v1/rag/sessions/{thread_id}/trace")
    assert res_trace.status_code == 200

    # 3. Call Reset (Cleanup)
    res_reset = api_client.post(f"/v1/rag/sessions/{thread_id}/reset")
    assert res_reset.status_code == 200
    # Expect successful message (will fail initially as "Not Supported")
    assert "successfully" in res_reset.json()["message"]

    # 4. Verify Deletion
    res_trace_after = api_client.get(f"/v1/rag/sessions/{thread_id}/trace")
    assert res_trace_after.status_code == 200
    data_after = res_trace_after.json()
    assert data_after["messages"] == []
    assert data_after["values"] == {}

