import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List

# Optional PyArrow import with graceful fallback
try:
    import pyarrow as pa
    import pyarrow.parquet as pq

    PYARROW_AVAILABLE = True
except ImportError:
    PYARROW_AVAILABLE = False
    pa = None
    pq = None

# -----------------------------------------------------------
# 1. Canonical reference data
# -----------------------------------------------------------
CANONICAL_BOOKS = [
    # Old Testament (39)
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1 Samuel",
    "2 Samuel",
    "1 Kings",
    "2 Kings",
    "1 Chronicles",
    "2 Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalms",
    "Proverbs",
    "Ecclesiastes",
    "Song of Solomon",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    # New Testament (27)
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1 Corinthians",
    "2 Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1 Thessalonians",
    "2 Thessalonians",
    "1 Timothy",
    "2 Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1 Peter",
    "2 Peter",
    "1 John",
    "2 John",
    "3 John",
    "Jude",
    "Revelation",
]

# EXPECTED_VERSES[book][chapter] = number_of_verses
# Baseline: King James Version (identical in most mainstream translations)

# Common abbreviations mapping
ABBREVIATION_MAP = {
    # Old Testament
    "Gen": "Genesis",
    "Ge": "Genesis",
    "Gn": "Genesis",
    "Exo": "Exodus",
    "Ex": "Exodus",
    "Exod": "Exodus",
    "Lev": "Leviticus",
    "Le": "Leviticus",
    "Lv": "Leviticus",
    "Num": "Numbers",
    "Nu": "Numbers",
    "Nm": "Numbers",
    "Nb": "Numbers",
    "Deu": "Deuteronomy",
    "De": "Deuteronomy",
    "Dt": "Deuteronomy",
    "Deut": "Deuteronomy",
    "Jos": "Joshua",
    "Jsh": "Joshua",
    "Josh": "Joshua",
    "Jud": "Judges",
    "Jdg": "Judges",
    "Jg": "Judges",
    "Judg": "Judges",
    "Rut": "Ruth",
    "Ru": "Ruth",
    "Rt": "Ruth",
    "1Sa": "1 Samuel",
    "1S": "1 Samuel",
    "1 Sam": "1 Samuel",
    "1Sam": "1 Samuel",
    "2Sa": "2 Samuel",
    "2S": "2 Samuel",
    "2 Sam": "2 Samuel",
    "2Sam": "2 Samuel",
    "1Ki": "1 Kings",
    "1K": "1 Kings",
    "1Kgs": "1 Kings",
    "1 Kings": "1 Kings",
    "2Ki": "2 Kings",
    "2K": "2 Kings",
    "2Kgs": "2 Kings",
    "2 Kings": "2 Kings",
    "1Ch": "1 Chronicles",
    "1Chr": "1 Chronicles",
    "1 Chr": "1 Chronicles",
    "1 Ch": "1 Chronicles",
    "2Ch": "2 Chronicles",
    "2Chr": "2 Chronicles",
    "2 Chr": "2 Chronicles",
    "2 Ch": "2 Chronicles",
    "Ezr": "Ezra",
    "Ez": "Ezra",
    "Neh": "Nehemiah",
    "Ne": "Nehemiah",
    "Est": "Esther",
    "Es": "Esther",
    "Job": "Job",
    "Psa": "Psalms",
    "Ps": "Psalms",
    "Psalm": "Psalms",
    "Pro": "Proverbs",
    "Pr": "Proverbs",
    "Prov": "Proverbs",
    "Ecc": "Ecclesiastes",
    "Ec": "Ecclesiastes",
    "Qoh": "Ecclesiastes",
    "Sol": "Song of Solomon",
    "Song": "Song of Solomon",
    "SOS": "Song of Solomon",
    "Cant": "Song of Solomon",
    "Isa": "Isaiah",
    "Is": "Isaiah",
    "Isa": "Isaiah",
    "Jer": "Jeremiah",
    "Je": "Jeremiah",
    "Lam": "Lamentations",
    "La": "Lamentations",
    "Eze": "Ezekiel",
    "Ezk": "Ezekiel",
    "Ez": "Ezekiel",
    "Dan": "Daniel",
    "Da": "Daniel",
    "Dn": "Daniel",
    "Hos": "Hosea",
    "Ho": "Hosea",
    "Joe": "Joel",
    "Jl": "Joel",
    "Amo": "Amos",
    "Am": "Amos",
    "Oba": "Obadiah",
    "Ob": "Obadiah",
    "Jon": "Jonah",
    "Jnh": "Jonah",
    "Mic": "Micah",
    "Mi": "Micah",
    "Nah": "Nahum",
    "Na": "Nahum",
    "Hab": "Habakkuk",
    "Hb": "Habakkuk",
    "Zep": "Zephaniah",
    "Zph": "Zephaniah",
    "Zp": "Zephaniah",
    "Hag": "Haggai",
    "Hg": "Haggai",
    "Zec": "Zechariah",
    "Zch": "Zechariah",
    "Zc": "Zechariah",
    "Zech": "Zechariah",
    "Mal": "Malachi",
    "Ml": "Malachi",
    # New Testament
    "Mat": "Matthew",
    "Mt": "Matthew",
    "Matt": "Matthew",
    "Mar": "Mark",
    "Mk": "Mark",
    "Mr": "Mark",
    "Luk": "Luke",
    "Lk": "Luke",
    "Lu": "Luke",
    "Joh": "John",
    "Jn": "John",
    "Jhn": "John",
    "Act": "Acts",
    "Ac": "Acts",
    "Rom": "Romans",
    "Ro": "Romans",
    "Rm": "Romans",
    "1Co": "1 Corinthians",
    "1Cor": "1 Corinthians",
    "1 Cor": "1 Corinthians",
    "2Co": "2 Corinthians",
    "2Cor": "2 Corinthians",
    "2 Cor": "2 Corinthians",
    "Gal": "Galatians",
    "Ga": "Galatians",
    "Eph": "Ephesians",
    "Ep": "Ephesians",
    "Phi": "Philippians",
    "Php": "Philippians",
    "Ph": "Philippians",
    "Phil": "Philippians",
    "Col": "Colossians",
    "Co": "Colossians",
    "1Th": "1 Thessalonians",
    "1Thess": "1 Thessalonians",
    "1 Thess": "1 Thessalonians",
    "1 Th": "1 Thessalonians",
    "2Th": "2 Thessalonians",
    "2Thess": "2 Thessalonians",
    "2 Thess": "2 Thessalonians",
    "2 Th": "2 Thessalonians",
    "1Ti": "1 Timothy",
    "1Tim": "1 Timothy",
    "1 Tim": "1 Timothy",
    "1 Ti": "1 Timothy",
    "2Ti": "2 Timothy",
    "2Tim": "2 Timothy",
    "2 Tim": "2 Timothy",
    "2 Ti": "2 Timothy",
    "Tit": "Titus",
    "Ti": "Titus",
    "Phm": "Philemon",
    "Phlm": "Philemon",
    "Pm": "Philemon",
    "Heb": "Hebrews",
    "He": "Hebrews",
    "Jam": "James",
    "Jas": "James",
    "Jm": "James",
    "1Pe": "1 Peter",
    "1Pet": "1 Peter",
    "1 Pet": "1 Peter",
    "1 Pe": "1 Peter",
    "2Pe": "2 Peter",
    "2Pet": "2 Peter",
    "2 Pet": "2 Peter",
    "2 Pe": "2 Peter",
    "1Jo": "1 John",
    "1Jn": "1 John",
    "1 Jn": "1 John",
    "1 Jo": "1 John",
    "2Jo": "2 John",
    "2Jn": "2 John",
    "2 Jn": "2 John",
    "2 Jo": "2 John",
    "3Jo": "3 John",
    "3Jn": "3 John",
    "3 Jn": "3 John",
    "3 Jo": "3 John",
    "Jud": "Jude",
    "Jude": "Jude",
    "Rev": "Revelation",
    "Re": "Revelation",
    "Rv": "Revelation",
}

# Expected chapter counts for each book
EXPECTED_CHAPTERS = {
    # Old Testament
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
    # New Testament
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

EXPECTED_VERSES = {
    "Genesis": {
        1: 31,
        2: 25,
        3: 24,
        4: 26,
        5: 32,
        6: 22,
        7: 24,
        8: 22,
        9: 29,
        10: 32,
        11: 32,
        12: 20,
        13: 18,
        14: 24,
        15: 21,
        16: 16,
        17: 27,
        18: 33,
        19: 38,
        20: 18,
        21: 34,
        22: 24,
        23: 20,
        24: 67,
        25: 34,
        26: 35,
        27: 46,
        28: 22,
        29: 35,
        30: 43,
        31: 55,
        32: 32,
        33: 20,
        34: 31,
        35: 29,
        36: 43,
        37: 36,
        38: 30,
        39: 23,
        40: 23,
        41: 57,
        42: 38,
        43: 34,
        44: 34,
        45: 28,
        46: 34,
        47: 31,
        48: 22,
        49: 33,
        50: 26,
    },
    "Exodus": {
        1: 22,
        2: 25,
        3: 22,
        4: 31,
        5: 23,
        6: 30,
        7: 25,
        8: 32,
        9: 35,
        10: 29,
        11: 10,
        12: 51,
        13: 22,
        14: 31,
        15: 27,
        16: 36,
        17: 16,
        18: 27,
        19: 25,
        20: 26,
        21: 36,
        22: 31,
        23: 33,
        24: 18,
        25: 40,
        26: 37,
        27: 21,
        28: 43,
        29: 46,
        30: 38,
        31: 18,
        32: 35,
        33: 23,
        34: 35,
        35: 35,
        36: 38,
        37: 29,
        38: 31,
        39: 43,
        40: 38,
    },
    "Leviticus": {
        1: 17,
        2: 16,
        3: 17,
        4: 35,
        5: 19,
        6: 30,
        7: 38,
        8: 36,
        9: 24,
        10: 20,
        11: 47,
        12: 8,
        13: 59,
        14: 57,
        15: 33,
        16: 34,
        17: 16,
        18: 30,
        19: 37,
        20: 27,
        21: 24,
        22: 33,
        23: 44,
        24: 23,
        25: 55,
        26: 46,
        27: 34,
    },
    "Numbers": {
        1: 54,
        2: 34,
        3: 51,
        4: 49,
        5: 31,
        6: 27,
        7: 89,
        8: 26,
        9: 23,
        10: 36,
        11: 35,
        12: 16,
        13: 33,
        14: 45,
        15: 41,
        16: 50,
        17: 13,
        18: 32,
        19: 22,
        20: 29,
        21: 35,
        22: 41,
        23: 30,
        24: 25,
        25: 18,
        26: 65,
        27: 23,
        28: 31,
        29: 40,
        30: 16,
        31: 54,
        32: 42,
        33: 56,
        34: 29,
        35: 34,
        36: 13,
    },
    "Deuteronomy": {
        1: 46,
        2: 37,
        3: 29,
        4: 49,
        5: 33,
        6: 25,
        7: 26,
        8: 20,
        9: 29,
        10: 22,
        11: 32,
        12: 32,
        13: 18,
        14: 29,
        15: 23,
        16: 22,
        17: 20,
        18: 22,
        19: 21,
        20: 20,
        21: 23,
        22: 30,
        23: 25,
        24: 22,
        25: 19,
        26: 19,
        27: 26,
        28: 68,
        29: 29,
        30: 20,
        31: 30,
        32: 52,
        33: 29,
        34: 12,
    },
    "Joshua": {
        1: 18,
        2: 24,
        3: 17,
        4: 24,
        5: 15,
        6: 27,
        7: 26,
        8: 35,
        9: 27,
        10: 43,
        11: 23,
        12: 24,
        13: 33,
        14: 15,
        15: 63,
        16: 10,
        17: 18,
        18: 28,
        19: 51,
        20: 9,
        21: 45,
        22: 34,
        23: 16,
        24: 33,
    },
    "Judges": {
        1: 36,
        2: 23,
        3: 31,
        4: 24,
        5: 31,
        6: 40,
        7: 25,
        8: 35,
        9: 57,
        10: 18,
        11: 40,
        12: 15,
        13: 25,
        14: 20,
        15: 20,
        16: 31,
        17: 13,
        18: 31,
        19: 30,
        20: 48,
        21: 25,
    },
    "Ruth": {1: 22, 2: 23, 3: 18, 4: 22},
    "1 Samuel": {
        1: 28,
        2: 36,
        3: 21,
        4: 22,
        5: 12,
        6: 21,
        7: 17,
        8: 22,
        9: 27,
        10: 27,
        11: 15,
        12: 25,
        13: 23,
        14: 52,
        15: 35,
        16: 23,
        17: 58,
        18: 30,
        19: 24,
        20: 42,
        21: 15,
        22: 23,
        23: 29,
        24: 22,
        25: 44,
        26: 25,
        27: 12,
        28: 25,
        29: 11,
        30: 31,
        31: 13,
    },
    "2 Samuel": {
        1: 27,
        2: 32,
        3: 39,
        4: 12,
        5: 25,
        6: 23,
        7: 29,
        8: 18,
        9: 13,
        10: 19,
        11: 27,
        12: 31,
        13: 39,
        14: 33,
        15: 37,
        16: 23,
        17: 29,
        18: 33,
        19: 43,
        20: 26,
        21: 22,
        22: 51,
        23: 39,
        24: 25,
    },
    "1 Kings": {
        1: 53,
        2: 46,
        3: 28,
        4: 34,
        5: 18,
        6: 38,
        7: 51,
        8: 66,
        9: 28,
        10: 29,
        11: 43,
        12: 33,
        13: 34,
        14: 31,
        15: 34,
        16: 34,
        17: 24,
        18: 46,
        19: 21,
        20: 43,
        21: 29,
        22: 53,
    },
    "2 Kings": {
        1: 18,
        2: 25,
        3: 27,
        4: 44,
        5: 27,
        6: 33,
        7: 20,
        8: 29,
        9: 37,
        10: 36,
        11: 21,
        12: 21,
        13: 25,
        14: 29,
        15: 38,
        16: 20,
        17: 41,
        18: 37,
        19: 37,
        20: 21,
        21: 26,
        22: 20,
        23: 37,
        24: 20,
        25: 30,
    },
    "1 Chronicles": {
        1: 54,
        2: 55,
        3: 24,
        4: 43,
        5: 26,
        6: 81,
        7: 40,
        8: 40,
        9: 44,
        10: 14,
        11: 47,
        12: 40,
        13: 14,
        14: 17,
        15: 29,
        16: 43,
        17: 27,
        18: 17,
        19: 19,
        20: 8,
        21: 30,
        22: 19,
        23: 32,
        24: 31,
        25: 31,
        26: 32,
        27: 34,
        28: 21,
        29: 30,
    },
    "2 Chronicles": {
        1: 17,
        2: 18,
        3: 17,
        4: 22,
        5: 14,
        6: 42,
        7: 22,
        8: 18,
        9: 31,
        10: 19,
        11: 23,
        12: 16,
        13: 22,
        14: 15,
        15: 19,
        16: 14,
        17: 19,
        18: 34,
        19: 11,
        20: 37,
        21: 20,
        22: 12,
        23: 21,
        24: 27,
        25: 28,
        26: 23,
        27: 9,
        28: 27,
        29: 36,
        30: 27,
        31: 21,
        32: 33,
        33: 25,
        34: 33,
        35: 27,
        36: 23,
    },
    "Ezra": {
        1: 11,
        2: 70,
        3: 13,
        4: 24,
        5: 17,
        6: 22,
        7: 28,
        8: 36,
        9: 15,
        10: 44,
    },
    "Nehemiah": {
        1: 11,
        2: 20,
        3: 32,
        4: 23,
        5: 19,
        6: 19,
        7: 73,
        8: 18,
        9: 38,
        10: 39,
        11: 36,
        12: 47,
        13: 31,
    },
    "Esther": {1: 22, 2: 23, 3: 15, 4: 17, 5: 14, 6: 14, 7: 10, 8: 17, 9: 32, 10: 3},
    "Job": {
        1: 22,
        2: 13,
        3: 26,
        4: 21,
        5: 27,
        6: 30,
        7: 21,
        8: 22,
        9: 35,
        10: 22,
        11: 20,
        12: 25,
        13: 28,
        14: 22,
        15: 35,
        16: 22,
        17: 16,
        18: 21,
        19: 29,
        20: 29,
        21: 34,
        22: 30,
        23: 17,
        24: 25,
        25: 6,
        26: 14,
        27: 23,
        28: 28,
        29: 25,
        30: 31,
        31: 40,
        32: 22,
        33: 33,
        34: 37,
        35: 16,
        36: 33,
        37: 24,
        38: 41,
        39: 30,
        40: 24,
        41: 34,
        42: 17,
    },
    "Psalms": {
        1: 6,
        2: 12,
        3: 8,
        4: 8,
        5: 12,
        6: 10,
        7: 17,
        8: 9,
        9: 20,
        10: 18,
        11: 7,
        12: 8,
        13: 6,
        14: 7,
        15: 5,
        16: 11,
        17: 15,
        18: 50,
        19: 14,
        20: 9,
        21: 13,
        22: 31,
        23: 6,
        24: 10,
        25: 22,
        26: 12,
        27: 14,
        28: 9,
        29: 11,
        30: 12,
        31: 24,
        32: 11,
        33: 22,
        34: 22,
        35: 28,
        36: 12,
        37: 40,
        38: 22,
        39: 13,
        40: 17,
        41: 13,
        42: 11,
        43: 5,
        44: 26,
        45: 17,
        46: 11,
        47: 9,
        48: 14,
        49: 20,
        50: 23,
        51: 19,
        52: 9,
        53: 6,
        54: 7,
        55: 23,
        56: 13,
        57: 11,
        58: 11,
        59: 17,
        60: 12,
        61: 8,
        62: 12,
        63: 11,
        64: 10,
        65: 13,
        66: 20,
        67: 7,
        68: 35,
        69: 36,
        70: 5,
        71: 24,
        72: 20,
        73: 28,
        74: 23,
        75: 10,
        76: 12,
        77: 20,
        78: 72,
        79: 13,
        80: 19,
        81: 16,
        82: 8,
        83: 18,
        84: 12,
        85: 13,
        86: 17,
        87: 7,
        88: 18,
        89: 52,
        90: 17,
        91: 16,
        92: 15,
        93: 5,
        94: 23,
        95: 11,
        96: 13,
        97: 12,
        98: 9,
        99: 9,
        100: 5,
        101: 8,
        102: 28,
        103: 22,
        104: 35,
        105: 45,
        106: 48,
        107: 43,
        108: 13,
        109: 31,
        110: 7,
        111: 10,
        112: 10,
        113: 9,
        114: 8,
        115: 18,
        116: 19,
        117: 2,
        118: 29,
        119: 176,
        120: 7,
        121: 8,
        122: 9,
        123: 4,
        124: 8,
        125: 5,
        126: 6,
        127: 5,
        128: 6,
        129: 8,
        130: 8,
        131: 3,
        132: 18,
        133: 3,
        134: 3,
        135: 21,
        136: 26,
        137: 9,
        138: 8,
        139: 24,
        140: 13,
        141: 10,
        142: 7,
        143: 12,
        144: 15,
        145: 21,
        146: 10,
        147: 20,
        148: 14,
        149: 9,
        150: 6,
    },
    "Proverbs": {
        1: 33,
        2: 22,
        3: 35,
        4: 27,
        5: 23,
        6: 35,
        7: 27,
        8: 36,
        9: 18,
        10: 32,
        11: 31,
        12: 28,
        13: 25,
        14: 35,
        15: 33,
        16: 33,
        17: 28,
        18: 24,
        19: 29,
        20: 30,
        21: 31,
        22: 29,
        23: 35,
        24: 34,
        25: 28,
        26: 28,
        27: 27,
        28: 28,
        29: 27,
        30: 33,
        31: 31,
    },
    "Ecclesiastes": {
        1: 18,
        2: 26,
        3: 22,
        4: 16,
        5: 20,
        6: 12,
        7: 29,
        8: 17,
        9: 18,
        10: 20,
        11: 10,
        12: 14,
    },
    "Song of Solomon": {1: 17, 2: 17, 3: 11, 4: 16, 5: 16, 6: 13, 7: 13, 8: 14},
    "Isaiah": {
        1: 31,
        2: 22,
        3: 26,
        4: 6,
        5: 30,
        6: 13,
        7: 25,
        8: 22,
        9: 21,
        10: 34,
        11: 16,
        12: 6,
        13: 22,
        14: 32,
        15: 9,
        16: 14,
        17: 14,
        18: 7,
        19: 25,
        20: 6,
        21: 17,
        22: 25,
        23: 18,
        24: 23,
        25: 12,
        26: 21,
        27: 13,
        28: 29,
        29: 24,
        30: 33,
        31: 9,
        32: 20,
        33: 24,
        34: 17,
        35: 10,
        36: 22,
        37: 38,
        38: 22,
        39: 8,
        40: 31,
        41: 29,
        42: 25,
        43: 28,
        44: 28,
        45: 25,
        46: 13,
        47: 15,
        48: 22,
        49: 26,
        50: 11,
        51: 23,
        52: 15,
        53: 12,
        54: 17,
        55: 13,
        56: 12,
        57: 21,
        58: 14,
        59: 21,
        60: 22,
        61: 11,
        62: 12,
        63: 19,
        64: 12,
        65: 25,
        66: 24,
    },
    "Jeremiah": {
        1: 19,
        2: 37,
        3: 25,
        4: 31,
        5: 31,
        6: 30,
        7: 34,
        8: 22,
        9: 26,
        10: 25,
        11: 23,
        12: 17,
        13: 27,
        14: 22,
        15: 21,
        16: 21,
        17: 27,
        18: 23,
        19: 15,
        20: 18,
        21: 14,
        22: 30,
        23: 40,
        24: 10,
        25: 38,
        26: 24,
        27: 22,
        28: 17,
        29: 32,
        30: 24,
        31: 40,
        32: 44,
        33: 26,
        34: 22,
        35: 19,
        36: 32,
        37: 21,
        38: 28,
        39: 18,
        40: 16,
        41: 18,
        42: 22,
        43: 13,
        44: 30,
        45: 5,
        46: 28,
        47: 7,
        48: 47,
        49: 39,
        50: 46,
        51: 64,
        52: 34,
    },
    "Lamentations": {1: 22, 2: 22, 3: 66, 4: 22, 5: 22},
    "Ezekiel": {
        1: 28,
        2: 10,
        3: 27,
        4: 17,
        5: 17,
        6: 14,
        7: 27,
        8: 18,
        9: 11,
        10: 22,
        11: 25,
        12: 28,
        13: 23,
        14: 23,
        15: 8,
        16: 63,
        17: 24,
        18: 32,
        19: 14,
        20: 49,
        21: 32,
        22: 31,
        23: 49,
        24: 27,
        25: 17,
        26: 21,
        27: 36,
        28: 26,
        29: 21,
        30: 26,
        31: 18,
        32: 32,
        33: 33,
        34: 31,
        35: 15,
        36: 38,
        37: 28,
        38: 23,
        39: 29,
        40: 49,
        41: 26,
        42: 20,
        43: 27,
        44: 31,
        45: 25,
        46: 24,
        47: 23,
        48: 35,
    },
    "Daniel": {
        1: 21,
        2: 49,
        3: 30,
        4: 37,
        5: 31,
        6: 28,
        7: 28,
        8: 27,
        9: 27,
        10: 21,
        11: 45,
        12: 13,
    },
    "Hosea": {
        1: 11,
        2: 23,
        3: 5,
        4: 19,
        5: 15,
        6: 11,
        7: 16,
        8: 14,
        9: 17,
        10: 15,
        11: 12,
        12: 14,
        13: 16,
        14: 9,
    },
    "Joel": {1: 20, 2: 32, 3: 21},
    "Amos": {1: 15, 2: 16, 3: 15, 4: 13, 5: 27, 6: 14, 7: 17, 8: 14, 9: 15},
    "Obadiah": {1: 21},
    "Jonah": {1: 17, 2: 10, 3: 10, 4: 11},
    "Micah": {1: 16, 2: 13, 3: 12, 4: 13, 5: 15, 6: 16, 7: 20},
    "Nahum": {1: 15, 2: 13, 3: 19},
    "Habakkuk": {1: 17, 2: 20, 3: 19},
    "Zephaniah": {1: 18, 2: 15, 3: 20},
    "Haggai": {1: 15, 2: 23},
    "Zechariah": {
        1: 21,
        2: 13,
        3: 10,
        4: 14,
        5: 11,
        6: 15,
        7: 14,
        8: 23,
        9: 17,
        10: 12,
        11: 17,
        12: 14,
        13: 9,
        14: 21,
    },
    "Malachi": {1: 14, 2: 17, 3: 18, 4: 6},
    "Matthew": {
        1: 25,
        2: 23,
        3: 17,
        4: 25,
        5: 48,
        6: 34,
        7: 29,
        8: 34,
        9: 38,
        10: 42,
        11: 30,
        12: 50,
        13: 58,
        14: 36,
        15: 39,
        16: 28,
        17: 27,
        18: 35,
        19: 30,
        20: 34,
        21: 46,
        22: 46,
        23: 39,
        24: 51,
        25: 46,
        26: 75,
        27: 66,
        28: 20,
    },
    "Mark": {
        1: 45,
        2: 28,
        3: 35,
        4: 41,
        5: 43,
        6: 56,
        7: 37,
        8: 38,
        9: 50,
        10: 52,
        11: 33,
        12: 44,
        13: 37,
        14: 72,
        15: 47,
        16: 20,
    },
    "Luke": {
        1: 80,
        2: 52,
        3: 38,
        4: 44,
        5: 39,
        6: 49,
        7: 50,
        8: 56,
        9: 62,
        10: 42,
        11: 54,
        12: 59,
        13: 35,
        14: 35,
        15: 32,
        16: 31,
        17: 37,
        18: 43,
        19: 48,
        20: 47,
        21: 38,
        22: 71,
        23: 56,
        24: 53,
    },
    "John": {
        1: 51,
        2: 25,
        3: 36,
        4: 54,
        5: 47,
        6: 71,
        7: 53,
        8: 59,
        9: 41,
        10: 42,
        11: 57,
        12: 50,
        13: 38,
        14: 31,
        15: 27,
        16: 33,
        17: 26,
        18: 40,
        19: 42,
        20: 31,
        21: 25,
    },
    "Acts": {
        1: 26,
        2: 47,
        3: 26,
        4: 37,
        5: 42,
        6: 15,
        7: 60,
        8: 40,
        9: 43,
        10: 48,
        11: 30,
        12: 25,
        13: 52,
        14: 28,
        15: 41,
        16: 40,
        17: 34,
        18: 28,
        19: 41,
        20: 38,
        21: 40,
        22: 30,
        23: 35,
        24: 27,
        25: 27,
        26: 32,
        27: 44,
        28: 31,
    },
    "Romans": {
        1: 32,
        2: 29,
        3: 31,
        4: 25,
        5: 21,
        6: 23,
        7: 25,
        8: 39,
        9: 33,
        10: 21,
        11: 36,
        12: 21,
        13: 14,
        14: 23,
        15: 33,
        16: 27,
    },
    "1 Corinthians": {
        1: 31,
        2: 16,
        3: 23,
        4: 21,
        5: 13,
        6: 20,
        7: 40,
        8: 13,
        9: 27,
        10: 33,
        11: 34,
        12: 31,
        13: 13,
        14: 40,
        15: 58,
        16: 24,
    },
    "2 Corinthians": {
        1: 24,
        2: 17,
        3: 18,
        4: 18,
        5: 21,
        6: 18,
        7: 16,
        8: 24,
        9: 15,
        10: 18,
        11: 33,
        12: 21,
        13: 14,
    },
    "Galatians": {1: 24, 2: 21, 3: 29, 4: 31, 5: 26, 6: 18},
    "Ephesians": {1: 23, 2: 22, 3: 21, 4: 32, 5: 33, 6: 24},
    "Philippians": {1: 30, 2: 30, 3: 21, 4: 23},
    "Colossians": {1: 29, 2: 23, 3: 25, 4: 18},
    "1 Thessalonians": {1: 10, 2: 20, 3: 13, 4: 18, 5: 28},
    "2 Thessalonians": {1: 12, 2: 17, 3: 18},
    "1 Timothy": {1: 20, 2: 15, 3: 16, 4: 16, 5: 25, 6: 21},
    "2 Timothy": {1: 18, 2: 26, 3: 17, 4: 22},
    "Titus": {1: 16, 2: 15, 3: 15},
    "Philemon": {1: 25},
    "Hebrews": {
        1: 14,
        2: 18,
        3: 19,
        4: 16,
        5: 14,
        6: 20,
        7: 28,
        8: 13,
        9: 28,
        10: 39,
        11: 40,
        12: 29,
        13: 25,
    },
    "James": {1: 27, 2: 26, 3: 18, 4: 17, 5: 20},
    "1 Peter": {1: 25, 2: 25, 3: 22, 4: 19, 5: 14},
    "2 Peter": {1: 21, 2: 22, 3: 18},
    "1 John": {1: 10, 2: 29, 3: 24, 4: 21, 5: 21},
    "2 John": {1: 13},
    "3 John": {1: 15},
    "Jude": {1: 25},
    "Revelation": {
        1: 20,
        2: 29,
        3: 22,
        4: 11,
        5: 14,
        6: 17,
        7: 17,
        8: 13,
        9: 21,
        10: 11,
        11: 19,
        12: 17,
        13: 18,
        14: 20,
        15: 8,
        16: 21,
        17: 18,
        18: 24,
        19: 21,
        20: 15,
        21: 27,
        22: 21,
    },
}


# -----------------------------------------------------------
# Known verse count variations across Bible translations
# -----------------------------------------------------------
KNOWN_VARIATIONS = {
    "3 John": {1: [14, 15]},  # Some versions split verse 14
    "Ezra": {2: [50, 54, 70]},  # Genealogical lists vary
    "Nehemiah": {7: [57, 60, 73]},  # Genealogical lists vary
    "Malachi": {3: [18, 19]},  # Some versions split verses
    "Romans": {12: [20, 21]},  # Textual variations
    "1 Corinthians": {11: [34, 35]},  # Textual variations
    "2 Corinthians": {2: [17, 18], 13: [13, 14]},  # Textual variations
    "Revelation": {12: [17, 18]},  # Textual variations
}


def validate_verse_count_flexible(book: str, chapter: int, actual_count: int) -> bool:
    """Flexible verse count validation that accounts for translation variations."""

    # Get expected count from standard reference
    expected = EXPECTED_VERSES.get(book, {}).get(chapter)
    if expected is None:
        return True  # No reference, assume valid

    # Check if actual count matches expected
    if actual_count == expected:
        return True

    # Check known variations
    variations = KNOWN_VARIATIONS.get(book, {}).get(chapter, [expected])
    return actual_count in variations


@dataclass
class BibleProcessor:
    json_path: Path
    translation_name: str = field(init=False)
    raw_data: Dict[str, Any] = field(init=False)
    validated: bool = field(default=False)
    issues: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.translation_name = self.json_path.stem.replace("clean_", "")
        self.raw_data = self._load_json()

    def _load_json(self) -> Dict[str, Any]:
        """Load JSON data from file with error handling"""
        try:
            return json.loads(self.json_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {self.json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.json_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load JSON from {self.json_path}: {e}")

    def validate_structure(self) -> List[str]:
        """Validate JSON structure against canonical requirements"""
        issues: List[str] = []

        # Collect all books from both testaments using modern dict unpacking
        books = {}
        for testament in ["old_testament", "new_testament"]:
            if testament in self.raw_data:
                books |= self.raw_data[testament].get("books", {})

        # Check book completeness using set operations
        canonical_set = set(CANONICAL_BOOKS)
        books_set = set(books.keys())

        if missing := canonical_set - books_set:
            issues.append(f"Missing books: {', '.join(sorted(missing))}")
        if extra := books_set - canonical_set:
            issues.append(f"Extra books: {', '.join(sorted(extra))}")

        # Check chapter/verse counts using pattern matching for better structure
        for book_name, book_data in books.items():
            match book_name:
                case name if name not in EXPECTED_VERSES:
                    issues.append(f"Skipping {book_name} - no verse data")
                    continue
                case _:
                    pass

            chapters = book_data.get("chapters", {})
            expected_chapters = EXPECTED_VERSES[book_name]

            # Chapter count check
            if len(chapters) != len(expected_chapters):
                issues.append(
                    f"{book_name}: Expected {len(expected_chapters)} chapters, "
                    f"found {len(chapters)}"
                )

            # Verse count per chapter using walrus operator and match
            for ch_num, expected_verse_count in expected_chapters.items():
                match chapters.get(str(ch_num)):
                    case None:
                        issues.append(f"{book_name} {ch_num}: Missing chapter")
                        continue
                    case chapter:
                        verses = chapter.get("verses", {})
                        # Count non-None verses efficiently
                        actual_verse_count = sum(
                            1 for v in verses.values() if v is not None
                        )

                        if not validate_verse_count_flexible(
                            book_name, ch_num, actual_verse_count
                        ):
                            issues.append(
                                f"{book_name} {ch_num}: Expected {expected_verse_count} verses, "
                                f"found {actual_verse_count}"
                            )

        self.issues = issues
        self.validated = not bool(issues)
        return issues

    def convert_to_parquet(self, output_dir: Path) -> Path:
        """Convert validated JSON to Parquet format"""
        if not PYARROW_AVAILABLE:
            raise ImportError(
                "PyArrow is required for Parquet conversion. "
                "Install with: pip install pyarrow"
            )

        if not self.validated:
            raise ValueError("JSON structure not validated or validation failed")

        # Create output directory if needed
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{self.translation_name}.parquet"

        # Prepare data using generator for memory efficiency
        def generate_verse_data():
            """Generator that yields verse data dictionaries efficiently"""
            testament_mapping = {"old_testament": "old", "new_testament": "new"}

            for testament, books in (
                (t, self.raw_data[t]["books"])
                for t in ["old_testament", "new_testament"]
                if t in self.raw_data
            ):
                testament_short = testament_mapping[testament]

                for book_name, book_data in books.items():
                    chapters = book_data.get("chapters", {})

                    for ch_num, chapter in chapters.items():
                        verses = chapter.get("verses", {})

                        for v_num, verse_data in verses.items():
                            # Skip None verses
                            if verse_data is None:
                                continue

                            yield {
                                "translation": self.translation_name,
                                "testament": testament_short,
                                "book": book_name,
                                "chapter": int(ch_num),
                                "verse": int(v_num),
                                "text": verse_data.get("text", ""),
                                "id": verse_data.get("id", ""),
                                "strongs_numbers": verse_data.get(
                                    "strongs_numbers", []
                                ),
                                "cross_references": verse_data.get(
                                    "cross_references", []
                                ),
                            }

        # Create PyArrow Table and save as Parquet
        data = list(generate_verse_data())

        if not data:
            raise ValueError("No verse data found to convert to Parquet")

        table = pa.Table.from_pylist(data)
        pq.write_table(table, output_path)

        print(f"✅ Converted {len(data)} verses to {output_path}")
        return output_path


def process_translation(json_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Process a single translation file"""
    translation_name = json_path.stem.replace("clean_", "")

    try:
        processor = BibleProcessor(json_path)
        validation_issues = processor.validate_structure()

        result = {
            "translation": translation_name,
            "valid": not bool(validation_issues),
            "issues": validation_issues,
            "parquet_path": None,
            "verse_count": 0,
        }

        if result["valid"]:
            try:
                parquet_path = processor.convert_to_parquet(output_dir)
                result["parquet_path"] = str(parquet_path)

                # Count verses for reporting
                result["verse_count"] = sum(
                    len(
                        [v for v in chapter.get("verses", {}).values() if v is not None]
                    )
                    for testament in ["old_testament", "new_testament"]
                    if testament in processor.raw_data
                    for book_data in processor.raw_data[testament]
                    .get("books", {})
                    .values()
                    for chapter in book_data.get("chapters", {}).values()
                )
            except Exception as e:
                result["valid"] = False
                result["issues"].append(f"Parquet conversion failed: {str(e)}")

        return result

    except Exception as e:
        return {
            "translation": translation_name,
            "valid": False,
            "issues": [f"Processing failed: {str(e)}"],
            "parquet_path": None,
            "verse_count": 0,
        }


def process_directory(json_dir: Path, output_dir: Path) -> List[Dict[str, Any]]:
    """Process all JSON translations in a directory"""
    # Find JSON files using pattern matching for better filtering
    json_files = [
        f for f in json_dir.glob("*.json") if not f.name.startswith(".") and f.is_file()
    ]

    if not json_files:
        print(f"⚠️ No JSON files found in directory: {json_dir}")
        return []

    print(f"📚 Found {len(json_files)} translations to process")
    print(f"📂 Output directory: {output_dir}")

    results = []
    for i, json_path in enumerate(json_files, 1):
        print(f"[{i}/{len(json_files)}] Processing: {json_path.name}")
        result = process_translation(json_path, output_dir)
        results.append(result)

        # Progress feedback
        status = "✅" if result["valid"] else "❌"
        verse_info = (
            f" ({result['verse_count']} verses)" if result["verse_count"] else ""
        )
        print(f"  {status} {result['translation']}{verse_info}")

        if not result["valid"] and result["issues"]:
            # Show first issue as preview
            print(f"    Issue: {result['issues'][0]}")

    return results


def main():
    """Main function with improved CLI and reporting"""
    # Default paths
    DEFAULT_JSON_DIR = Path("/Users/joshuashay/Desktop/holybible/data/json/cleaned")
    DEFAULT_OUTPUT_DIR = Path("/Users/joshuashay/Desktop/holybible/data/parquet")

    # Parse command-line arguments
    match len(sys.argv):
        case 1:
            json_dir, output_dir = DEFAULT_JSON_DIR, DEFAULT_OUTPUT_DIR
        case 2:
            json_dir, output_dir = Path(sys.argv[1]), DEFAULT_OUTPUT_DIR
        case 3:
            json_dir, output_dir = Path(sys.argv[1]), Path(sys.argv[2])
        case _:
            print("Usage: python bible_processor.py [json_dir] [output_dir]")
            return

    # Verify input directory exists
    if not json_dir.exists():
        print(f"❌ Input directory not found: {json_dir}")
        return

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🔄 Bible Translation Processor")
    print(f"📂 Input directory: {json_dir}")
    print(f"📂 Output directory: {output_dir}")
    print("-" * 50)

    # Process all translations
    results = process_directory(json_dir, output_dir)

    if not results:
        return

    # Generate comprehensive summary
    print("\n" + "=" * 60)
    print("📊 PROCESSING SUMMARY")
    print("=" * 60)

    valid_results = [r for r in results if r["valid"]]
    failed_results = [r for r in results if not r["valid"]]

    total_verses = sum(r["verse_count"] for r in valid_results)

    print(f"📈 Total translations processed: {len(results)}")
    print(f"✅ Successful: {len(valid_results)}")
    print(f"❌ Failed: {len(failed_results)}")
    print(f"📝 Total verses converted: {total_verses:,}")

    if valid_results:
        print(f"\n✅ SUCCESSFUL TRANSLATIONS:")
        for res in valid_results:
            verse_count = (
                f"({res['verse_count']:,} verses)" if res["verse_count"] else ""
            )
            print(f"  • {res['translation']} {verse_count}")

    if failed_results:
        print(f"\n❌ FAILED TRANSLATIONS:")
        for res in failed_results:
            print(f"  • {res['translation']}")
            print(f"    Issues: {len(res['issues'])}")
            # Show first few issues
            for issue in res["issues"][:2]:
                print(f"      - {issue}")
            if len(res["issues"]) > 2:
                print(f"      ... and {len(res['issues']) - 2} more issues")

    print(f"\n📁 Parquet files saved to: {output_dir}")
    print("🎉 Processing complete!")


if __name__ == "__main__":
    main()
