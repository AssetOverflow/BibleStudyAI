from fastapi import (
    FastAPI,
    HTTPException,
    BackgroundTasks,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import json
import asyncio
from datetime import datetime
from loguru import logger
from contextlib import asynccontextmanager

# Import project modules
from utils.config import settings
from utils.logging import setup_logging
from models import api_models, db_models
from services.rag_system import RAGSystem
from database.timescale_db import get_engine
from database.neo4j_graph import Neo4jManager
from database.milvus_vector import MilvusManager
from services.knowledge_graph import BiblicalKnowledgeGraph

# from services.deephaven_manager import DeephavenManager  # Commented out until deephaven is enabled
# from services.kafka_communication import KafkaManager  # Commented out until redpanda is enabled
from routers import (
    auth,
    notes,
    bible,
)  # chat, users  # Import additional routers when ready

# Setup logging
setup_logging(level="DEBUG", serialize=False)

# Global instances
rag_system: RAGSystem | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan with proper startup and shutdown."""
    logger.info(f"Starting {settings.PROJECT_NAME}...")

    # Create DB tables if they don't exist with retry logic
    engine = get_engine()
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(db_models.Base.metadata.create_all)
            logger.info("Successfully connected to database and created tables")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Database connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds..."
                )
                await asyncio.sleep(retry_delay)
            else:
                logger.error(
                    f"Failed to connect to database after {max_retries} attempts: {e}"
                )
                raise

    global rag_system
    try:
        # Initialize the fully implemented RAG system
        rag_system = RAGSystem()
        logger.info("Successfully initialized RAG System")

    except Exception as e:
        logger.opt(exception=True).error(f"Failed to initialize components: {e}")
        raise

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    if rag_system:
        rag_system.close()
    logger.info("Shutdown complete.")


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Advanced Biblical Teaching System API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(bible.router, prefix="/api/bible", tags=["bible"])
from routers import search

# ...existing code...
app.include_router(search.router, prefix="/api/search", tags=["search"])


# Core RAG API Endpoint
@app.post("/api/rag/answer", response_model=api_models.RAGResponse)
async def get_rag_answer(request: api_models.RAGRequest):
    """
    Receives a question, retrieves context from vector and graph databases,
    and generates a synthesized answer using the RAG system.
    """
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system is not available.")
    try:
        result = await rag_system.answer_question(request.question)
        return api_models.RAGResponse(
            answer=result.get("answer", ""), context=result.get("context", {})
        )
    except Exception as e:
        logger.opt(exception=True).error(f"Error processing RAG request: {e}")
        raise HTTPException(status_code=500, detail="Error processing your request.")


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components": {"database": "connected", "rag_system": "active"},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
