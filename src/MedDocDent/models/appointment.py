from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Appointment:
    appointment_id: int
    patient_id: int
    shift_id: int
    created_at: str
    updated_at: Optional[str] = None
    status: str = 'BOOKED'  # 'BOOKED', 'COMPLETED' и т.п.