ANALYTICAL_KEYWORDS = [
    "explain", "why", "workflow", "architecture",
    "process", "methodology", "approach"
]

METADATA_KEYWORDS = [
    "author", "authors", "journal", "published", "year", "title"
]


def is_analytical_question(query: str) -> bool:
    q = query.lower()
    return any(q.startswith(k) or f" {k} " in q for k in ANALYTICAL_KEYWORDS)


def is_metadata_question(query: str) -> bool:
    q = query.lower()
    return any(k in q for k in METADATA_KEYWORDS)



