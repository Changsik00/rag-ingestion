from unittest.mock import MagicMock, patch

import pytest

from app.admin.services.graph_service import GraphService


@pytest.fixture
def mock_driver():
    with patch("neo4j.GraphDatabase.driver") as mock:
        yield mock


@pytest.fixture
def graph_service(mock_driver):
    # Mocking config loading if necessary, or assuming default env vars work for tests
    return GraphService()


def test_get_presets(graph_service):
    """Test that presets are returned correctly."""
    presets = graph_service.get_presets()
    assert isinstance(presets, dict)
    assert len(presets) > 0
    assert "전체 노드 조회 (Limit 50)" in presets


def test_build_query_simple(graph_service):
    """Test query builder for simple entity lookup."""
    query = graph_service.build_query(entity_type="Person", relation_type=None, limit=10)
    assert "MATCH (n:Person)" in query
    assert "RETURN n" in query
    assert "LIMIT 10" in query


def test_build_query_relation(graph_service):
    """Test query builder for relationship lookup."""
    query = graph_service.build_query(entity_type="Person", relation_type="WORKS_FOR", limit=20)
    assert "MATCH (n:Person)-[r:WORKS_FOR]->(m)" in query
    assert "RETURN n, r, m" in query
    assert "LIMIT 20" in query


def test_build_query_all(graph_service):
    """Test query builder for 'All' selection."""
    query = graph_service.build_query(entity_type="All", relation_type="All", limit=5)
    assert "MATCH (n)-[r]->(m)" in query
    assert "LIMIT 5" in query


def test_execute_cypher_success(graph_service):
    """Test executing a Cypher query successfully."""
    mock_driver = graph_service.driver
    mock_session_context = mock_driver.session.return_value
    mock_session = mock_session_context.__enter__.return_value

    # Mock result record
    mock_record = MagicMock()
    mock_record.data.return_value = {"n": {"name": "Alice"}}

    # Mock result iterator
    mock_session.run.return_value = [mock_record]

    result = graph_service.execute_query("MATCH (n) RETURN n")

    assert len(result) == 1
    assert result[0] == {"n": {"name": "Alice"}}
    mock_session.run.assert_called_with("MATCH (n) RETURN n")


def test_execute_graph_query(graph_service):
    """Test executing a query and returning graph data (nodes/relationships)."""
    mock_driver = graph_service.driver
    mock_session_context = mock_driver.session.return_value
    mock_session = mock_session_context.__enter__.return_value

    # Mock result with graph method
    mock_result = MagicMock()
    # Mock graph() result
    mock_node = MagicMock()
    mock_node.element_id = "1"
    mock_node.labels = {"Person"}
    mock_node._properties = {"name": "Bob"}

    mock_rel = MagicMock()
    mock_rel.element_id = "r1"
    mock_rel.type = "KNOWS"
    mock_rel.start_node.element_id = "1"
    mock_rel.end_node.element_id = "2"
    mock_rel._properties = {"since": 2024}

    mock_graph = MagicMock()
    mock_graph.nodes = [mock_node]
    mock_graph.relationships = [mock_rel]

    mock_result.graph.return_value = mock_graph
    mock_session.run.return_value = mock_result

    nodes, edges = graph_service.execute_graph_query("MATCH path = (n)-[r]->(m) RETURN path")

    assert len(nodes) == 1
    assert nodes[0]["id"] == "1"
    assert "Person" in nodes[0]["labels"]
    assert nodes[0]["properties"] == {"name": "Bob"}

    assert len(edges) == 1
    assert edges[0]["id"] == "r1"
    assert edges[0]["source"] == "1"
    assert edges[0]["target"] == "2"
    assert edges[0]["type"] == "KNOWS"


def test_execute_cypher_error(graph_service):
    """Test handling of Neo4j errors."""
    mock_driver = graph_service.driver
    mock_session_context = mock_driver.session.return_value
    mock_session = mock_session_context.__enter__.return_value

    mock_session.run.side_effect = Exception("Neo4j Error")

    with pytest.raises(Exception, match="Neo4j Error"):
        graph_service.execute_query("INVALID QUERY")
