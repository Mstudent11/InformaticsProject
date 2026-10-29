from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional

@dataclass
class Doctor:
    doctor_id: int
    user_id: int
    specialty: str
    shift_type: Optional[str] = None