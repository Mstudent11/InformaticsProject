from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    user_id: int
    login: str
    password_hash: str
    role: str  # 'ADMIN', 'DOCTOR', 'PATIENT'
    name: str
    surname: str
    patronymic: str
    contact_phone: Optional[str] = None