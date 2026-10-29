from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional

@dataclass
class Patient:
    patient_id: int
    user_id: int
    birth_date: date
    gender: Optional[str] = None
    policy_number: Optional[str] = None
    contact_phone: Optional[str] = None
