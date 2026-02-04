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
    dark_mode_graph = st.checkbox("Dark Mode", value=True, help="Toggle for Dark/Light background verification")

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
    presets_resp = api_client.get("/graph/presets") or {}
    presets = presets_resp.get("presets", {})
    # Default selection key if exists
    default_key = list(presets.keys())[0] if presets else None
    selected_preset = st.selectbox("📌 Presets", list(presets.keys()))
    if st.button("Load Preset"):
        st.session_state["cypher_input"] = presets[selected_preset]
        st.rerun()

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
            st.session_state["cypher_input"] = query
            st.rerun()

    st.divider()

    # 3. Raw Cypher
    if "cypher_input" not in st.session_state:
        st.session_state["cypher_input"] = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50"

    cypher_input = st.text_area(
        "SQL (Cypher)",
        height=150,
        key="cypher_input"
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

                        # Color Config
                        text_color = "white" if dark_mode_graph else "black"
                        edge_color = "#AAAAAA" if dark_mode_graph else "#333333"

                        nodes.append(
                            Node(
                                id=n["id"],
                                label=n["properties"].get("name") or n["properties"].get("title") or label,
                                size=25,
                                color=color,
                                title=str(n["properties"]),
                                font={"color": text_color, "size": 14}, 
                                shadow=True
                            )
                        )

                    edges = []
                    edges = []
                    for e in edge_data:
                        edges.append(Edge(source=e["source"], target=e["target"], label=e["type"], color=edge_color, font={"color": edge_color, "size": 10}))

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
