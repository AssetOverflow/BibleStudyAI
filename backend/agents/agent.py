"""
Main Pydantic AI agent for agentic RAG with knowledge graph.
"""

# Imports optimized for agentic Bible study and semantic analytics
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from .prompts import SYSTEM_PROMPT
from .providers import get_llm_model
from .tools import (
    vector_search_tool,
    graph_search_tool,
    hybrid_search_tool,
    get_document_tool,
    list_documents_tool,
    get_entity_relationships_tool,
    get_entity_timeline_tool,
    VectorSearchInput,
    GraphSearchInput,
    HybridSearchInput,
    DocumentInput,
    DocumentListInput,
    EntityRelationshipInput,
    EntityTimelineInput,
)


@dataclass
class AgentDependencies:
    """Dependencies for the agent."""

    session_id: str
    user_id: Optional[str] = None
    search_preferences: Dict[str, Any] = None

    def __post_init__(self):
        if self.search_preferences is None:
            self.search_preferences = {
                "use_vector": True,
                "use_graph": True,
                "default_limit": 10,
            }


# Initialize the agent with flexible model configuration
rag_agent = Agent(
    get_llm_model(), deps_type=AgentDependencies, system_prompt=SYSTEM_PROMPT
)


# Register tools with proper docstrings (no description parameter)


@rag_agent.tool
async def vector_search(
    ctx: RunContext[AgentDependencies],
    query: str,
    limit: int = 10,
    labels: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Search for relevant Bible content using semantic similarity and label-based filtering.

    This tool performs vector similarity search across Bible document chunks,
    supporting semantic joins and label-based filtering (e.g. topic, theme, entity).

    Args:
        query: Search query to find similar content
        limit: Maximum number of results to return (1-50)
        labels: Optional list of semantic labels to filter results

    Returns:
        List of matching chunks ordered by similarity (best first), with schema fields
    """
    input_data = VectorSearchInput(query=query, limit=limit, labels=labels)
    results = await vector_search_tool(input_data)
    return [
        {
            "content": r.content,
            "score": r.score,
            "document_title": r.document_title,
            "document_source": r.document_source,
            "chunk_id": r.chunk_id,
            "translation": getattr(r, "translation", None),
            "testament": getattr(r, "testament", None),
            "book": getattr(r, "book", None),
            "chapter": getattr(r, "chapter", None),
            "verse": getattr(r, "verse", None),
            "labels": getattr(r, "labels", None),
        }
        for r in results
    ]


@rag_agent.tool
async def graph_search(
    ctx: RunContext[AgentDependencies], query: str
) -> List[Dict[str, Any]]:
    """
    Search the knowledge graph for facts and relationships.

    This tool queries the knowledge graph to find specific facts, relationships
    between entities, and temporal information. Best for finding specific facts,
    relationships between companies/people/technologies, and time-based information.

    Args:
        query: Search query to find facts and relationships

    Returns:
        List of facts with associated episodes and temporal data
    """
    input_data = GraphSearchInput(query=query)

    results = await graph_search_tool(input_data)

    # Convert results to dict for agent
    return [
        {
            "fact": r.fact,
            "uuid": r.uuid,
            "valid_at": r.valid_at,
            "invalid_at": r.invalid_at,
            "source_node_uuid": r.source_node_uuid,
        }
        for r in results
    ]


@rag_agent.tool
async def hybrid_search(
    ctx: RunContext[AgentDependencies],
    query: str,
    limit: int = 10,
    text_weight: float = 0.3,
    labels: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Perform both vector and keyword search for comprehensive Bible results, supporting label-based filtering.

    This tool combines semantic similarity search with keyword matching and label-based filtering.
    Results include advanced schema fields for semantic analytics and joins.

    Args:
        query: Search query for hybrid search
        limit: Maximum number of results to return (1-50)
        text_weight: Weight for text similarity vs vector similarity (0.0-1.0)
        labels: Optional list of semantic labels to filter results

    Returns:
        List of chunks ranked by combined relevance score, with schema fields
    """
    input_data = HybridSearchInput(
        query=query, limit=limit, text_weight=text_weight, labels=labels
    )
    results = await hybrid_search_tool(input_data)
    return [
        {
            "content": r.content,
            "score": r.score,
            "document_title": r.document_title,
            "document_source": r.document_source,
            "chunk_id": r.chunk_id,
            "translation": getattr(r, "translation", None),
            "testament": getattr(r, "testament", None),
            "book": getattr(r, "book", None),
            "chapter": getattr(r, "chapter", None),
            "verse": getattr(r, "verse", None),
            "labels": getattr(r, "labels", None),
        }
        for r in results
    ]


@rag_agent.tool
async def get_document(
    ctx: RunContext[AgentDependencies], document_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve the complete content and metadata of a specific Bible document, including advanced schema fields.

    This tool fetches the full document content, all advanced metadata fields, and all its chunks.
    Best for getting comprehensive information from a specific Bible source.

    Args:
        document_id: UUID of the document to retrieve

    Returns:
        Complete document data with content, metadata, and schema fields, or None if not found
    """
    input_data = DocumentInput(document_id=document_id)
    document = await get_document_tool(input_data)
    if document:
        return {
            "id": document["id"],
            "translation": document.get("translation"),
            "testament": document.get("testament"),
            "book": document.get("book"),
            "book_author": document.get("book_author"),
            "canonical_order": document.get("canonical_order"),
            "chronology": document.get("chronology"),
            "title": document["title"],
            "source": document["source"],
            "content": document["content"],
            "metadata": document.get("metadata"),
            "chunk_count": len(document.get("chunks", [])),
            "created_at": document["created_at"],
            "updated_at": document.get("updated_at"),
            "labels": document.get("labels"),
        }
    return None


@rag_agent.tool
async def list_documents(
    ctx: RunContext[AgentDependencies],
    limit: int = 20,
    offset: int = 0,
    labels: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    List available Bible documents with advanced metadata and label-based filtering.

    This tool provides an overview of all Bible documents in the knowledge base,
    including advanced schema fields and supports label-based filtering.

    Args:
        limit: Maximum number of documents to return (1-100)
        offset: Number of documents to skip for pagination
        labels: Optional list of semantic labels to filter results

    Returns:
        List of documents with advanced metadata and chunk counts
    """
    input_data = DocumentListInput(limit=limit, offset=offset, labels=labels)
    documents = await list_documents_tool(input_data)
    return [
        {
            "id": getattr(d, "id", None),
            "translation": getattr(d, "translation", None),
            "testament": getattr(d, "testament", None),
            "book": getattr(d, "book", None),
            "book_author": getattr(d, "book_author", None),
            "canonical_order": getattr(d, "canonical_order", None),
            "chronology": getattr(d, "chronology", None),
            "title": getattr(d, "title", None),
            "source": getattr(d, "source", None),
            "metadata": getattr(d, "metadata", None),
            "chunk_count": getattr(d, "chunk_count", None),
            "created_at": getattr(d, "created_at", None),
            "updated_at": getattr(d, "updated_at", None),
            "labels": getattr(d, "labels", None),
        }
        for d in documents
    ]


@rag_agent.tool
async def get_entity_relationships(
    ctx: RunContext[AgentDependencies], entity_name: str, depth: int = 2
) -> Dict[str, Any]:
    """
    Get all relationships for a specific entity in the knowledge graph.

    This tool explores the knowledge graph to find how a specific entity
    (company, person, technology) relates to other entities. Best for
    understanding how companies or technologies relate to each other.

    Args:
        entity_name: Name of the entity to explore (e.g., "Google", "OpenAI")
        depth: Maximum traversal depth for relationships (1-5)

    Returns:
        Entity relationships and connected entities with relationship types
    """
    input_data = EntityRelationshipInput(entity_name=entity_name, depth=depth)

    return await get_entity_relationships_tool(input_data)


@rag_agent.tool
async def get_entity_timeline(
    ctx: RunContext[AgentDependencies],
    entity_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get the timeline of facts for a specific entity.

    This tool retrieves chronological information about an entity,
    showing how information has evolved over time. Best for understanding
    how information about an entity has developed or changed.

    Args:
        entity_name: Name of the entity (e.g., "Microsoft", "AI")
        start_date: Start date in ISO format (YYYY-MM-DD), optional
        end_date: End date in ISO format (YYYY-MM-DD), optional

    Returns:
        Chronological list of facts about the entity with timestamps
    """
    input_data = EntityTimelineInput(
        entity_name=entity_name, start_date=start_date, end_date=end_date
    )

    return await get_entity_timeline_tool(input_data)
