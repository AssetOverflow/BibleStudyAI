from fastapi import APIRouter, Depends, HTTPException
from typing import List
from services.bible_service import BibleService
from models import api_models

router = APIRouter()

# This is a simplified way to manage the service instance.
# In a larger application, you might use a more robust dependency injection system.
bible_service = BibleService(parquet_dir="db/bibles/parquet/")


def get_bible_service():
    return bible_service


@router.get("/translations", response_model=List[str])
async def get_translations(service: BibleService = Depends(get_bible_service)):
    return service.get_translations()


@router.get("/{translation}/books", response_model=List[str])
async def get_books(
    translation: str, service: BibleService = Depends(get_bible_service)
):
    books = service.get_books(translation)
    if books is None:
        raise HTTPException(status_code=404, detail="Translation not found")
    return books


@router.get("/{translation}/{book}/chapters", response_model=List[int])
async def get_chapters(
    translation: str, book: str, service: BibleService = Depends(get_bible_service)
):
    chapters = service.get_chapters(translation, book)
    if chapters is None:
        raise HTTPException(status_code=404, detail="Book or translation not found")
    return chapters


@router.get(
    "/{translation}/{book}/{chapter}/verses", response_model=List[api_models.Verse]
)
async def get_verses(
    translation: str,
    book: str,
    chapter: int,
    service: BibleService = Depends(get_bible_service),
):
    verses = service.get_verses(translation, book, chapter)
    if verses is None:
        raise HTTPException(
            status_code=404, detail="Chapter, book, or translation not found"
        )
    return [api_models.Verse(**v) for v in verses]


@router.get("/{translation}/search", response_model=List[api_models.Verse])
async def search_bible(
    translation: str, query: str, service: BibleService = Depends(get_bible_service)
):
    results = service.search(translation, query)
    if results is None:
        raise HTTPException(status_code=404, detail="Translation not found")
    return [api_models.Verse(**r) for r in results]
