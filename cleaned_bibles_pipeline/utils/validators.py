"""
Bible data validation utilities.
Ensures integrity and accuracy of Bible objects, chapters, verses, and references.
"""

from holybible.models.bible import Bible, Testament, Book, Chapter, Verse, VerseRef, BibleTranslation, TestamentType
from typing import List, Optional

class ValidationError(Exception):
    pass

def validate_bible(bible: Bible) -> None:
    """Validate the structure and content of a Bible object."""
    if not isinstance(bible.translation, BibleTranslation):
        raise ValidationError("Bible translation is not a valid BibleTranslation enum.")
    for testament in [bible.old_testament, bible.new_testament]:
        validate_testament(testament)

def validate_testament(testament: Testament) -> None:
    if not isinstance(testament.type, TestamentType):
        raise ValidationError(f"Testament type is invalid: {testament.type}")
    for book in testament.books.values():
        validate_book(book, testament.type)

def validate_book(book: Book, expected_testament: TestamentType) -> None:
    if book.testament != expected_testament:
        raise ValidationError(f"Book {book.name} is in the wrong testament: {book.testament} != {expected_testament}")
    for chapter in book.chapters.values():
        validate_chapter(chapter, book.name)

def validate_chapter(chapter: Chapter, expected_book: str) -> None:
    if chapter.book != expected_book:
        raise ValidationError(f"Chapter {chapter.number} has book {chapter.book}, expected {expected_book}")
    for verse in chapter.verses.values():
        validate_verse(verse, chapter.book, chapter.number)

def validate_verse(verse: Verse, expected_book: str, expected_chapter: int) -> None:
    ref = verse.reference
    if ref.book != expected_book or ref.chapter != expected_chapter or not isinstance(ref.verse, int):
        raise ValidationError(f"Verse reference mismatch: {ref} vs {expected_book} {expected_chapter}")
    if not verse.text or not isinstance(verse.text, str):
        raise ValidationError(f"Verse text missing or not a string: {ref}")
    if not isinstance(verse.translation, BibleTranslation):
        raise ValidationError(f"Verse translation is invalid: {verse.translation}")
    # Optionally, validate cross references
    for cref in verse.cross_references:
        if not isinstance(cref, VerseRef):
            raise ValidationError(f"Cross reference is not a VerseRef: {cref}")

def validate_bible_strict(bible: Bible) -> None:
    """Validate Bible and ensure every book, chapter, and verse is present and in canonical order (optional strict mode)."""
    from holybible.utils.book_mapping import CANONICAL_BOOK_NAMES
    # Check all canonical books are present
    all_books = list(bible.old_testament.books.keys()) + list(bible.new_testament.books.keys())
    missing = [b for b in CANONICAL_BOOK_NAMES if b not in all_books]
    if missing:
        raise ValidationError(f"Missing canonical books: {missing}")

    # Check for duplicate books
    if len(all_books) != len(set(all_books)):
        raise ValidationError("Duplicate book names detected.")

    # Check each book for chapter and verse continuity and order
    for testament in [bible.old_testament, bible.new_testament]:
        for book_name in testament.books:
            book = testament.books[book_name]
            chapter_numbers = sorted(book.chapters.keys())
            # Chapters must start at 1 and be continuous
            if chapter_numbers and (chapter_numbers[0] != 1 or chapter_numbers != list(range(1, len(chapter_numbers) + 1))):
                raise ValidationError(f"Chapters in {book.name} are not continuous or do not start at 1: {chapter_numbers}")
            seen_chapters = set()
            for chap_num in chapter_numbers:
                if chap_num in seen_chapters:
                    raise ValidationError(f"Duplicate chapter number {chap_num} in book {book.name}")
                seen_chapters.add(chap_num)
                chapter = book.chapters[chap_num]
                verse_numbers = sorted(chapter.verses.keys())
                # Verses must start at 1 and be continuous
                if verse_numbers and (verse_numbers[0] != 1 or verse_numbers != list(range(1, len(verse_numbers) + 1))):
                    raise ValidationError(f"Verses in {book.name} {chap_num} are not continuous or do not start at 1: {verse_numbers}")
                seen_verses = set()
                for v_num in verse_numbers:
                    if v_num in seen_verses:
                        raise ValidationError(f"Duplicate verse number {v_num} in {book.name} {chap_num}")
                    seen_verses.add(v_num)
                    verse = chapter.verses[v_num]
                    # Check verse reference matches location
                    ref = verse.reference
                    if ref.book != book.name or ref.chapter != chap_num or ref.verse != v_num:
                        raise ValidationError(f"Verse reference mismatch in {book.name} {chap_num}:{v_num} -> {ref}")
    # Check for empty chapters or verses
    for testament in [bible.old_testament, bible.new_testament]:
        for book_name, book in testament.books.items():
            if not book.chapters:
                raise ValidationError(f"Book {book_name} has no chapters.")
            for chap_num, chapter in book.chapters.items():
                if not chapter.verses:
                    raise ValidationError(f"Chapter {chap_num} in {book_name} has no verses.")

    # Check for missing books (already checked above), and extra books not in canonical list
    canonical_set = set(CANONICAL_BOOK_NAMES)
    extra_books = [b for b in all_books if b not in canonical_set]
    if extra_books:
        raise ValidationError(f"Extra books found not in canonical list: {extra_books}")
