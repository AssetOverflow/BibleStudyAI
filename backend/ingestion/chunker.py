# Unified chunk model for Bible and documents
from typing import List, Dict, Any, Optional, Tuple
import re
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from loguru import logger


@dataclass
class UnifiedChunk:
    """Chunk model supporting both biblical and general document context."""

    id: str = None
    content: str = ""
    translation: Optional[str] = None
    book: Optional[str] = None
    chapter: Optional[int] = None
    start_verse: Optional[int] = None
    end_verse: Optional[int] = None
    chunk_index: Optional[int] = None
    word_count: int = 0
    char_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.word_count == 0:
            self.word_count = len(self.content.split())
        if self.char_count == 0:
            self.char_count = len(self.content)
        # Add Bible-specific metadata if available
        if (
            self.book
            and self.chapter
            and self.start_verse is not None
            and self.end_verse is not None
        ):
            self.metadata.update(
                {
                    "passage_reference": f"{self.book} {self.chapter}:{self.start_verse}-{self.end_verse}",
                    "chunk_size": self.word_count,
                    "testament": "old" if self._is_old_testament() else "new",
                }
            )

    def _is_old_testament(self) -> bool:
        ot_books = {
            "Genesis",
            "Exodus",
            "Leviticus",
            "Numbers",
            "Deuteronomy",
            "Joshua",
            "Judges",
            "Ruth",
            "1 Samuel",
            "2 Samuel",
            "1 Kings",
            "2 Kings",
            "1 Chronicles",
            "2 Chronicles",
            "Ezra",
            "Nehemiah",
            "Esther",
            "Job",
            "Psalms",
            "Proverbs",
            "Ecclesiastes",
            "Song of Solomon",
            "Isaiah",
            "Jeremiah",
            "Lamentations",
            "Ezekiel",
            "Daniel",
            "Hosea",
            "Joel",
            "Amos",
            "Obadiah",
            "Jonah",
            "Micah",
            "Nahum",
            "Habakkuk",
            "Zephaniah",
            "Haggai",
            "Zechariah",
            "Malachi",
        }
        return self.book in ot_books if self.book else False


import os
from dotenv import load_dotenv

load_dotenv()

# Import agentic providers
try:
    from ..agent.providers import get_embedding_client, get_ingestion_model
except ImportError:
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agent.providers import get_embedding_client, get_ingestion_model
embedding_client = get_embedding_client()
ingestion_model = get_ingestion_model()


@dataclass
class ChunkingConfig:
    """Configuration for chunking."""

    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_chunk_size: int = 2000
    min_chunk_size: int = 100
    use_semantic_splitting: bool = True
    preserve_structure: bool = True
    mode: str = "auto"  # "auto", "bible", "semantic", "simple"

    def __post_init__(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")
        if self.min_chunk_size <= 0:
            raise ValueError("Minimum chunk size must be positive")


# Unified chunk object for all chunkers
@dataclass
class ChunkObject:
    content: str
    index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]
    token_count: Optional[int] = None
    embedding: Optional[List[float]] = None

    def __post_init__(self):
        if self.token_count is None:
            self.token_count = len(self.content) // 4


class SemanticChunker:
    """Semantic document chunker using LLM for intelligent splitting."""

    def __init__(self, config: ChunkingConfig):
        self.config = config
        self.client = embedding_client
        self.model = ingestion_model

    async def chunk_document(
        self,
        content: str,
        title: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[ChunkObject]:
        if not content.strip():
            return []
        base_metadata = {"title": title, "source": source, **(metadata or {})}
        if self.config.use_semantic_splitting and len(content) > self.config.chunk_size:
            try:
                semantic_chunks = await self._semantic_chunk(content)
                if semantic_chunks:
                    return self._create_chunk_objects(
                        semantic_chunks, content, base_metadata
                    )
            except Exception as e:
                logger.warning(
                    f"Semantic chunking failed, falling back to simple chunking: {e}"
                )
        return self._simple_chunk(content, base_metadata)

    async def _semantic_chunk(self, content: str) -> List[str]:
        """
        Perform semantic chunking using LLM.

        Args:
            content: Content to chunk

        Returns:
            List of chunk boundaries
        """
        sections = self._split_on_structure(content)
        chunks = []
        current_chunk = ""
        for section in sections:
            potential_chunk = (
                current_chunk + "\n\n" + section if current_chunk else section
            )
            if len(potential_chunk) <= self.config.chunk_size:
                current_chunk = potential_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                if len(section) > self.config.max_chunk_size:
                    sub_chunks = await self._split_long_section(section)
                    chunks.extend(sub_chunks)
                else:
                    current_chunk = section
        if current_chunk:
            chunks.append(current_chunk.strip())
        return [
            chunk
            for chunk in chunks
            if len(chunk.strip()) >= self.config.min_chunk_size
        ]

    def _split_on_structure(self, content: str) -> List[str]:
        """
        Split content on structural boundaries.

        Args:
            content: Content to split

        Returns:
            List of sections
        """
        # Split on markdown headers, paragraphs, and other structural elements
        patterns = [
            r"\n#{1,6}\s+.+?\n",  # Markdown headers
            r"\n\n+",  # Multiple newlines (paragraph breaks)
            r"\n[-*+]\s+",  # List items
            r"\n\d+\.\s+",  # Numbered lists
            r"\n```.*?```\n",  # Code blocks
            r"\n\|\s*.+?\|\s*\n",  # Tables
        ]

        # Split by patterns but keep the separators
        sections = [content]

        for pattern in patterns:
            new_sections = []
            for section in sections:
                parts = re.split(
                    f"({pattern})", section, flags=re.MULTILINE | re.DOTALL
                )
                new_sections.extend([part for part in parts if part.strip()])
            sections = new_sections

        return sections

    async def _split_long_section(self, section: str) -> List[str]:
        """
        Split a long section using LLM for semantic boundaries.

        Args:
            section: Section to split

        Returns:
            List of sub-chunks
        """
        try:
            prompt = f"""
            Split the following text into semantically coherent chunks. Each chunk should:
            1. Be roughly {self.config.chunk_size} characters long
            2. End at natural semantic boundaries
            3. Maintain context and readability
            4. Not exceed {self.config.max_chunk_size} characters

            Return only the split text with "---CHUNK---" as separator between chunks.

            Text to split:
            {section}
            """

            # Use Pydantic AI for LLM calls
            from pydantic_ai import Agent

            temp_agent = Agent(self.model)

            response = await temp_agent.run(prompt)
            result = response.data
            chunks = [chunk.strip() for chunk in result.split("---CHUNK---")]

            # Validate chunks
            valid_chunks = []
            for chunk in chunks:
                if (
                    self.config.min_chunk_size
                    <= len(chunk)
                    <= self.config.max_chunk_size
                ):
                    valid_chunks.append(chunk)

            return valid_chunks if valid_chunks else self._simple_split(section)

        except Exception as e:
            logger.error(f"LLM chunking failed: {e}")
            return self._simple_split(section)

    def _simple_split(self, text: str) -> List[str]:
        """
        Simple text splitting as fallback.

        Args:
            text: Text to split

        Returns:
            List of chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.config.chunk_size

            if end >= len(text):
                # Last chunk
                chunks.append(text[start:])
                break

            # Try to end at a sentence boundary
            chunk_end = end
            for i in range(end, max(start + self.config.min_chunk_size, end - 200), -1):
                if text[i] in ".!?\n":
                    chunk_end = i + 1
                    break

            chunks.append(text[start:chunk_end])
            start = chunk_end - self.config.chunk_overlap

        return chunks

    def _simple_chunk(
        self, content: str, base_metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Simple rule-based chunking.

        Args:
            content: Content to chunk
            base_metadata: Base metadata for chunks

        Returns:
            List of document chunks
        """
        chunks = self._simple_split(content)
        return self._create_chunk_objects(chunks, content, base_metadata)

    def _create_chunk_objects(
        self, chunks: List[str], original_content: str, base_metadata: Dict[str, Any]
    ) -> List[ChunkObject]:
        chunk_objects = []
        current_pos = 0
        for i, chunk_text in enumerate(chunks):
            start_pos = original_content.find(chunk_text, current_pos)
            if start_pos == -1:
                start_pos = current_pos
            end_pos = start_pos + len(chunk_text)
            chunk_metadata = {
                **base_metadata,
                "chunk_method": (
                    "semantic" if self.config.use_semantic_splitting else "simple"
                ),
                "total_chunks": len(chunks),
            }
            chunk_objects.append(
                ChunkObject(
                    content=chunk_text.strip(),
                    index=i,
                    start_char=start_pos,
                    end_char=end_pos,
                    metadata=chunk_metadata,
                )
            )
            current_pos = end_pos
        return chunk_objects


class SimpleChunker:
    """Simple non-semantic chunker for faster processing."""

    def __init__(self, config: ChunkingConfig):
        self.config = config

    def chunk_document(
        self,
        content: str,
        title: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[ChunkObject]:
        if not content.strip():
            return []
        base_metadata = {
            "title": title,
            "source": source,
            "chunk_method": "simple",
            **(metadata or {}),
        }
        paragraphs = re.split(r"\n\s*\n", content)
        chunks = []
        current_chunk = ""
        current_pos = 0
        chunk_index = 0
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            potential_chunk = (
                current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            )
            if len(potential_chunk) <= self.config.chunk_size:
                current_chunk = potential_chunk
            else:
                if current_chunk:
                    chunks.append(
                        self._create_chunk(
                            current_chunk,
                            chunk_index,
                            current_pos,
                            current_pos + len(current_chunk),
                            base_metadata.copy(),
                        )
                    )
                    overlap_start = max(
                        0, len(current_chunk) - self.config.chunk_overlap
                    )
                    current_pos += overlap_start
                    chunk_index += 1
                current_chunk = paragraph
        if current_chunk:
            chunks.append(
                self._create_chunk(
                    current_chunk,
                    chunk_index,
                    current_pos,
                    current_pos + len(current_chunk),
                    base_metadata.copy(),
                )
            )
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)
        return chunks

    def _create_chunk(
        self,
        content: str,
        index: int,
        start_pos: int,
        end_pos: int,
        metadata: Dict[str, Any],
    ) -> ChunkObject:
        return ChunkObject(
            content=content.strip(),
            index=index,
            start_char=start_pos,
            end_char=end_pos,
            metadata=metadata,
        )


# Factory function supporting Bible, semantic, and simple chunking
def create_chunker(config: ChunkingConfig):
    if config.mode == "bible":
        return AdvancedBiblicalChunker(config)
    elif config.use_semantic_splitting:
        return SemanticChunker(config)
    else:
        return SimpleChunker(config)


# Advanced Bible chunker (agentic, canonical)
class AdvancedBiblicalChunker:
    def __init__(self, config: ChunkingConfig):
        self.config = config
        self.embedding_client = embedding_client
        self.model = ingestion_model

    async def chunk_document(
        self,
        content: str,
        translation: str,
        book: str,
        chapter: int,
        verses: List[Tuple[int, str]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[UnifiedChunk]:
        chunks = []
        chunk_index = 0
        current_chunk = ""
        start_verse = None
        end_verse = None
        for verse_num, verse_text in verses:
            if start_verse is None:
                start_verse = verse_num
            current_chunk += verse_text + " "
            end_verse = verse_num
            if len(current_chunk.split()) >= self.config.chunk_size:
                chunk = UnifiedChunk(
                    content=current_chunk.strip(),
                    translation=translation,
                    book=book,
                    chapter=chapter,
                    start_verse=start_verse,
                    end_verse=end_verse,
                    chunk_index=chunk_index,
                    metadata=metadata or {},
                )
                chunks.append(chunk)
                chunk_index += 1
                current_chunk = ""
                start_verse = None
                end_verse = None
        if current_chunk:
            chunk = UnifiedChunk(
                content=current_chunk.strip(),
                translation=translation,
                book=book,
                chapter=chapter,
                start_verse=start_verse,
                end_verse=end_verse,
                chunk_index=chunk_index,
                metadata=metadata or {},
            )
            chunks.append(chunk)
        return chunks


# ...existing code...
