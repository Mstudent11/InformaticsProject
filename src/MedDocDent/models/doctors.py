from dataclasses import dataclass
from typing import Optional

@dataclass
class Doctor:
    user_id: int
    specialty: str
    shift_type: Optional[str] = None