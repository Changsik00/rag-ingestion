from datetime import datetime

from app.interfaces.api.v1.dto.jobs import JobResponse, ResumeRequest


def test_job_response_creation():
    now = datetime.now()
    response = JobResponse(job_id="job-123", current_status="running", source_url="http://example.com", created_at=now)
    assert response.job_id == "job-123"
    assert response.current_status == "running"
    assert response.created_at == now
    assert response.metadata == {}


def test_resume_request():
    req = ResumeRequest(input={"foo": "bar"})
    assert req.input["foo"] == "bar"
