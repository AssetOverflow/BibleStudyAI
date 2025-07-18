from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid

from models import api_models, db_models
from database.timescale_db import get_db
from auth.security import get_current_user

router = APIRouter()


@router.post(
    "/", response_model=api_models.NoteInDB, status_code=status.HTTP_201_CREATED
)
async def create_note(
    note: api_models.NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    db_note = db_models.Note(**note.dict(), user_id=current_user.id)
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note


@router.get("/", response_model=List[api_models.NoteInDB])
async def read_notes(
    db: AsyncSession = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    result = await db.execute(
        select(db_models.Note).filter(db_models.Note.user_id == current_user.id)
    )
    notes = result.scalars().all()
    return notes


@router.get("/{note_id}", response_model=api_models.NoteInDB)
async def read_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    result = await db.execute(
        select(db_models.Note).filter(
            db_models.Note.id == note_id, db_models.Note.user_id == current_user.id
        )
    )
    note = result.scalars().first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=api_models.NoteInDB)
async def update_note(
    note_id: uuid.UUID,
    note: api_models.NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    result = await db.execute(
        select(db_models.Note).filter(
            db_models.Note.id == note_id, db_models.Note.user_id == current_user.id
        )
    )
    db_note = result.scalars().first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    for key, value in note.dict().items():
        setattr(db_note, key, value)

    await db.commit()
    await db.refresh(db_note)
    return db_note


@router.delete("/{note_id}", response_model=api_models.NoteInDB)
async def delete_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: db_models.User = Depends(get_current_user),
):
    result = await db.execute(
        select(db_models.Note).filter(
            db_models.Note.id == note_id, db_models.Note.user_id == current_user.id
        )
    )
    db_note = result.scalars().first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    await db.delete(db_note)
    await db.commit()
    return db_note
