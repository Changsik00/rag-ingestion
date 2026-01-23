import pytest

from app.domain.schemas.ontology import EntityType
from app.infrastructure.storage.neo4j_graph_repository import Neo4jGraphRepository
from app.interfaces.api.dependencies import get_neo4j_driver


@pytest.fixture
def graph_repo():
    driver = get_neo4j_driver()
    repo = Neo4jGraphRepository(driver)
    yield repo


@pytest.mark.integration
def test_get_subgraph_flow(graph_repo):
    """
    Scenario: Retrieve Subgraph for specific entities
    1. Create Entities: Elon (Person), Tesla (Org).
    2. Create Relationship: Elon FOUNDED Tesla.
    3. Call get_subgraph(['Elon']).
    4. Verify result contains the triple (Elon, FOUNDED, Tesla).
    """
    # 1. Setup Data
    # Use unique names to avoid collision
    from uuid import uuid4

    suffix = uuid4().hex[:6]
    elon = f"Elon_{suffix}"
    tesla = f"Tesla_{suffix}"

    graph_repo.save_entity(elon, EntityType.PERSON)
    graph_repo.save_entity(tesla, EntityType.ORGANIZATION)

    # We need to manually create relationship because save_entity doesn't do it
    # And create_entity_relationship interface requires enum?
    # Let's check create_entity_relationship signature in previous file view
    # It takes relationship_type as ENUM.
    # For flexibility in test, we might mock the enum or just pass an object with .value

    class MockRelType:
        value = "FOUNDED"

    graph_repo.create_entity_relationship(elon, MockRelType(), tesla)

    # 2. Call get_subgraph (TDD: Method not implemented yet)
    if hasattr(graph_repo, "get_subgraph"):
        results = graph_repo.get_subgraph([elon])
    else:
        pytest.fail("get_subgraph not implemented yet")

    # 3. Assert
    # Expecting list of dicts: source, types, target
    assert len(results) > 0

    found = False
    for triple in results:
        # Check structure
        assert "source" in triple
        assert "relationship" in triple
        assert "target" in triple

        if triple["source"] == elon and triple["target"] == tesla and triple["relationship"] == "FOUNDED":
            found = True

    assert found, f"Relationship {elon} FOUNDED {tesla} not found in subgraph"
