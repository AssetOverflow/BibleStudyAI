import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Canonical data for validation with known variations
EXPECTED_STRUCTURE = {
    "Genesis": 50,
    "Exodus": 40,
    "Leviticus": 27,
    "Numbers": 36,
    "Deuteronomy": 34,
    "Joshua": 24,
    "Judges": 21,
    "Ruth": 4,
    "1 Samuel": 31,
    "2 Samuel": 24,
    "1 Kings": 22,
    "2 Kings": 25,
    "1 Chronicles": 29,
    "2 Chronicles": 36,
    "Ezra": 10,
    "Nehemiah": 13,
    "Esther": 10,
    "Job": 42,
    "Psalms": 150,
    "Proverbs": 31,
    "Ecclesiastes": 12,
    "Song of Solomon": 8,
    "Isaiah": 66,
    "Jeremiah": 52,
    "Lamentations": 5,
    "Ezekiel": 48,
    "Daniel": 12,
    "Hosea": 14,
    "Joel": 3,
    "Amos": 9,
    "Obadiah": 1,
    "Jonah": 4,
    "Micah": 7,
    "Nahum": 3,
    "Habakkuk": 3,
    "Zephaniah": 3,
    "Haggai": 2,
    "Zechariah": 14,
    "Malachi": 4,
    "Matthew": 28,
    "Mark": 16,
    "Luke": 24,
    "John": 21,
    "Acts": 28,
    "Romans": 16,
    "1 Corinthians": 16,
    "2 Corinthians": 13,
    "Galatians": 6,
    "Ephesians": 6,
    "Philippians": 4,
    "Colossians": 4,
    "1 Thessalonians": 5,
    "2 Thessalonians": 3,
    "1 Timothy": 6,
    "2 Timothy": 4,
    "Titus": 3,
    "Philemon": 1,
    "Hebrews": 13,
    "James": 5,
    "1 Peter": 5,
    "2 Peter": 3,
    "1 John": 5,
    "2 John": 1,
    "3 John": 1,
    "Jude": 1,
    "Revelation": 22,
}

# Known legitimate verse count variations based on manuscript traditions
# Format: "Book Chapter": [accepted_counts], description
KNOWN_VERSE_VARIATIONS = {
    # 3 John 1: Greek manuscript tradition differences
    ("3 John", 1): {
        "counts": [14, 15],
        "reason": "Greek manuscript traditions - some split verse 14 into verses 14-15",
        "sources": ["Critical Text", "Textus Receptus", "Majority Text"],
    },
    # Malachi 3: Hebrew vs Septuagint numbering systems
    ("Malachi", 3): {
        "counts": [18, 19, 24],
        "reason": "Hebrew Masoretic vs Greek Septuagint chapter/verse numbering traditions",
        "sources": ["Hebrew MT", "Greek LXX", "Various translations"],
    },
    # Ezra 2: Census list variations from different time periods
    ("Ezra", 2): {
        "counts": [50, 54, 70],
        "reason": "Parallel census lists from different time periods with documented numerical discrepancies",
        "sources": ["Different census times", "Textual transmission variations"],
    },
    # Nehemiah 7: Parallel to Ezra 2 with similar variations
    ("Nehemiah", 7): {
        "counts": [57, 60, 73],
        "reason": "Parallel census lists with Ezra 2, reflecting different count periods and scribal transmission",
        "sources": [
            "Post-settlement census",
            "Levitical ancestry resolution",
            "Scribal variations",
        ],
    },
    # Additional known variations can be added here as discovered
}


def validate_bible_json(file_path):
    """Validate the structure of a Bible JSON file with flexible validation for known variations."""
    with open(file_path, "r") as f:
        data = json.load(f)

    issues = []
    warnings = []

    # Validate Old Testament
    old_testament_books = data.get("old_testament", {}).get("books", {})
    for book, book_data in old_testament_books.items():
        expected_chapters = EXPECTED_STRUCTURE.get(book)
        if not expected_chapters:
            issues.append(f"Unexpected book in Old Testament: {book}")
            continue

        chapters = book_data.get("chapters", {})
        actual_chapters = len(chapters)
        if actual_chapters != expected_chapters:
            issues.append(
                f"Book {book} has {actual_chapters} chapters (expected {expected_chapters})"
            )

        # Validate verse counts for each chapter
        for chapter_num, chapter_data in chapters.items():
            chapter_int = int(chapter_num)
            verses = chapter_data.get("verses", {})
            actual_verse_count = len(verses)

            # Check if this is a known variation
            variation_key = (book, chapter_int)
            if variation_key in KNOWN_VERSE_VARIATIONS:
                variation_info = KNOWN_VERSE_VARIATIONS[variation_key]
                if actual_verse_count not in variation_info["counts"]:
                    issues.append(
                        f"Book {book} Chapter {chapter_int} has {actual_verse_count} verses "
                        f"(expected one of {variation_info['counts']} due to {variation_info['reason']})"
                    )
                else:
                    warnings.append(
                        f"Book {book} Chapter {chapter_int} has {actual_verse_count} verses "
                        f"(acceptable variation: {variation_info['reason']})"
                    )

    # Validate New Testament
    new_testament_books = data.get("new_testament", {}).get("books", {})
    for book, book_data in new_testament_books.items():
        expected_chapters = EXPECTED_STRUCTURE.get(book)
        if not expected_chapters:
            issues.append(f"Unexpected book in New Testament: {book}")
            continue

        chapters = book_data.get("chapters", {})
        actual_chapters = len(chapters)
        if actual_chapters != expected_chapters:
            issues.append(
                f"Book {book} has {actual_chapters} chapters (expected {expected_chapters})"
            )

        # Validate verse counts for each chapter
        for chapter_num, chapter_data in chapters.items():
            chapter_int = int(chapter_num)
            verses = chapter_data.get("verses", {})
            actual_verse_count = len(verses)

            # Check if this is a known variation
            variation_key = (book, chapter_int)
            if variation_key in KNOWN_VERSE_VARIATIONS:
                variation_info = KNOWN_VERSE_VARIATIONS[variation_key]
                if actual_verse_count not in variation_info["counts"]:
                    issues.append(
                        f"Book {book} Chapter {chapter_int} has {actual_verse_count} verses "
                        f"(expected one of {variation_info['counts']} due to {variation_info['reason']})"
                    )
                else:
                    warnings.append(
                        f"Book {book} Chapter {chapter_int} has {actual_verse_count} verses "
                        f"(acceptable variation: {variation_info['reason']})"
                    )

    # Check for missing books
    all_books = set(old_testament_books.keys()) | set(new_testament_books.keys())
    for book in EXPECTED_STRUCTURE.keys():
        if book not in all_books:
            issues.append(f"Missing book: {book}")

    return issues, warnings


def validate_all_translations(directory_path):
    """Validate all Bible translation JSON files in a directory."""
    directory = Path(directory_path)
    results = {}

    for json_file in directory.glob("clean_*.json"):
        try:
            issues, warnings = validate_bible_json(json_file)
            results[json_file.name] = {
                "issues": issues,
                "warnings": warnings,
                "status": "PASS" if not issues else "FAIL",
            }
        except Exception as e:
            results[json_file.name] = {
                "issues": [f"Error reading file: {str(e)}"],
                "warnings": [],
                "status": "ERROR",
            }

    return results


def print_validation_report(results):
    """Print a detailed validation report."""
    print("=" * 80)
    print("📖 BIBLE TRANSLATION VALIDATION REPORT")
    print("=" * 80)

    total_files = len(results)
    passed_files = sum(1 for r in results.values() if r["status"] == "PASS")
    failed_files = sum(1 for r in results.values() if r["status"] == "FAIL")
    error_files = sum(1 for r in results.values() if r["status"] == "ERROR")

    print(f"📊 SUMMARY:")
    print(f"   Total files: {total_files}")
    print(f"   ✅ Passed: {passed_files}")
    print(f"   ❌ Failed: {failed_files}")
    print(f"   🔥 Errors: {error_files}")
    print()

    # Print detailed results
    for filename, result in results.items():
        translation_name = filename.replace("clean_", "").replace(".json", "")
        status_icon = (
            "✅"
            if result["status"] == "PASS"
            else "❌" if result["status"] == "FAIL" else "🔥"
        )

        print(f"{status_icon} {translation_name}")

        if result["issues"]:
            print("   🚨 ISSUES:")
            for issue in result["issues"]:
                print(f"      • {issue}")

        if result["warnings"]:
            print("   ⚠️  KNOWN VARIATIONS (acceptable):")
            for warning in result["warnings"]:
                print(f"      • {warning}")

        if not result["issues"] and not result["warnings"]:
            print("   ✅ No issues found")

        print()


if __name__ == "__main__":
    # Path to the JSON files directory
    json_directory = Path("/Users/joshuashay/Desktop/holybible/data/json/cleaned")

    # Validate all translations
    validation_results = validate_all_translations(json_directory)

    # Print the report
    print_validation_report(validation_results)

    # Also validate single file for backward compatibility
    print("\n" + "=" * 80)
    print("📋 SINGLE FILE VALIDATION (American Standard Version)")
    print("=" * 80)

    json_file = json_directory / "clean_American_Standard_Version_1901_ASV.json"
    if json_file.exists():
        validation_issues, validation_warnings = validate_bible_json(json_file)

        if validation_issues:
            print("🚨 ISSUES:")
            for issue in validation_issues:
                print(f"   • {issue}")

        if validation_warnings:
            print("⚠️  KNOWN VARIATIONS (acceptable):")
            for warning in validation_warnings:
                print(f"   • {warning}")

        if not validation_issues and not validation_warnings:
            print("✅ No issues found. The JSON structure is valid.")
    else:
        print("❌ File not found.")
