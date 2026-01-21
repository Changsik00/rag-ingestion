import pytest

from app.admin.config import AdminConfig


def test_admin_config_loading(monkeypatch):
    """Test that AdminConfig loads values from environment variables."""
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "password")

    config = AdminConfig()

    assert config.neo4j_uri == "bolt://localhost:7687"
    assert config.neo4j_username == "neo4j"
    assert config.neo4j_password == "password"


def test_admin_config_defaults():
    """Test default values if environment variables are missing (if applicable)."""
    # Assuming standard defaults or just checking strictness
    # For now, let's just ensure it initializes
    try:
        config = AdminConfig()
        assert config is not None
    except Exception:
        pytest.fail("AdminConfig failed to initialize with defaults/existing env")
