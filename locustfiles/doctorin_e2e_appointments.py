import os
import sys
import yaml
from locust import HttpUser, task, between

CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from client import DoctorinClient
from sla_guard import register_sla_guard

ROOT = os.path.dirname(os.path.dirname(__file__))
CFG_PATH = os.path.join(ROOT, "config", "perf_config.yaml")
with open(CFG_PATH, "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

register_sla_guard(CFG.get("sla_ms", {}), percentile=0.95)


class DoctorinUser(HttpUser):
    """
    - on_start: dashboard warmup
    - Tasks:
       * t_list_appointments: /appointment-service/appointments (3 ağırlık)
       * t_homepage: GET / (1 ağırlık)
    """
    wait_time = between(
        CFG["runtime"]["min_wait_ms"] / 1000.0,
        CFG["runtime"]["max_wait_ms"] / 1000.0,
    )

    def on_start(self):
        self.api = DoctorinClient(self.client, CFG)
        self.api.open_dashboard()

    @task(3)
    def t_list_appointments(self):
        self.api.list_appointments()

    @task(1)
    def t_homepage(self):
        self.api.open_dashboard()
