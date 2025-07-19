from typing import List, Dict, Any, Optional, Tuple
import re
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from loguru import logger


@dataclass
class BiblicalChunk:
    """Enhanced chunk model for biblical text with rich metadata."""

    id: str
    content: str
    translation: str
    book: str
    chapter: int
    start_verse: int
    end_verse: int
    chunk_index: int
    word_count: int
    char_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

        # Auto-calculate metrics if not provided
        if self.word_count == 0:
            self.word_count = len(self.content.split())
        if self.char_count == 0:
            self.char_count = len(self.content)

        # Add contextual metadata
        self.metadata.update(
            {
                "passage_reference": f"{self.book} {self.chapter}:{self.start_verse}-{self.end_verse}",
                "chunk_size": self.word_count,
                "testament": "old" if self._is_old_testament() else "new",
            }
        )

    def _is_old_testament(self) -> bool:
        """Determine if this chunk is from Old Testament."""
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
        return self.book in ot_books


@dataclass
class ChunkingConfig:
    """Configuration for biblical text chunking."""

    target_chunk_size: int = 250  # words
    size_variance: int = 50  # words
    overlap_verses: int = 1  # number of verses to overlap
    min_chunk_size: int = 100  # minimum words
    max_chunk_size: int = 400  # maximum words
    preserve_verse_boundaries: bool = True
    semantic_splitting: bool = True
    include_context: bool = True
    context_window: int = 2  # verses before/after for context


class AdvancedBiblicalChunker:
    """
    Advanced biblical text chunker optimized for agentic RAG + knowledge graph.

    Features:
    - Semantic boundary preservation
    - Biblical structure awareness (verses, chapters, books)
    - Rich metadata extraction
    - Async processing
    - Contextual overlapping
    - Cross-reference preservation
    """

    def __init__(self, config: ChunkingConfig = None):
        """Initialize the chunker with configuration."""
        self.config = config or ChunkingConfig()
        logger.info(f"Advanced Biblical Chunker initialized with config: {self.config}")

    async def chunk_bible_data(
        self, bible_df, translation: str, book_filter: Optional[List[str]] = None
    ) -> List[BiblicalChunk]:
        """
        Chunk entire Bible data with async processing.

        Args:
            bible_df: DataFrame with Bible data
            translation: Translation name (e.g., "KJV")
            book_filter: Optional list of books to process

        Returns:
            List of BiblicalChunk objects
        """
        logger.info(f"Starting biblical chunking for {translation}")

        if book_filter:
            bible_df = bible_df[bible_df["book"].isin(book_filter)]

        # Group by book for processing
        chunks = []
        books = bible_df["book"].unique()

        # Process books concurrently
        tasks = []
        for book in books:
            book_data = bible_df[bible_df["book"] == book]
            task = self._chunk_book_async(book_data, translation, book)
            tasks.append(task)

        # Gather results
        book_chunks_list = await asyncio.gather(*tasks)

        # Flatten results
        chunk_index = 0
        for book_chunks in book_chunks_list:
            for chunk in book_chunks:
                chunk.chunk_index = chunk_index
                chunk_index += 1
                chunks.append(chunk)

        logger.success(f"Created {len(chunks)} chunks for {translation}")
        return chunks

    async def _chunk_book_async(
        self, book_df, translation: str, book: str
    ) -> List[BiblicalChunk]:
        """Process a single book asynchronously."""

        chunks = []
        chapters = sorted(book_df["chapter"].unique())

        for chapter in chapters:
            chapter_data = book_df[book_df["chapter"] == chapter]
            chapter_chunks = await self._chunk_chapter(
                chapter_data, translation, book, chapter
            )
            chunks.extend(chapter_chunks)

        return chunks

    async def _chunk_chapter(
        self, chapter_df, translation: str, book: str, chapter: int
    ) -> List[BiblicalChunk]:
        """Chunk a single chapter with semantic awareness."""

        # Sort verses
        chapter_df = chapter_df.sort_values("verse")
        verses = chapter_df.to_dict("records")

        if not verses:
            return []

        chunks = []
        current_chunk_verses = []
        current_word_count = 0

        for i, verse_data in enumerate(verses):
            verse_text = verse_data["text"]
            verse_word_count = len(verse_text.split())

            # Check if adding this verse would exceed max size
            if (
                current_word_count + verse_word_count > self.config.max_chunk_size
                and current_chunk_verses
            ):

                # Create chunk from current verses
                chunk = await self._create_chunk_from_verses(
                    current_chunk_verses, translation, book, chapter
                )
                chunks.append(chunk)

                # Start new chunk with overlap
                if self.config.overlap_verses > 0:
                    overlap_verses = current_chunk_verses[-self.config.overlap_verses :]
                    current_chunk_verses = overlap_verses
                    current_word_count = sum(
                        len(v["text"].split()) for v in overlap_verses
                    )
                else:
                    current_chunk_verses = []
                    current_word_count = 0

            current_chunk_verses.append(verse_data)
            current_word_count += verse_word_count

        # Handle remaining verses
        if current_chunk_verses:
            if (
                current_word_count >= self.config.min_chunk_size or not chunks
            ):  # Always include if it's the only chunk
                chunk = await self._create_chunk_from_verses(
                    current_chunk_verses, translation, book, chapter
                )
                chunks.append(chunk)
            else:
                # Merge with previous chunk if too small
                if chunks:
                    last_chunk = chunks[-1]
                    extended_content = (
                        last_chunk.content
                        + " "
                        + " ".join(v["text"] for v in current_chunk_verses)
                    )
                    last_chunk.content = extended_content
                    last_chunk.end_verse = current_chunk_verses[-1]["verse"]
                    last_chunk.word_count = len(extended_content.split())
                    last_chunk.char_count = len(extended_content)

        return chunks

    async def _create_chunk_from_verses(
        self, verses: List[Dict], translation: str, book: str, chapter: int
    ) -> BiblicalChunk:
        """Create a BiblicalChunk from a list of verses."""

        if not verses:
            raise ValueError("Cannot create chunk from empty verses")

        # Combine verse texts
        content = " ".join(verse["text"] for verse in verses)

        # Extract metadata
        start_verse = verses[0]["verse"]
        end_verse = verses[-1]["verse"]

        # Collect cross-references and Strong's numbers
        cross_refs = []
        strongs_numbers = []

        for verse in verses:
            if verse.get("cross_references"):
                cross_refs.extend(verse["cross_references"])
            if verse.get("strongs_numbers"):
                strongs_numbers.append(verse["strongs_numbers"])

        # Create rich metadata
        metadata = {
            "verses_included": [v["verse"] for v in verses],
            "verse_count": len(verses),
            "cross_references": list(set(cross_refs)) if cross_refs else [],
            "strongs_numbers": [s for s in strongs_numbers if s],
            "processing_timestamp": datetime.now().isoformat(),
        }

        # Add contextual information if enabled
        if self.config.include_context:
            metadata["context"] = await self._extract_context(
                book, chapter, start_verse, end_verse
            )

        chunk = BiblicalChunk(
            id=str(uuid.uuid4()),
            content=content,
            translation=translation,
            book=book,
            chapter=chapter,
            start_verse=start_verse,
            end_verse=end_verse,
            chunk_index=0,  # Will be set later
            word_count=len(content.split()),
            char_count=len(content),
            metadata=metadata,
        )

        return chunk

    async def _extract_context(
        self, book: str, chapter: int, start_verse: int, end_verse: int
    ) -> Dict[str, Any]:
        """Extract contextual information for better understanding."""

        context = {
            "section_type": self._identify_section_type(book, chapter),
            "literary_genre": self._identify_genre(book),
            "historical_period": self._get_historical_period(book),
            "theological_themes": self._extract_themes(book, chapter),
        }

        return context

    def _identify_section_type(self, book: str, chapter: int) -> str:
        """Identify the type of biblical section."""

        # This is a simplified version - could be enhanced with more sophisticated logic
        narrative_books = {
            "Genesis",
            "Exodus",
            "Numbers",
            "Joshua",
            "Judges",
            "1 Samuel",
            "2 Samuel",
            "1 Kings",
            "2 Kings",
            "Matthew",
            "Mark",
            "Luke",
            "John",
            "Acts",
        }
        poetry_books = {"Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon"}
        prophetic_books = {
            "Isaiah",
            "Jeremiah",
            "Ezekiel",
            "Daniel",
            "Hosea",
            "Joel",
            "Amos",
        }
        law_books = {"Leviticus", "Deuteronomy"}
        epistle_books = {
            "Romans",
            "1 Corinthians",
            "2 Corinthians",
            "Galatians",
            "Ephesians",
        }

        if book in narrative_books:
            return "narrative"
        elif book in poetry_books:
            return "poetry"
        elif book in prophetic_books:
            return "prophecy"
        elif book in law_books:
            return "law"
        elif book in epistle_books:
            return "epistle"
        else:
            return "other"

    def _identify_genre(self, book: str) -> str:
        """Identify literary genre of the book."""

        genres = {
            "Genesis": "narrative_origins",
            "Exodus": "narrative_law",
            "Psalms": "poetry_worship",
            "Proverbs": "wisdom_literature",
            "Isaiah": "major_prophet",
            "Matthew": "gospel",
            "Romans": "epistle_doctrinal",
            "Revelation": "apocalyptic",
        }

        return genres.get(book, "general")

    def _get_historical_period(self, book: str) -> str:
        """Get the historical period of the book."""

        periods = {
            "Genesis": "patriarchal",
            "Exodus": "exodus_wilderness",
            "Joshua": "conquest",
            "Judges": "judges",
            "1 Samuel": "united_monarchy",
            "1 Kings": "divided_monarchy",
            "Isaiah": "pre_exilic",
            "Ezra": "post_exilic",
            "Matthew": "gospel_period",
            "Acts": "early_church",
            "Romans": "apostolic",
        }

        return periods.get(book, "unknown")

    def _extract_themes(self, book: str, chapter: int) -> List[str]:
        """Extract major theological themes."""

        # Simplified theme extraction - could be enhanced with NLP
        book_themes = {
            "Genesis": ["creation", "covenant", "fall", "redemption"],
            "Exodus": ["deliverance", "covenant", "law", "worship"],
            "Psalms": ["worship", "prayer", "trust", "praise"],
            "Isaiah": ["judgment", "salvation", "messiah", "restoration"],
            "Matthew": ["kingdom", "discipleship", "messiah", "teaching"],
            "Romans": ["salvation", "righteousness", "grace", "faith"],
        }

        return book_themes.get(book, ["general_theology"])

    async def chunk_single_passage(
        self,
        text: str,
        translation: str,
        book: str,
        chapter: int,
        verse: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BiblicalChunk:
        """Chunk a single passage for testing or specific use."""

        chunk_metadata = metadata or {}
        chunk_metadata.update(
            {"single_passage": True, "processing_timestamp": datetime.now().isoformat()}
        )

        chunk = BiblicalChunk(
            id=str(uuid.uuid4()),
            content=text,
            translation=translation,
            book=book,
            chapter=chapter,
            start_verse=verse,
            end_verse=verse,
            chunk_index=0,
            word_count=len(text.split()),
            char_count=len(text),
            metadata=chunk_metadata,
        )

        return chunk


# Factory function for easy instantiation
def create_biblical_chunker(config: ChunkingConfig = None) -> AdvancedBiblicalChunker:
    """Create an optimized biblical chunker instance."""
    return AdvancedBiblicalChunker(config)


# For backward compatibility
class HybridChunker:
    """Legacy chunker class for backward compatibility."""

    def __init__(
        self,
        target_chunk_size: int = 300,
        size_variance: int = 50,
        overlap_sentences: int = 2,
    ):
        self.target_chunk_size = target_chunk_size
        self.size_variance = size_variance
        self.overlap_sentences = overlap_sentences
        logger.warning(
            "Using legacy HybridChunker. Consider upgrading to AdvancedBiblicalChunker."
        )

    def chunk_text(self, text: str) -> List[str]:
        """Legacy chunking method."""
        # Simple implementation for backward compatibility
        sentences = text.split(". ")
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len((current_chunk + sentence).split()) <= self.target_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


# Example usage and testing
if __name__ == "__main__":
    import pandas as pd

    async def test_chunker():
        """Test the chunker with sample data."""

        # Create sample Bible data
        sample_data = {
            "translation": ["KJV"] * 6,
            "book": ["Genesis"] * 6,
            "chapter": [1] * 6,
            "verse": [1, 2, 3, 4, 5, 6],
            "text": [
                "In the beginning God created the heaven and the earth.",
                "And the earth was without form, and void; and darkness was upon the face of the deep.",
                "And the Spirit of God moved upon the face of the waters.",
                "And God said, Let there be light: and there was light.",
                "And God saw the light, that it was good: and God divided the light from the darkness.",
                "And God called the light Day, and the darkness he called Night.",
            ],
            "cross_references": [[], [], [], [], [], []],
            "strongs_numbers": [None] * 6,
        }

        df = pd.DataFrame(sample_data)

        # Test chunker
        config = ChunkingConfig(target_chunk_size=50, size_variance=20)
        chunker = create_biblical_chunker(config)

        chunks = await chunker.chunk_bible_data(df, "KJV")

        print(f"\nCreated {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks):
            print(f"\n--- CHUNK {i+1} ---")
            print(f"Reference: {chunk.metadata['passage_reference']}")
            print(f"Words: {chunk.word_count}")
            print(f"Content: {chunk.content[:100]}...")
            print(f"Metadata keys: {list(chunk.metadata.keys())}")

    # Run test
    asyncio.run(test_chunker())
