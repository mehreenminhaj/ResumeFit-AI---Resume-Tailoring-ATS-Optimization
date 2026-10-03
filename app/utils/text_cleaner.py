import re
from collections import Counter
from typing import Dict, List, Set

STOP_WORDS: Set[str] = {
    'the', 'and', 'for', 'with', 'that', 'this', 'from', 'have', 'are', 'you', 'will',
    'our', 'team', 'work', 'your', 'about', 'join', 'opportunity', 'company', 'role',
    'looking', 'candidate', 'skills', 'experience', 'years', 'working', 'ability', 'must',
    'responsible', 'requirements', 'qualifications', 'such', 'well', 'using', 'plus',
    'strong', 'knowledge', 'understanding', 'preferred', 'across', 'including', 'can',
    'all', 'any', 'each', 'more', 'other', 'into', 'over', 'than', 'them', 'then'
}


def clean_text(text: str) -> str:
    """Normalizes whitespace and removes unwanted control characters."""
    if not text:
        return ""
    text = re.sub(r'[\r\f\v]+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def normalize_term(term: str) -> str:
    """Lowercases, trims, and cleans bullet symbols from terms."""
    if not term:
        return ""
    cleaned = re.sub(r'^[•\-\*\s]+', '', term.lower().strip())
    return cleaned


def extract_keywords_from_text(text: str, top_n: int = 40) -> Dict[str, int]:
    """
    Extracts frequency of meaningful keywords, supporting terms like c++, c#, .net, node.js
    """
    if not text:
        return {}

    # Regular expression capturing programming terms with punctuation (+, #, .)
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.]*\b", text.lower())

    filtered = []
    for word in words:
        w = word.strip('.')
        if len(w) > 2 and w not in STOP_WORDS and not w.isdigit():
            filtered.append(w)

    counts = Counter(filtered)
    return dict(counts.most_common(top_n))
