from fastapi import APIRouter, Depends
from typing import List
from ..services.bible_service import BibleService
from ..models import api_models

router = APIRouter()

# This is a simplified way to manage the service instance.
# In a larger application, you might use a more robust dependency injection system.
bible_service = BibleService(parquet_dir="cleaned_bibles_pipeline/parquet_output/")


@router.get("/translations", response_model=List[str])
async def get_translations():
    return bible_service.get_translations()


@router.get("/{translation}/books", response_model=List[str])
async def get_books(translation: str):
    return bible_service.get_books(translation)


@router.get("/{translation}/{book}/chapters", response_model=List[int])
async def get_chapters(translation: str, book: str):
    return bible_service.get_chapters(translation, book)


@router.get(
    "/{translation}/{book}/{chapter}/verses", response_model=List[api_models.Verse]
)
async def get_verses(translation: str, book: str, chapter: int):
    verses = bible_service.get_verses(translation, book, chapter)
    return [api_models.Verse(**v) for v in verses]


@router.get("/{translation}/search", response_model=List[api_models.Verse])
async def search_bible(translation: str, query: str):
    results = bible_service.search(translation, query)
    return [api_models.Verse(**r) for r in results]
