import csv, random
from typing import List, Dict
from datetime import datetime

def load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline='', encoding="utf-8") as f:
        return list(csv.DictReader(f))

def choose(items: list):
    return random.choice(items)

def iso_start(hour_24: int, minute: int) -> str:
    dt = datetime.utcnow().replace(hour=hour_24, minute=minute, second=0, microsecond=0)
    return dt.isoformat(timespec="seconds") + "Z"
