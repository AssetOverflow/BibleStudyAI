from loguru import logger
from neo4j import AsyncSession

from ..services.bible_service import BibleService
from ..database.neo4j_graph import get_neo4j_session, Neo4jConnection


async def create_neo4j_constraints(session: AsyncSession):
    """Creates unique constraints in Neo4j to prevent duplicate nodes."""
    logger.info("Creating Neo4j constraints...")
    await session.run(
        "CREATE CONSTRAINT IF NOT EXISTS FOR (b:Book) REQUIRE b.name IS UNIQUE"
    )
    await session.run(
        "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE"
    )
    await session.run(
        "CREATE CONSTRAINT IF NOT EXISTS FOR (pl:Place) REQUIRE pl.name IS UNIQUE"
    )
    await session.run(
        "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE"
    )
    logger.success("Neo4j constraints created.")


async def ingest_bible_structure_to_neo4j():
    """Ingests the basic structure of the Bible (books and chapters) into Neo4j."""
    driver = await Neo4jConnection.get_driver()
    if not driver:
        logger.error("Cannot ingest to Neo4j, driver not available.")
        return

    async with driver.session() as session:
        await create_neo4j_constraints(session)

        bible_service = BibleService(parquet_dir="KoinoniaHouse/db/bibles/parquet/")
        # Using KJV as the base for structure
        translation = "KJV"
        logger.info(f"Ingesting Bible structure based on '{translation}' translation.")

        books = bible_service.get_books(translation)
        if not books:
            logger.error(
                f"Could not retrieve book list for '{translation}'. Aborting ingestion."
            )
            return

        for book_name in books:
            # Create Book node
            await session.run("MERGE (b:Book {name: $name})", name=book_name)

            chapters = bible_service.get_chapters(translation, book_name)
            for chapter_num in chapters:
                # Create Chapter node and link it to the Book
                await session.run(
                    """
                    MATCH (b:Book {name: $book_name})
                    MERGE (c:Chapter {book: $book_name, number: $chapter_num})
                    MERGE (b)-[:HAS_CHAPTER]->(c)
                    """,
                    book_name=book_name,
                    chapter_num=chapter_num,
                )
        logger.success("Finished ingesting Bible book and chapter structure to Neo4j.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(ingest_bible_structure_to_neo4j())
