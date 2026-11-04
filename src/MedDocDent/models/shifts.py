from dataclasses import dataclass
from datetime import date, time

@dataclass
class Shift:
    shift_id: int
    doctor_id: int
    day_date: date
    start_time: time
    end_time: time