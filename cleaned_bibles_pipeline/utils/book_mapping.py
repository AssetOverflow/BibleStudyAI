# Comprehensive mapping of Bible book names and abbreviations to canonical names
# This should be expanded as needed for all edge cases
BOOK_NAME_MAP = {
    # Genesis
    'Gen': 'Genesis', 'Ge': 'Genesis', 'Gn': 'Genesis', 'Genesis': 'Genesis',
    # Exodus
    'Ex': 'Exodus', 'Exo': 'Exodus', 'Exodus': 'Exodus',
    # Leviticus
    'Lev': 'Leviticus', 'Le': 'Leviticus', 'Lv': 'Leviticus', 'Leviticus': 'Leviticus',
    # Numbers
    'Num': 'Numbers', 'Nu': 'Numbers', 'Nm': 'Numbers', 'Numbers': 'Numbers',
    # Deuteronomy
    'Deut': 'Deuteronomy', 'Dt': 'Deuteronomy', 'Deuteronomy': 'Deuteronomy',
    # Joshua
    'Josh': 'Joshua', 'Jos': 'Joshua', 'Joshua': 'Joshua',
    # Judges
    'Judg': 'Judges', 'Jdg': 'Judges', 'Judges': 'Judges', 'Judg.': 'Judges', 'Jdgs': 'Judges',
    # Ruth
    'Ruth': 'Ruth', 'Ru': 'Ruth',
    # 1 Samuel
    '1Sam': '1 Samuel', '1 Sam': '1 Samuel', 'I Samuel': '1 Samuel', '1Sa': '1 Samuel', '1Samuel': '1 Samuel', '1 Sm': '1 Samuel', '1st Samuel': '1 Samuel',
    # 2 Samuel
    '2Sam': '2 Samuel', '2 Sam': '2 Samuel', 'II Samuel': '2 Samuel', '2Sa': '2 Samuel', '2Samuel': '2 Samuel', '2 Sm': '2 Samuel', '2nd Samuel': '2 Samuel',
    # 1 Kings
    '1Ki': '1 Kings', '1 Kgs': '1 Kings', '1Kings': '1 Kings', '1 Kings': '1 Kings', 'I Kings': '1 Kings', '1st Kings': '1 Kings',
    # 2 Kings
    '2Ki': '2 Kings', '2 Kgs': '2 Kings', '2Kings': '2 Kings', '2 Kings': '2 Kings', 'II Kings': '2 Kings', '2nd Kings': '2 Kings',
    # 1 Chronicles
    '1Chr': '1 Chronicles', '1 Chron': '1 Chronicles', 'I Chronicles': '1 Chronicles', '1Ch': '1 Chronicles', '1 Chronicles': '1 Chronicles', '1st Chronicles': '1 Chronicles',
    # 2 Chronicles
    '2Chr': '2 Chronicles', '2 Chron': '2 Chronicles', 'II Chronicles': '2 Chronicles', '2Ch': '2 Chronicles', '2 Chronicles': '2 Chronicles', '2nd Chronicles': '2 Chronicles',
    # Ezra
    'Ezra': 'Ezra', 'Ezr': 'Ezra',
    # Nehemiah
    'Neh': 'Nehemiah', 'Nehemiah': 'Nehemiah',
    # Esther
    'Esth': 'Esther', 'Esther': 'Esther', 'Est': 'Esther',
    # Job
    'Job': 'Job',
    # Psalms
    'Ps': 'Psalms', 'Pss': 'Psalms', 'Psm': 'Psalms', 'Psalm': 'Psalms', 'Psalms': 'Psalms',
    # Proverbs
    'Prov': 'Proverbs', 'Pro': 'Proverbs', 'Prv': 'Proverbs', 'Proverbs': 'Proverbs',
    # Ecclesiastes
    'Eccl': 'Ecclesiastes', 'Ecc': 'Ecclesiastes', 'Ecclesiastes': 'Ecclesiastes',
    # Song of Solomon
    'Song': 'Song of Solomon', 'Song of Songs': 'Song of Solomon', 'SOS': 'Song of Solomon', 'Canticles': 'Song of Solomon', 'Cant': 'Song of Solomon', 'Sol': 'Song of Solomon', 'Song of Solomon': 'Song of Solomon',
    # Isaiah
    'Isa': 'Isaiah', 'Is': 'Isaiah', 'Isaiah': 'Isaiah',
    # Jeremiah
    'Jer': 'Jeremiah', 'Jr': 'Jeremiah', 'Jeremiah': 'Jeremiah',
    # Lamentations
    'Lam': 'Lamentations', 'Lamentations': 'Lamentations',
    # Ezekiel
    'Ezek': 'Ezekiel', 'Eze': 'Ezekiel', 'Ezekiel': 'Ezekiel',
    # Daniel
    'Dan': 'Daniel', 'Daniel': 'Daniel',
    # Hosea
    'Hos': 'Hosea', 'Hosea': 'Hosea',
    # Joel
    'Joel': 'Joel', 'Jl': 'Joel',
    # Amos
    'Amos': 'Amos', 'Am': 'Amos',
    # Obadiah
    'Obad': 'Obadiah', 'Obadiah': 'Obadiah', 'Ob': 'Obadiah',
    # Jonah
    'Jonah': 'Jonah', 'Jon': 'Jonah',
    # Micah
    'Mic': 'Micah', 'Micah': 'Micah',
    # Nahum
    'Nah': 'Nahum', 'Nahum': 'Nahum',
    # Habakkuk
    'Hab': 'Habakkuk', 'Habakkuk': 'Habakkuk',
    # Zephaniah
    'Zeph': 'Zephaniah', 'Zephaniah': 'Zephaniah', 'Zep': 'Zephaniah',
    # Haggai
    'Hag': 'Haggai', 'Haggai': 'Haggai',
    # Zechariah
    'Zech': 'Zechariah', 'Zec': 'Zechariah', 'Zechariah': 'Zechariah',
    # Malachi
    'Mal': 'Malachi', 'Malachi': 'Malachi',
    # Add all New Testament books similarly...
}

# List of canonical book names in order
CANONICAL_BOOK_NAMES = [
    'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua',
    'Judges', 'Ruth', '1 Samuel', '2 Samuel', '1 Kings', '2 Kings',
    '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job',
    'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah',
    'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel',
    'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah',
    'Haggai', 'Zechariah', 'Malachi',
    # ...NT books...
]
