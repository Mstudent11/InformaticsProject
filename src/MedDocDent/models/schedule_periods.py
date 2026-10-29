from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional

@dataclass
class SchedulePeriod:
    period_id: int
    doctor_id: int
    start_date: date
    end_date: date
    type: str  # VACATION, TRAINING, etc.
