from dataclasses import dataclass
from datetime import date

@dataclass
class SchedulePeriod:
    period_id: int
    doctor_id: int
    start_date: date
    end_date: date
    type: str  # например: 'VACATION', 'TRAINING', 'WORK'
