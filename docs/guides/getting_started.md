# 🚀 Getting Started with RAG Ingestion

This guide covers the prerequisites, installation, and steps to run the RAG Ingestion Engine.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker & Docker Compose**: For containerized deployment (Recommended).
*   **Python 3.12+**: For local development.
*   **Make**: For executing build commands.

## ⚡ Quick Start (Docker)

The easiest way to run the entire system (Backend, Admin, DBs) is using Docker Compose.

### 1. Build & Run
Docker Build Optimization (Spec 059) is applied using a Base Image.

```bash
# Option A: Build Base Image & Run All Services (Recommended)
make up

# Option B: Manual Build & Run
make build-base
docker compose up -d --build
```

### 2. Verify Services
Once running, you can access the following services:

| System | URL | Description |
| :--- | :--- | :--- |
| **Admin Dashboard** | [http://localhost:8501](http://localhost:8501) | Main Interface for Monitoring & Control |
| **API Documentation** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI for Backend API |
| **Neo4j Browser** | [http://localhost:7474](http://localhost:7474) | Graph Database Viewer (ID/PW: neo4j/password) |

### 3. Stop Services
```bash
make down
# OR
docker compose down
```

---

## 🔧 Configuration (.env)

Create a `.env` file in the project root. You can copy from `.env.example`.

```ini
# Core
PROJECT_NAME=rag-ingestion
ENV=development

# LLM (Gemini)
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-2.0-flash-exp

# Database
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# ... see .env.example for full list
```

## 💻 Local Development

If you want to run the code locally without Docker (e.g. for debugging):

1.  **Install Dependencies**:
    ```bash
    uv sync
    ```

2.  **Run Dependencies (DBs only)**:
    ```bash
    docker compose up -d neo4j redis
    ```

3.  **Run Backend**:
    ```bash
    uv run uvicorn app.main:app --reload
    ```

4.  **Run Streamlit Admin**:
    ```bash
    uv run streamlit run admin/app.py
    ```
