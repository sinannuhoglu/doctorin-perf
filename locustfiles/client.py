from typing import Dict, Any

class DoctorinClient:
    """
    Sadece case'de verilen endpoint'lerle çalışan basit istemci.
    - GET /               : UI ayakta mı/warmup
    - GET /appointment-service/appointments : randevu listesi
    """
    def __init__(self, http_client, cfg: Dict[str, Any]):
        self.client = http_client
        self.cfg = cfg

    def open_dashboard(self):
        with self.client.get(self.cfg["urls"]["dashboard"], name="/", catch_response=True) as r:
            r.success() if 200 <= r.status_code < 400 else r.failure(f"/ {r.status_code}")

    def list_appointments(self):
        path = self.cfg["urls"]["appointments_list"]
        with self.client.get(path, name="/appointment-service/appointments", catch_response=True) as r:
            if 200 <= r.status_code < 300:
                r.success()
            else:
                body = (r.text or "")[:200].replace("\n", " ")
                r.failure(f"List failed {r.status_code}: {body}")

