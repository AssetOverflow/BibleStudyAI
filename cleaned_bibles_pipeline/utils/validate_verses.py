import json
from pathlib import Path

# Canonical verse counts for validation
EXPECTED_VERSES = {
    "Genesis": {
        1: 31,
        2: 25,
        3: 24,
        # ... Add all chapters and verse counts for Genesis
    },
    "Exodus": {
        1: 22,
        2: 25,
        # ... Add all chapters and verse counts for Exodus
    },
    # Add all books and their chapters with verse counts
}


def validate_verses(file_path):
    """Validate the verse counts in a Bible JSON file."""
    with open(file_path, "r") as f:
        data = json.load(f)

    issues = []

    # Validate Old Testament
    old_testament_books = data.get("old_testament", {}).get("books", {})
    for book, book_data in old_testament_books.items():
        expected_chapters = EXPECTED_VERSES.get(book, {})
        chapters = book_data.get("chapters", {})

        for chapter, verses in chapters.items():
            chapter_number = int(chapter)
            expected_verse_count = expected_chapters.get(chapter_number)
            if expected_verse_count is None:
                issues.append(f"Unexpected chapter {chapter_number} in book {book}")
                continue

            actual_verse_count = len(verses.get("verses", {}))
            if actual_verse_count != expected_verse_count:
                issues.append(
                    f"Book {book} Chapter {chapter_number} has {actual_verse_count} verses (expected {expected_verse_count})"
                )

    # Validate New Testament
    new_testament_books = data.get("new_testament", {}).get("books", {})
    for book, book_data in new_testament_books.items():
        expected_chapters = EXPECTED_VERSES.get(book, {})
        chapters = book_data.get("chapters", {})

        for chapter, verses in chapters.items():
            chapter_number = int(chapter)
            expected_verse_count = expected_chapters.get(chapter_number)
            if expected_verse_count is None:
                issues.append(f"Unexpected chapter {chapter_number} in book {book}")
                continue

            actual_verse_count = len(verses.get("verses", {}))
            if actual_verse_count != expected_verse_count:
                issues.append(
                    f"Book {book} Chapter {chapter_number} has {actual_verse_count} verses (expected {expected_verse_count})"
                )

    return issues


if __name__ == "__main__":
    # Path to the JSON file
    json_file = Path(
        "/Users/joshuashay/Desktop/holybible/data/json/cleaned/clean_American_Standard_Version_1901_ASV.json"
    )

    # Validate the file
    validation_issues = validate_verses(json_file)

    if validation_issues:
        print("Validation Issues:")
        for issue in validation_issues:
            print(f"- {issue}")
    else:
        print("No issues found. The verse counts are valid.")
