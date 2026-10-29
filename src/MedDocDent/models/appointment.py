from dataclasses import dataclass
from datetime import date, time, datetime
from typing import Optional, List

@dataclass
class Appointment:
    appointment_id: int
    patient_id: int
    shift_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    status: str