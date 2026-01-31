"""
Contract tests for JobRepository implementations.
"""

import pytest

from app.domain.interfaces.job_repository import JobRepository
from app.infrastructure.repositories.neo4j_job_repository import Neo4jJobRepository


@pytest.fixture(
    params=[
        Neo4jJobRepository,
    ]
)
def job_repo_class(request):
    """All JobRepository implementation classes"""
    return request.param


class TestJobRepositoryContract:
    """Contract tests for JobRepository interface"""

    def test_implements_job_repository(self, job_repo_class):
        """All job repository classes must implement JobRepository"""
        assert issubclass(job_repo_class, JobRepository)

    def test_has_create_job_method(self, job_repo_class):
        """All job repository classes must have a create_job method"""
        assert hasattr(job_repo_class, "create_job")
        assert callable(getattr(job_repo_class, "create_job"))

    def test_has_update_job_method(self, job_repo_class):
        """All job repository classes must have an update_job method"""
        assert hasattr(job_repo_class, "update_job")
        assert callable(getattr(job_repo_class, "update_job"))

    def test_has_get_job_method(self, job_repo_class):
        """All job repository classes must have a get_job method"""
        assert hasattr(job_repo_class, "get_job")
        assert callable(getattr(job_repo_class, "get_job"))

    def test_has_list_jobs_method(self, job_repo_class):
        """All job repository classes must have a list_jobs method"""
        assert hasattr(job_repo_class, "list_jobs")
        assert callable(getattr(job_repo_class, "list_jobs"))

    def test_create_job_method_signature(self, job_repo_class):
        """create_job method should accept Job entity"""
        import inspect

        sig = inspect.signature(job_repo_class.create_job)
        params = list(sig.parameters.values())

        # Should have 'self' and 'job' parameters
        assert len(params) == 2, f"{job_repo_class.__name__}.create_job should have 2 parameters (self, job)"

        param_names = [p.name for p in params]
        assert "self" in param_names
        assert "job" in param_names

    def test_get_job_method_signature(self, job_repo_class):
        """get_job method should accept job_id"""
        import inspect

        sig = inspect.signature(job_repo_class.get_job)
        params = list(sig.parameters.values())

        # Should have 'self' and 'job_id' parameters
        assert len(params) == 2, f"{job_repo_class.__name__}.get_job should have 2 parameters (self, job_id)"

        param_names = [p.name for p in params]
        assert "self" in param_names
        assert "job_id" in param_names

    def test_update_job_method_signature(self, job_repo_class):
        """update_job method should accept job entity"""
        import inspect

        sig = inspect.signature(job_repo_class.update_job)
        params = list(sig.parameters.values())

        # Should have 'self' and 'job' parameters
        assert len(params) == 2, f"{job_repo_class.__name__}.update_job should have 2 parameters (self, job)"

        param_names = [p.name for p in params]
        assert "self" in param_names
        assert "job" in param_names

    def test_list_jobs_method_signature(self, job_repo_class):
        """list_jobs method should accept optional limit parameter"""
        import inspect

        sig = inspect.signature(job_repo_class.list_jobs)
        params = list(sig.parameters.values())

        # Should have at least 'self', optionally 'limit'
        assert len(params) >= 1, f"{job_repo_class.__name__}.list_jobs should have at least 1 parameter (self)"

        param_names = [p.name for p in params]
        assert "self" in param_names

        # If limit exists, it should have a default value
        if "limit" in param_names:
            limit_param = [p for p in params if p.name == "limit"][0]
            assert limit_param.default != inspect.Parameter.empty, "limit parameter should have a default value"


class TestJobRepositoryConstructorConsistency:
    """Tests to verify constructor consistency across JobRepository implementations"""

    def test_neo4j_job_repository_constructor(self):
        """Neo4jJobRepository should accept a Driver instance"""
        from unittest.mock import Mock

        from neo4j import Driver

        mock_driver = Mock(spec=Driver)
        repo = Neo4jJobRepository(mock_driver)

        assert repo.driver == mock_driver
