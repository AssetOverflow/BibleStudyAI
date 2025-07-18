from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class AgentState:
    """Represents the current state of an agent"""

    agent_id: str
    name: str
    specialization: str
    status: str  # active, idle, processing, error
    current_task: Optional[str]
    conversation_context: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    last_updated: str
    memory_usage: int
    active_connections: List[str]


@dataclass
class ChuckMisslerPersona:
    """Embodies Chuck Missler's teaching style and knowledge"""

    name: str = "Dr. Chuck Missler"
    role: str = "Master Biblical Teacher"
    personality_traits: List[str] = None
    teaching_principles: Dict[str, str] = None
    signature_phrases: List[str] = None

    def __post_init__(self):
        if self.personality_traits is None:
            self.personality_traits = [
                "Warm and encouraging",
                "Scientifically rigorous",
                "Passionate about God's Word",
                "Integrates faith and reason",
                "Mathematically precise",
                "Historically grounded",
            ]

        if self.teaching_principles is None:
            self.teaching_principles = {
                "hermeneutics": "Scripture interprets Scripture",
                "approach": "Literal interpretation with scientific validation",
                "focus": "Integrated message system of the Bible",
                "methodology": "Rigorous scholarship with spiritual insight",
            }

        if self.signature_phrases is None:
            self.signature_phrases = [
                "The Bible is an extraterrestrial message",
                "Every detail is there by deliberate design",
                "God has a technology to get His message to us",
                "The Bible is an integrated message system",
            ]


@dataclass
class BiblicalQuery:
    """Represents a biblical query with context"""

    query: str
    context: Optional[Dict[str, Any]] = None
    agent_preference: Optional[str] = "chuck_missler"
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AgentResponse:
    """Represents an agent's response to a query"""

    agent_id: str
    response: str
    cross_references: List[str]
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class UserProfile:
    """Represents a user's profile and preferences"""

    name: str
    email: str
    experience_level: str
    study_interests: List[str]
    preferences: Dict[str, Any]
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class StudySession:
    """Represents a study session"""

    session_id: str
    user_id: str
    book: str
    chapter: int
    verses: List[int]
    notes: str
    insights: List[str]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
