from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional

@dataclass
class Shift:
    shift_id: int
    doctor_id: int
    day_date: date
    start_time: time
    end_time: time