from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class VectorRecord:
    embedding: Any
    metadata: Dict
