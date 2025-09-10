import csv, os, sys

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def pick_key(row, *candidates):
    for k in candidates:
        if k in row:
            return k
    raise KeyError(f"Expected one of {candidates}, but row has keys: {list(row.keys())}")

def summarize_from_stats(stats_rows):
    """
    doctorin_run_stats.csv içinden 'Aggregated' satırını bularak özet çıkarır.
    """
    agg = None
    for r in stats_rows:
        if r.get("Name", "").strip().lower() == "aggregated":
            agg = r
            break
    if not agg:
        agg = {"Requests": 0, "Failures": 0, "Average Response Time": 0.0}
        total_w = 0
        for r in stats_rows:
            if r.get("Name", "").strip().lower() in ("", "aggregated"):
                continue
            req = int(r.get("Requests", "0") or 0)
            fail = int(r.get("Failures", "0") or 0)
            avg_key = "Average Response Time" if "Average Response Time" in r else "Avg"
            avg = float(r.get(avg_key, "0") or 0.0)
            agg["Requests"] += req
            agg["Failures"] += fail
            agg["Average Response Time"] += avg * req
            total_w += req
        if total_w:
            agg["Average Response Time"] = int(agg["Average Response Time"] / total_w)

    req_key = pick_key(agg, "Requests", "# requests", "Request Count")
    fail_key = pick_key(agg, "Failures", "# failures", "Failure Count")
    avg_key = "Average Response Time" if "Average Response Time" in agg else pick_key(
        agg, "Avg Response Time", "Average"
    )
    print("# Summary")
    print(f"- Requests: {agg[req_key]}, Fails: {agg[fail_key]}")
    print(f"- Avg resp (ms): {agg[avg_key]}")

def list_endpoints(stats_rows):
    print("\n# Endpoints")
    for r in stats_rows:
        name = r.get("Name", "").strip()
        if name.lower() == "aggregated":
            continue
        method = r.get("Method", "").strip()
        p50 = r.get("50%", r.get("Median Response Time", ""))
        p95 = r.get("95%", "")
        p99 = r.get("99%", "")
        avg = r.get("Average Response Time", r.get("Avg Response Time", ""))
        print(f"  * {method} {name}: p50={p50} p95={p95} p99={p99} avg={avg} ms")

def summarize_from_history(hist_rows):
    """
    doctorin_run_stats_history.csv içinden en son 'Aggregated' satırı alır.
    """
    target = None
    for r in reversed(hist_rows):
        if r.get("Name", "").strip().lower() == "aggregated":
            target = r
            break
    if not target:
        target = hist_rows[-1]

    req_key  = pick_key(target, "Requests", "# requests", "Request Count")
    fail_key = pick_key(target, "Failures", "# failures", "Failure Count")
    rps_key  = "Requests/s" if "Requests/s" in target else pick_key(target, "Total RPS", "RPS")
    avg_key  = "Average Response Time" if "Average Response Time" in target else pick_key(
        target, "Avg Response Time", "Average"
    )
    print("# Summary")
    print(f"- Requests: {target[req_key]}, Fails: {target[fail_key]}, RPS: {float(target[rps_key]):.2f}")
    print(f"- Avg resp (ms): {float(target[avg_key]):.0f}")

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    reports = os.path.join(root, "reports")
    stats_path = os.path.join(reports, "doctorin_run_stats.csv")
    hist_path  = os.path.join(reports, "doctorin_run_stats_history.csv")

    if os.path.exists(stats_path):
        stats_rows = read_csv(stats_path)
        summarize_from_stats(stats_rows)
        list_endpoints(stats_rows)
        print("\nNot: SLA kontrolü run bitiminde otomatik (exit code).")
        return

    if os.path.exists(hist_path):
        hist_rows = read_csv(hist_path)
        summarize_from_history(hist_rows)
        print("\nNot: SLA kontrolü run bitiminde otomatik (exit code).")
        return

    print("Raporlar bulunamadı. Önce 'python run_locust.py' çalıştırın.")

if __name__ == "__main__":
    main()
