<!-- @format -->

# BibleStudyAI

This project is an AI-powered biblical studies platform designed to assist users in their research and understanding of the Bible. It leverages a sophisticated agentic RAG (Retrieval-Augmented Generation) system, a knowledge graph, and multiple specialized AI agents to provide comprehensive and context-aware answers to user queries.

## Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Agentic RAG System**: A multi-agent system where specialized AI agents collaborate to provide well-rounded answers.
- **Knowledge Graph**: Utilizes a Neo4j graph database to store and retrieve relationships between biblical entities, concepts, and passages.
- **Vector Search**: Employs Milvus for efficient similarity search on biblical texts.
- **Hybrid Search**: Combines keyword, vector, and graph-based search for optimal retrieval.
- **User Authentication**: Secure user authentication using JWT and Argon2 password hashing.
- **Real-time Monitoring**: Integrated with Deephaven for real-time monitoring of agent interactions.
- **Scalable Architecture**: Built with FastAPI, Docker, and a suite of modern database technologies.

## System Architecture

The system is composed of the following key components:

- **FastAPI Backend**: The core of the application, providing a RESTful API for user interaction and agent orchestration.
- **React Frontend**: A user-friendly interface for interacting with the AI agents.
- **TimescaleDB**: A PostgreSQL database for storing structured data, such as user information and notes.
- **Milvus**: A vector database for storing and searching text embeddings.
- **Neo4j**: A graph database for the knowledge graph.
- **Redis**: Used for caching and as a message broker.
- **Redpanda**: A Kafka-compatible streaming platform for asynchronous communication between agents.
- **Deephaven**: A real-time analytics engine for monitoring agent activity.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11
- Node.js and npm
- An OpenAI API key

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/AssetOverflow/BibleStudyAI.git
    cd BibleStudyAI
    ```

2.  **Set up environment variables:**

    Create a `.env` file in the root of the project and add the following:

    ```env
    OPENAI_API_KEY=your_openai_api_key
    ```

3.  **Build and run the application:**

    ```bash
    docker-compose up --build
    ```

## Usage

### Running the Application

Once the containers are running, you can access the application at `http://localhost:3000`.

### API Endpoints

The API documentation is available at `http://localhost:8000/docs`.

Key endpoints include:

- `POST /users/`: Create a new user.
- `POST /token`: Obtain a JWT token for authentication.
- `POST /chat/`: Interact with the AI agents.

## Project Structure

The project is organized into the following directories:

```
BibleStudyAI/
├── backend/         # FastAPI backend
├── frontend/        # React frontend
├── db/              # Database initialization scripts
├── docker-compose.yml
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
