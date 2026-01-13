from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class Patient:
    patient_id: str
    name: str
    age: int
    condition: str
    risk_level: str
    therapist_id: str


@dataclass
class Device:
    device_id: str
    patient_id: str
    status: str
    battery_pct: int
    last_seen_at: datetime
    firmware: str
