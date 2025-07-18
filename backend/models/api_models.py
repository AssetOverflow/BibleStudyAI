from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime


class Book(BaseModel):
    id: str
    name: str
    chapters: int


class Verse(BaseModel):
    book: str
    chapter: int
    verse: int
    text: str


class VerseAnalysisRequest(BaseModel):
    book: str
    chapter: int
    verse: int


class VerseAnalysis(BaseModel):
    reference: str
    text: str
    analysis: str
    original_text: Optional[str] = None
    patterns: Optional[str] = None


class CrossRef(BaseModel):
    reference: str
    text: str


class ChatMessage(BaseModel):
    agent_id: str
    content: str


class ChatResponse(BaseModel):
    response: str


class Agent(BaseModel):
    id: str
    name: str
    role: str
    avatar: str
    greeting: str


class StudyProgress(BaseModel):
    title: str
    description: str
    progress: int


# RAG System Schemas
class RAGRequest(BaseModel):
    question: str
    user_id: Optional[str] = None  # Optional user context


class RAGResponse(BaseModel):
    answer: str
    context: dict  # The retrieved context for transparency


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: uuid.UUID

    class Config:
        orm_mode = True


class UserPublic(UserBase):
    id: uuid.UUID


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Note Schemas
class NoteBase(BaseModel):
    title: str
    content: str


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    pass


class NoteInDB(NoteBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
