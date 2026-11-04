from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Appointment:
    appointment_id: int
    patient_id: int
    shift_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str  # 'BOOKED', 'COMPLETED' и т.п.