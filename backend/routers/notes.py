from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from .. import models, schemas
from ..database import get_db
from ..auth.security import get_current_user

router = APIRouter()


@router.post("/", response_model=schemas.NoteInDB)
def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_note = models.Note(**note.dict(), user_id=current_user.id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.get("/", response_model=List[schemas.NoteInDB])
def read_notes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Note).filter(models.Note.user_id == current_user.id).all()


@router.get("/{note_id}", response_model=schemas.NoteInDB)
def read_note(
    note_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.user_id == current_user.id)
        .first()
    )
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note


@router.put("/{note_id}", response_model=schemas.NoteInDB)
def update_note(
    note_id: uuid.UUID,
    note: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.user_id == current_user.id)
        .first()
    )
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    for var, value in vars(note).items():
        setattr(db_note, var, value) if value else None

    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.delete("/{note_id}", response_model=schemas.NoteInDB)
def delete_note(
    note_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.user_id == current_user.id)
        .first()
    )
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(db_note)
    db.commit()
    return db_note
