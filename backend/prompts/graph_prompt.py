GRAPH_GENERATION_PROMPT = """
You are an expert theologian and a master knowledge graph architect. Your task is to analyze a given passage of biblical text and extract all significant entities and the relationships between them.

Return your findings as a single, well-formed JSON object with two keys: "nodes" and "edges".

**Node Schema:**
- Each node must have an "id" (a unique name or identifier for the entity) and a "label" (the type of entity).
- Valid node labels are: "Person", "Place", "Topic", "Event", "Book", "Chapter", "Verse".
- Nodes can have additional properties relevant to their type (e.g., a "Place" might have "region").

**Edge Schema:**
- Each edge must have a "source" (the id of the starting node), a "target" (the id of the ending node), and a "label" (the type of relationship).
- Relationship labels should be descriptive and in uppercase, e.g., "BORN_IN", "TRAVELLED_TO", "SPOKE_ABOUT", "PARTICIPATED_IN".

**Example Input Text:**
"In the first year of Cyrus king of Persia, that the word of the LORD by the mouth of Jeremiah might be fulfilled, the LORD stirred up the spirit of Cyrus king of Persia, so that he made a proclamation throughout all his kingdom and also put it in writing: 'Thus says Cyrus king of Persia: The LORD, the God of heaven, has given me all the kingdoms of the earth, and he has charged me to build him a house at Jerusalem, which is in Judah.'"

**Example JSON Output:**
{
  "nodes": [
    {"id": "Cyrus", "label": "Person", "properties": {"title": "King of Persia"}},
    {"id": "Jeremiah", "label": "Person", "properties": {"title": "Prophet"}},
    {"id": "Persia", "label": "Place", "properties": {}},
    {"id": "Jerusalem", "label": "Place", "properties": {"region": "Judah"}},
    {"id": "Judah", "label": "Place", "properties": {}},
    {"id": "Temple_Rebuilding", "label": "Event", "properties": {}}
  ],
  "edges": [
    {"source": "Cyrus", "target": "Persia", "label": "RULER_OF"},
    {"source": "Cyrus", "target": "Temple_Rebuilding", "label": "AUTHORIZED"},
    {"source": "Jeremiah", "target": "Temple_Rebuilding", "label": "PROPHESIED"},
    {"source": "Temple_Rebuilding", "target": "Jerusalem", "label": "LOCATED_IN"},
    {"source": "Jerusalem", "target": "Judah", "label": "LOCATED_IN"}
  ]
}

Now, analyze the following text and generate the corresponding JSON object:
---
{text}
"""

ENTITY_EXTRACTION_PROMPT = """
You are an expert in Natural Language Processing and Biblical Studies. Your task is to extract key entities from the provided text.
Focus on identifying specific names of people, places, significant theological concepts, and events.

Return your findings as a single, well-formed JSON object with a single key: "entities". The value should be a list of strings.
Do not return entities that are too generic (e.g., "the world", "a man"). Be specific.

Example Input Text:
"For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life. This was in Jerusalem."

Example JSON Output:
{
  "entities": ["God", "Son", "Jerusalem", "eternal life"]
}

Now, analyze the following text and generate the corresponding JSON object:
---
{text}
"""
