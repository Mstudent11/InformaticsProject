from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Patient:
    user_id: int
    birth_date: date
    gender: Optional[str] = None
    policy_number: Optional[str] = None
    contact_phone: Optional[str] = None