<!-- @format -->

# Gemini Backend Development Plan

This document outlines the development plan for the Koinonia House backend. The backend is a FastAPI application responsible for powering the various features of the Koinonia House platform, including AI-driven chat, Bible exploration, knowledge graph visualization, and collaborative study tools.

## 1. Project Setup & Configuration

- **Environment Variables**: Ensure all necessary environment variables from `docker-compose.yml` are documented and a `.env.example` file is created.
- **Configuration Management**: Use `backend/utils/config.py` to load and manage all configurations.
- **Logging**: Implement structured logging in `backend/utils/logging.py` to be used across all services.

## 2. Core Data Models

Define the core data models in `backend/models/`.

### `data_models.py` (Pydantic models for data representation)

- `User`: User profile information.
- `Note`: User-created notes, potentially linked to Bible verses or topics.
- `ChatMessage`: A single message in a chat session.
- `BibleVerse`: Representation of a Bible verse.
- `KnowledgeGraphNode`: A node in the Neo4j graph.
- `KnowledgeGraphEdge`: A relationship in the Neo4j graph.

### `api_models.py` (Pydantic models for API requests/responses)

- Schemas for user login/registration.
- Schemas for creating/updating notes.
- Schemas for chat requests.
- Schemas for API responses, including standardized error responses.

### `db_models.py` (SQLAlchemy/ORM models for TimescaleDB)

- Tables for users, notes, chat history, and other relational data.

## 3. API Endpoint Design (`main.py`)

This section details the API endpoints required by the frontend components.

### User Authentication (`/auth`)

- `POST /auth/register`: Register a new user.
- `POST /auth/login`: Authenticate a user and return a token.
- `GET /users/me`: Get current user's profile.

### Chat Interface (`/chat`)

- `POST /chat`: Send a message to the RAG system and get a response.
- `GET /chat/history/{session_id}`: Retrieve the chat history for a session.
- `GET /chat/sessions`: List all chat sessions for the current user.

### Bible Explorer (`/bible`)

- **Data Source**: Preprocessed Bible translations are stored as Parquet files in `db/bibles/parquet/`. Use PyArrow or Pandas to query verses for the Bible Explorer endpoints.
- `GET /bible/books`: Get a list of all books in the Bible.
- `GET /bible/chapters`: Get chapters for a specific book.
- `GET /bible/verses`: Get verses for a specific chapter.
- `GET /bible/search`: Search the Bible for a query string.

### Note Taking (`/notes`)

- `POST /notes`: Create a new note.
- `GET /notes`: Get all notes for the current user.
- `GET /notes/{note_id}`: Get a specific note.
- `PUT /notes/{note_id}`: Update a note.
- `DELETE /notes/{note_id}`: Delete a note.

### Knowledge Graph (`/graph`)

- `GET /graph/topic/{topic}`: Get graph data related to a specific topic.
- `GET /graph/search`: Search for nodes in the knowledge graph.

### Prophecy Lab (`/prophecy`)

- `GET /prophecy/topics`: List available prophecy topics.
- `GET /prophecy/analysis/{topic}`: Get analysis and related verses for a prophecy topic.

### Study Groups (`/groups`)

- `POST /groups`: Create a new study group.
- `GET /groups`: List study groups for the user.
- `GET /groups/{group_id}`: Get details of a study group.
- `POST /groups/{group_id}/join`: Join a study group.
- `POST /groups/{group_id}/chat`: Post a message in the group chat.

## 4. Service Layer Implementation (`backend/services/`)

### `ai_integration.py`

- Connect to OpenAI and XAI APIs.
- Provide a unified interface for different LLM providers.

### `rag_system.py`

- Orchestrate the Retrieval-Augmented Generation process.
- Take a user query.
- Retrieve relevant context from Milvus (vector search) and Neo4j (graph search).
- Construct a prompt with the context and query.
- Call the AI service (`ai_integration.py`) to get a response.

### `knowledge_graph.py`

- Interface with the Neo4j database (`database/neo4j_graph.py`).
- Provide functions to query and update the knowledge graph.
- Implement algorithms for graph traversal and analysis (e.g., finding related concepts).

### `kafka_communication.py`

- Manage producing and consuming messages from Redpanda/Kafka.
- Used for asynchronous tasks, real-time updates (e.g., study group chat), and data ingestion pipelines.

### `deephaven_manager.py`

- Interface with the Deephaven server for real-time data analysis and dashboards.
- (Scope to be defined based on specific real-time analytics requirements).

## 5. Database Layer Implementation (`backend/database/`)

### `timescale_db.py`

- Handle connections to the TimescaleDB instance.
- Define functions for CRUD operations on the relational data (users, notes, etc.).

### `milvus_vector.py`

- Handle connections to the Milvus vector database.
- Provide functions to create collections, insert text embeddings, and perform similarity searches.

### `neo4j_graph.py`

- Handle connections to the Neo4j graph database.
- Provide functions to execute Cypher queries for graph operations.

## 6. Agentic Workflows (`backend/agents/`)

### `base_agents.py`

- Define the base classes for different types of AI agents (e.g., ResearchAgent, ChatAgent, BibleStudyAgent).
- Each agent will have specific tools and prompts.

### `workflows.py`

- Define multi-step workflows that combine different agents to accomplish complex tasks.
- Example Workflow: "Analyze a Bible Passage"
  1. `BibleStudyAgent` retrieves the passage and related cross-references.
  2. `ResearchAgent` queries the knowledge graph and vector DB for historical context and commentaries.
  3. `ChatAgent` synthesizes the information and presents it to the user.

## 7. Development and Deployment

- **Local Development**: Run all services using `docker-compose up`.
- **Testing**: Implement unit and integration tests for all services and API endpoints.
- **CI/CD**: Set up a CI/CD pipeline to automate testing and deployment.
- **API Documentation**: FastAPI will automatically generate OpenAPI (`/docs`) and ReDoc (`/redoc`) documentation. Ensure all API models have good descriptions.
