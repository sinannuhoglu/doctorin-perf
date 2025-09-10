from locust import events

def register_sla_guard(sla_ms: dict, percentile: float = 0.95):
    """
    Run sonunda pXX'e göre SLA kontrolü yapar; ihlal varsa process exit code != 0.
    sla_ms örn: {"GET /": 2000, "GET /appointment-service/appointments": 1500}
    """
    if not sla_ms:
        return

    def resolve_entry(stats, method: str, path_or_name: str):
        """
        Locust istatistiğini farklı ad biçimlerine karşı dayanıklı şekilde bul.
        Denenen sıralar:
          (name=path, method)
          (name=f"{method} {path}", method)
          (name=path, method="")
          (name=f"{method} {path}", method="")
          Son çare: entries içinde normalize eşleşme
        """
        probes = [
            (path_or_name, method),
            (f"{method} {path_or_name}", method),
            (path_or_name, ""),
            (f"{method} {path_or_name}", ""),
        ]
        for name, meth in probes:
            e = stats.get(name, meth)
            if e:
                return e

        try:
            items = getattr(stats, "entries", {}).items()
        except Exception:
            items = []
        for (m, n), e in items:
            if m == method and (n == path_or_name or n == f"{method} {path_or_name}"):
                return e
            if m in ("", None) and (n == path_or_name or n == f"{method} {path_or_name}"):
                return e
        return None

    @events.quitting.add_listener
    def _(environment, **kw):
        stats = environment.stats
        breaches = []

        for key, limit in sla_ms.items():
            if " " in key.strip():
                method, name = key.split(" ", 1)
            else:
                method, name = "GET", key.strip()

            entry = resolve_entry(stats, method.strip(), name.strip())
            val = entry.get_response_time_percentile(percentile) if entry else None

            if val is None:
                breaches.append(f"{method} {name}: istatistik bulunamadı (ad eşleşmedi)")
                continue

            if val > limit:
                breaches.append(
                    f"{method} {name}: p{int(percentile*100)}={int(val)}ms > SLA {int(limit)}ms"
                )

        if breaches:
            print("\nSLA breaches:")
            for b in breaches:
                print(" -", b)
            environment.process_exit_code = 1
        else:
            print("\nAll SLAs met.")
