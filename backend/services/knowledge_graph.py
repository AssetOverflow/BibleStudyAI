from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class BiblicalKnowledgeGraph:
    """Advanced knowledge graph for biblical concepts and relationships"""

    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.session = None

    async def initialize(self):
        """Initialize the knowledge graph with biblical ontology"""
        try:
            self.session = self.driver.session()
            await self.build_biblical_ontology()
            logger.info("Biblical Knowledge Graph initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge graph: {e}")
            raise

    async def build_biblical_ontology(self):
        """Build comprehensive biblical ontology"""
        try:
            # Create basic biblical entity types
            entity_types = [
                "Person",
                "Place",
                "Event",
                "Concept",
                "Book",
                "Chapter",
                "Verse",
                "Prophecy",
                "Miracle",
                "Parable",
                "Genealogy",
                "Covenant",
                "Law",
            ]

            for entity_type in entity_types:
                await self._create_entity_type(entity_type)

            # Create basic relationships
            relationships = [
                "APPEARS_IN",
                "REFERENCES",
                "FULFILLS",
                "PROPHESIES",
                "TEACHES",
                "LOCATED_IN",
                "RELATED_TO",
                "MENTIONS",
                "EXPLAINS",
                "CROSS_REFERENCES",
            ]

            for relationship in relationships:
                await self._create_relationship_type(relationship)

            logger.info("Biblical ontology created successfully")

        except Exception as e:
            logger.error(f"Failed to build biblical ontology: {e}")
            raise

    async def _create_entity_type(self, entity_type: str):
        """Create entity type in Neo4j"""
        try:
            query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{entity_type}) REQUIRE n.name IS UNIQUE"
            await self._execute_query(query)
        except Exception as e:
            logger.error(f"Failed to create entity type {entity_type}: {e}")

    async def _create_relationship_type(self, relationship_type: str):
        """Create relationship type in Neo4j"""
        try:
            # Neo4j doesn't require explicit relationship type creation
            # This is a placeholder for future enhancements
            pass
        except Exception as e:
            logger.error(f"Failed to create relationship type {relationship_type}: {e}")

    async def add_biblical_entity(self, entity_type: str, name: str, properties: Dict):
        """Add biblical entity to knowledge graph"""
        try:
            # Prepare properties for Cypher query
            props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])

            query = f"""
            MERGE (n:{entity_type} {{name: $name}})
            SET n += {{{props_str}}}
            RETURN n
            """

            params = {"name": name, **properties}
            result = await self._execute_query(query, params)

            logger.info(f"Added biblical entity: {entity_type} - {name}")
            return result

        except Exception as e:
            logger.error(f"Failed to add biblical entity {name}: {e}")
            raise

    async def create_relationship(
        self,
        entity1: str,
        entity2: str,
        relationship_type: str,
        properties: Dict = None,
    ):
        """Create relationship between entities"""
        try:
            props_str = ""
            if properties:
                props_str = (
                    "{" + ", ".join([f"{k}: ${k}" for k in properties.keys()]) + "}"
                )

            query = f"""
            MATCH (a {{name: $entity1}})
            MATCH (b {{name: $entity2}})
            MERGE (a)-[r:{relationship_type} {props_str}]->(b)
            RETURN r
            """

            params = {"entity1": entity1, "entity2": entity2}
            if properties:
                params.update(properties)

            result = await self._execute_query(query, params)

            logger.info(
                f"Created relationship: {entity1} -{relationship_type}-> {entity2}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            raise

    async def find_biblical_connections(
        self, concept: str, depth: int = 2
    ) -> List[Dict]:
        """Find related biblical concepts using graph traversal"""
        try:
            query = f"""
            MATCH path = (start {{name: $concept}})-[*1..{depth}]-(connected)
            RETURN DISTINCT connected.name as name, 
                   labels(connected) as types,
                   length(path) as distance,
                   [r in relationships(path) | type(r)] as relationship_path
            ORDER BY distance, connected.name
            LIMIT 50
            """

            result = await self._execute_query(query, {"concept": concept})

            connections = []
            for record in result:
                connections.append(
                    {
                        "name": record["name"],
                        "types": record["types"],
                        "distance": record["distance"],
                        "relationship_path": record["relationship_path"],
                    }
                )

            return connections

        except Exception as e:
            logger.error(f"Failed to find biblical connections for {concept}: {e}")
            return []

    async def find_cross_references(
        self, book: str, chapter: int, verse: Optional[int] = None
    ) -> List[str]:
        """Find cross-references for a biblical passage"""
        try:
            if verse:
                passage_name = f"{book} {chapter}:{verse}"
            else:
                passage_name = f"{book} {chapter}"

            query = """
            MATCH (passage {name: $passage_name})-[:CROSS_REFERENCES]-(ref)
            RETURN DISTINCT ref.name as reference
            ORDER BY ref.name
            LIMIT 20
            """

            result = await self._execute_query(query, {"passage_name": passage_name})

            cross_refs = [record["reference"] for record in result]

            # If no specific cross-references found, find conceptual connections
            if not cross_refs:
                cross_refs = await self._find_conceptual_connections(passage_name)

            return cross_refs

        except Exception as e:
            logger.error(f"Failed to find cross-references for {book} {chapter}: {e}")
            return []

    async def _find_conceptual_connections(self, passage_name: str) -> List[str]:
        """Find conceptual connections when direct cross-references aren't available"""
        try:
            # Extract concepts from passage and find related passages
            query = """
            MATCH (passage {name: $passage_name})-[:MENTIONS|TEACHES|EXPLAINS]-(concept)
            MATCH (concept)-[:MENTIONED_IN|TAUGHT_IN|EXPLAINED_IN]-(related_passage)
            WHERE related_passage.name <> $passage_name
            RETURN DISTINCT related_passage.name as reference
            ORDER BY reference
            LIMIT 10
            """

            result = await self._execute_query(query, {"passage_name": passage_name})
            return [record["reference"] for record in result]

        except Exception as e:
            logger.error(f"Failed to find conceptual connections: {e}")
            return []

    async def find_prophetic_patterns(self, prophecy_text: str) -> List[Dict]:
        """Find patterns in prophetic fulfillment"""
        try:
            # This is a simplified implementation
            # In a real system, this would use NLP to analyze the prophecy text

            query = """
            MATCH (prophecy:Prophecy)-[:FULFILLS]->(fulfillment:Event)
            WHERE prophecy.text CONTAINS $search_term
            RETURN prophecy.name as prophecy_name,
                   prophecy.text as prophecy_text,
                   fulfillment.name as fulfillment_name,
                   fulfillment.date as fulfillment_date
            ORDER BY fulfillment.date
            """

            # Extract key terms from prophecy text for search
            search_terms = prophecy_text.lower().split()[:5]  # First 5 words

            patterns = []
            for term in search_terms:
                result = await self._execute_query(query, {"search_term": term})
                for record in result:
                    patterns.append(
                        {
                            "prophecy_name": record["prophecy_name"],
                            "prophecy_text": record["prophecy_text"],
                            "fulfillment_name": record["fulfillment_name"],
                            "fulfillment_date": record["fulfillment_date"],
                            "search_term": term,
                        }
                    )

            return patterns

        except Exception as e:
            logger.error(f"Failed to find prophetic patterns: {e}")
            return []

    async def add_passage_with_context(
        self, book: str, chapter: int, verse: int, text: str, context: Dict
    ):
        """Add a biblical passage with its context to the knowledge graph"""
        try:
            passage_name = f"{book} {chapter}:{verse}"

            # Add the passage entity
            await self.add_biblical_entity(
                "Verse",
                passage_name,
                {
                    "book": book,
                    "chapter": chapter,
                    "verse": verse,
                    "text": text,
                    "created_at": datetime.now().isoformat(),
                },
            )

            # Add book entity if not exists
            await self.add_biblical_entity(
                "Book",
                book,
                {
                    "testament": context.get("testament", "unknown"),
                    "genre": context.get("genre", "unknown"),
                },
            )

            # Create relationships
            await self.create_relationship(passage_name, book, "BELONGS_TO")

            # Add themes and concepts
            if "themes" in context:
                for theme in context["themes"]:
                    await self.add_biblical_entity("Concept", theme, {"type": "theme"})
                    await self.create_relationship(passage_name, theme, "TEACHES")

            logger.info(f"Added passage with context: {passage_name}")

        except Exception as e:
            logger.error(f"Failed to add passage with context: {e}")
            raise

    async def _execute_query(self, query: str, params: Dict = None):
        """Execute a Cypher query safely"""
        try:
            if not self.session:
                self.session = self.driver.session()

            result = self.session.run(query, params or {})
            return list(result)

        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise

    async def close(self):
        """Close the database connection"""
        try:
            if self.session:
                self.session.close()
            if self.driver:
                self.driver.close()
            logger.info("Knowledge graph connection closed")
        except Exception as e:
            logger.error(f"Error closing knowledge graph connection: {e}")

    async def get_statistics(self) -> Dict:
        """Get knowledge graph statistics"""
        try:
            queries = {
                "total_nodes": "MATCH (n) RETURN count(n) as count",
                "total_relationships": "MATCH ()-[r]->() RETURN count(r) as count",
                "node_types": "MATCH (n) RETURN labels(n) as types, count(n) as count",
                "relationship_types": "MATCH ()-[r]->() RETURN type(r) as type, count(r) as count",
            }

            stats = {}
            for stat_name, query in queries.items():
                result = await self._execute_query(query)
                if stat_name in ["total_nodes", "total_relationships"]:
                    stats[stat_name] = result[0]["count"] if result else 0
                else:
                    stats[stat_name] = [dict(record) for record in result]

            return stats

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

    async def populate_with_sample_data(self):
        """Populate the knowledge graph with sample biblical data"""
        try:
            # Sample biblical entities
            sample_entities = [
                {
                    "type": "Person",
                    "name": "Jesus",
                    "properties": {"role": "Messiah", "testament": "New"},
                },
                {
                    "type": "Person",
                    "name": "David",
                    "properties": {"role": "King", "testament": "Old"},
                },
                {
                    "type": "Place",
                    "name": "Jerusalem",
                    "properties": {"significance": "Holy City"},
                },
                {
                    "type": "Book",
                    "name": "Genesis",
                    "properties": {"testament": "Old", "genre": "History"},
                },
                {
                    "type": "Book",
                    "name": "John",
                    "properties": {"testament": "New", "genre": "Gospel"},
                },
                {
                    "type": "Concept",
                    "name": "Salvation",
                    "properties": {"type": "theological"},
                },
                {
                    "type": "Concept",
                    "name": "Prophecy",
                    "properties": {"type": "theological"},
                },
            ]

            for entity in sample_entities:
                await self.add_biblical_entity(
                    entity["type"], entity["name"], entity["properties"]
                )

            # Sample relationships
            sample_relationships = [
                {"from": "Jesus", "to": "David", "type": "DESCENDED_FROM"},
                {"from": "Jesus", "to": "Jerusalem", "type": "MINISTERED_IN"},
                {"from": "John", "to": "Jesus", "type": "SPEAKS_ABOUT"},
                {"from": "Genesis", "to": "Prophecy", "type": "CONTAINS"},
                {"from": "Salvation", "to": "Jesus", "type": "THROUGH"},
            ]

            for rel in sample_relationships:
                await self.create_relationship(rel["from"], rel["to"], rel["type"])

            logger.info("Sample data populated successfully")

        except Exception as e:
            logger.error(f"Failed to populate sample data: {e}")
            raise
