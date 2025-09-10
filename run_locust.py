import subprocess
import os

def run_locust():
    root = os.path.dirname(os.path.abspath(__file__))
    locustfile = os.path.join(root, "locustfiles", "doctorin_e2e_appointments.py")

    reports_dir = os.path.join(root, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    cmd = [
        "locust",
        "-f", locustfile,
        "--host", "https://testapp.doctorin.app",
        "-u", "100",
        "-r", "10",
        "-t", "2m",
        "--headless",
        "--csv", os.path.join(reports_dir, "doctorin_run"),
        "--csv-full-history"
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([
        env.get("PYTHONPATH", ""),
        os.path.join(root, "locustfiles")
    ])

    print(">>> Locust başlatılıyor...\n")
    subprocess.run(cmd, env=env)

if __name__ == "__main__":
    run_locust()
