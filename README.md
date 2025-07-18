# KoinoniaHouse

A modern full-stack application for biblical study and analysis, featuring a React frontend and FastAPI backend with advanced AI integration.

## 🚀 Features

- **Interactive Bible Explorer**: Modern interface for biblical text exploration
- **AI-Powered Chat**: Intelligent conversation system for biblical insights
- **Knowledge Graph**: Visual representation of biblical connections and relationships
- **Note Taking System**: Comprehensive note management for study sessions
- **Study Groups**: Collaborative learning environment
- **Prophecy Lab**: Advanced analytical tools for prophetic studies

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.11
- **Database**: TimescaleDB (PostgreSQL with time-series extensions)
- **Vector Database**: Milvus for semantic search
- **Graph Database**: Neo4j for relationship mapping
- **Message Queue**: Kafka/RedPanda for event streaming
- **Caching**: Redis Stack
- **Analytics**: Deephaven for real-time data analysis

### Frontend (React + Vite)
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite 7
- **Styling**: CSS with modern design patterns
- **Icons**: React Icons
- **Animations**: Framer Motion
- **Charts**: Chart.js for data visualization

## 🛠️ Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd KoinoniaHouse
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker compose up --build -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🔧 Development

### Backend Development
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 📦 Services

The application consists of multiple containerized services:

- **fastapi-backend**: Main API server
- **react-frontend**: User interface
- **timescaledb**: Primary database with vector extensions
- **milvus**: Vector database for semantic search
- **neo4j**: Graph database for relationships
- **redis-stack**: Caching and session management
- **redpanda**: Message streaming
- **deephaven**: Real-time analytics

## 🔑 Environment Variables

Create a `.env` file with the following variables:

```env
# Database
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=koinonia_house
POSTGRES_PORT=5432

# Redis
REDIS_PASSWORD=your_redis_password
REDIS_PORT=6379

# AI Services
OPENAI_API_KEY=your_openai_key
XAI_API_KEY=your_xai_key
```

## 📁 Project Structure

```
KoinoniaHouse/
├── backend/                 # FastAPI backend
│   ├── agents/             # AI agent implementations
│   ├── database/           # Database connections and models
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic services
│   └── utils/              # Utility functions
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── assets/         # Static assets
│   │   └── memory/         # Memory management
├── db/                     # Database initialization
├── docker-compose.yml      # Service orchestration
└── ProjectDesign/          # Documentation and design docs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](./ProjectDesign/)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Issue Tracker](https://github.com/your-username/KoinoniaHouse/issues)

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by the need for advanced biblical study tools
- Community-driven development
