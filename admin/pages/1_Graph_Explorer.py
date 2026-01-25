import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph
from admin.utils.api_client import get_api_client

st.set_page_config(page_title="Graph Explorer", page_icon="🕸️", layout="wide")
st.title("🕸️ Graph Explorer")

api_client = get_api_client()

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("Graph Settings")
    physics = st.checkbox("Enable Physics", value=True)
    directed = st.checkbox("Directed Edges", value=True)

    config = Config(
        width=1000,
        height=600,
        directed=directed,
        physics=physics,
        hierarchical=False,
    )

# --- Main Layout ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Query Builder")

    # 1. Presets
    presets = api_client.get("/graph/presets") or {}
    selected_preset = st.selectbox("📌 Presets", list(presets.keys()))
    if st.button("Load Preset"):
        st.session_state["cypher_query"] = presets[selected_preset]

    st.divider()

    # 2. Builder (Fetch labels/rels from API)
    with st.expander("🛠️ Custom Builder"):
        schema = api_client.get("/graph/schema") or {"labels": [], "relationship_types": []}
        labels = ["All"] + schema["labels"]
        rels = ["All"] + schema["relationship_types"]
        
        entity_type = st.selectbox("Entity Type", labels)
        relation_type = st.selectbox("Relation Type", rels)
        limit = st.slider("Limit", 10, 100, 25)
        
        if st.button("Build Query"):
            # Simple build logic (Moved to backend if complex, but kept simple here for now)
            if entity_type == "All":
                if relation_type == "All":
                    query = f"MATCH (n)-[r]->(m) RETURN n, r, m LIMIT {limit}"
                else:
                    query = f"MATCH (n)-[r:{relation_type}]->(m) RETURN n, r, m LIMIT {limit}"
            else:
                if relation_type == "All":
                    query = f"MATCH (n:{entity_type}) RETURN n LIMIT {limit}"
                else:
                    query = f"MATCH (n:{entity_type})-[r:{relation_type}]->(m) RETURN n, r, m LIMIT {limit}"
            st.session_state["cypher_query"] = query

    st.divider()

    # 3. Raw Cypher
    cypher_input = st.text_area(
        "SQL (Cypher)", value=st.session_state.get("cypher_query", "MATCH (n) RETURN n LIMIT 25"), height=150
    )
    run_btn = st.button("🚀 Run Query", type="primary")

with col2:
    st.subheader("Visualization")

    if run_btn:
        try:
            with st.spinner("Fetching Graph Data..."):
                res = api_client.post("/graph/query", json={"query": cypher_input})
                
                if res:
                    node_data = res.get("nodes", [])
                    edge_data = res.get("edges", [])

                    nodes = []
                    for n in node_data:
                        label = n["labels"][0] if n["labels"] else "Unknown"
                        color = "#97C2FC"
                        if "Person" in n["labels"]:
                            color = "#FF7675"
                        elif "Organization" in n["labels"]:
                            color = "#74B9FF"
                        elif "Technology" in n["labels"]:
                            color = "#55E6C1"
                        elif "Document" in n["labels"]:
                            color = "#A29BFE"
                        elif "Chunk" in n["labels"]:
                            color = "#DFE6E9"

                        nodes.append(
                            Node(
                                id=n["id"],
                                label=n["properties"].get("name") or n["properties"].get("title") or label,
                                size=20,
                                color=color,
                                title=str(n["properties"]),
                            )
                        )

                    edges = []
                    for e in edge_data:
                        edges.append(Edge(source=e["source"], target=e["target"], label=e["type"], color="#B2BEC3"))

                    if not nodes:
                        st.warning("No nodes found.")
                    else:
                        st.success(f"Found {len(nodes)} Nodes, {len(edges)} Edges")
                        agraph(nodes=nodes, edges=edges, config=config)

                        with st.expander("Show Raw Data"):
                            st.json({"nodes": node_data, "edges": edge_data})
                else:
                    st.error("Failed to fetch graph data.")

        except Exception as e:
            st.error(f"Error executing query: {e}")
