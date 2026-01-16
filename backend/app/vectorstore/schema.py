from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class VectorRecord:
    text: str
    embedding: Any
    metadata: Dict
    score: float | None = None
    block_type: str = "text"

