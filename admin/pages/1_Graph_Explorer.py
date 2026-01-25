import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph

from admin.services.graph_service import GraphService

st.set_page_config(page_title="Graph Explorer", page_icon="🕸️", layout="wide")
st.title("🕸️ Graph Explorer")


# Initialize Service
@st.cache_resource
def get_graph_service():
    return GraphService()


service = get_graph_service()

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
    presets = service.get_presets()
    selected_preset = st.selectbox("📌 Presets", list(presets.keys()))
    if st.button("Load Preset"):
        st.session_state["cypher_query"] = presets[selected_preset]

    st.divider()

    # 2. Builder
    with st.expander("🛠️ Custom Builder"):
        entity_type = st.selectbox("Entity Type", ["All", "Person", "Organization", "Technology", "Document", "Chunk"])
        relation_type = st.selectbox("Relation Type", ["All", "MENTIONS", "WORKS_FOR", "RELATED_TO", "HAS_CHUNK"])
        limit = st.slider("Limit", 10, 100, 50)
        if st.button("Build Query"):
            query = service.build_query(entity_type, relation_type, limit)
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
                node_data, edge_data = service.execute_graph_query(cypher_input)

                nodes = []
                for n in node_data:
                    # Determine color/icon based on labels
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
                            title=str(n["properties"]),  # Tooltip
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

                    # Show Raw Data in Expander
                    with st.expander("Show Raw Data"):
                        st.json({"nodes": node_data, "edges": edge_data})

        except Exception as e:
            st.error(f"Error executing query: {e}")
