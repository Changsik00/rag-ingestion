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


@pytest.mark.integration
def test_find_shortest_path(graph_repo):
    """
    Scenario: Find shortest path between two entities
    1. Create A -> B -> C
    2. Call find_shortest_path([A, C])
    3. Verify result contains A->B and B->C
    """
    from uuid import uuid4

    suffix = uuid4().hex[:6]
    name_a = f"A_{suffix}"
    name_b = f"B_{suffix}"
    name_c = f"C_{suffix}"

    graph_repo.save_entity(name_a, EntityType.CONCEPT)
    graph_repo.save_entity(name_b, EntityType.CONCEPT)
    graph_repo.save_entity(name_c, EntityType.CONCEPT)

    class MockRelType:
        value = "RELATED_TO"

    graph_repo.create_entity_relationship(name_a, MockRelType(), name_b)
    graph_repo.create_entity_relationship(name_b, MockRelType(), name_c)

    # Call method
    if hasattr(graph_repo, "find_shortest_path"):
        results = graph_repo.find_shortest_path([name_a, name_c])
    else:
        pytest.fail("find_shortest_path not implemented yet")

    # Assert
    assert len(results) >= 2
    # Verify path continuity
    sources = set(r["source"] for r in results)
    targets = set(r["target"] for r in results)

    assert name_a in sources
    assert name_b in sources  # B is source of B->C
    assert name_b in targets  # B is target of A->B
    assert name_c in targets
