
# Doctorin Performans Testi (Locust)

Bu depo, **Doctorin** platformu için **Locust** kullanılarak hazırlanmış, senaryolaştırılabilir ve **SLA doğrulamalı** bir performans testidir.

 ### **Öne çıkanlar**
 - Tek komutla headless koşum (`run_locust.py`)
 - **SLA Guard**: p95 eşikleri ihlal edilirse **exit code ≠ 0** (CI/CD için ideal)
 - CSV raporları + konsol özetleyici (`scripts/summarize_run.py`)
 - Parametrik yük (kullanıcı sayısı, ramp hızı, süre) ve YAML konfigürasyonu

---

## Proje Yapısı

```
doctorin-perf/
├─ config/
│  └─ perf_config.yaml                 # host, endpointler, bekleme aralığı, SLA eşiği
├─ data/
│  ├─ doctors.csv
│  ├─ patients.csv
│  └─ users.csv                        # placeholder verileri (min. senaryo için opsiyonel)
├─ locustfiles/
│  ├─ client.py                        # basit HTTP istemci sarmalayıcı
│  ├─ doctorin_e2e_appointments.py     # Locust user + görevler (anasayfa, randevu listesi)
│  ├─ sla_guard.py                     # p95 SLA kontrolü (exit code ayarı)
│  └─ utils.py                         # yardımcı fonksiyonlar
├─ reports/                            # koşum sonrası CSV raporları buraya düşer
│  ├─ doctorin_run_stats.csv
│  ├─ doctorin_run_failures.csv
│  ├─ doctorin_run_exceptions.csv
│  └─ doctorin_run_stats_history.csv
├─ scripts/
│  └─ summarize_run.py                 # CSV'lerden özet ve endpoint bazlı metrik çıktısı
├─ run_locust.py                       # headless koşum komutu (tek adımda)
└─ requirements.txt
```

---

## Özellikler

- **Locust tabanlı yük testi altyapısı** — tek komutla headless koşum (`run_locust.py`).
- **Ağırlıklı kullanıcı akışları** — randevu listesi (x3) + anasayfa (x1); **warm-up** ve **think time** (500–1500 ms).
- **YAML ile yapılandırma** — host, endpointler, runtime aralığı ve **SLA p95** eşikleri (`config/perf_config.yaml`).
- **SLA guard (p95)** — koşum sonunda otomatik kontrol; ihlalde **non-zero exit code** (CI dostu).
- **Raporlama** — CSV istatistikleri (stats/history/failures/exceptions) + `scripts/summarize_run.py` ile p50/p95/p99 özeti.
- **Ölçeklenebilir yük profili** — `-u` (kullanıcı), `-r` (spawn rate), `-t` (süre) parametreleriyle esnek ayar.
- **Veri fikstürleri** — `data/*.csv` placeholder’ları (kullanıcı/doktor/hasta) ile akışları genişletmeye hazır.
- **Genişletilebilir istemci** — `DoctorinClient` yapısı yeni endpoint/metot eklemeyi kolaylaştırır.

---

## Teknolojiler ve Kullanım Amaçları

| Bileşen / Alan          | Teknoloji / Araç                | Sürüm            | Amaç / Kullanım                                                                 | Konum / Örnek Dosya |
|-------------------------|---------------------------------|------------------|----------------------------------------------------------------------------------|---------------------|
| Yük testi               | **Locust**                      | 2.40.1           | Kullanıcı modeli, görev ağırlıkları, headless koşum, CSV export                  | `locustfiles/doctorin_e2e_appointments.py`, `run_locust.py` |
| HTTP istemci            | **Locust HttpUser client**      | —                | `GET /` ve `GET /appointment-service/appointments` istekleri                    | `locustfiles/client.py` |
| SLA doğrulama           | **Locust events API**           | —                | Koşum sonunda **p95** kontrolü, ihlalde **non-zero exit code**                  | `locustfiles/sla_guard.py` |
| Konfigürasyon           | **YAML** (+ **PyYAML**)         | ≥ 6.0.1          | Host, endpoint yolları, bekleme aralığı, **SLA p95** eşiği                      | `config/perf_config.yaml` |
| Raporlama               | **CSV** (Locust exporter)       | —                | `stats`, `history`, `failures`, `exceptions` CSV dosyaları                      | `reports/*.csv` |
| Konsol özeti            | **Python csv stdlib**           | 3.10+            | p50/p95/p99 ve özet metriklerin konsola yazdırılması                            | `scripts/summarize_run.py` |
| Veri fikstürleri        | **CSV**                          | —                | Genişletilebilir örnek veri (kullanıcı/doktor/hasta)                            | `data/*.csv` |
| Ortam                   | **Python** + **venv**           | 3.10+            | Sanal ortam ve paket yönetimi                                                   | `requirements.txt` |

## Raporlama ve Çıktılar

Koşum sonunda **CSV** raporlar:
- `doctorin_run_stats.csv` → her endpoint için **Request Count**, **Failure Count**, **Median/Avg**, **Min/Max**, **p50/p95/p99** ve throughput alanları
- `doctorin_run_stats_history.csv` → zaman serisi
- `doctorin_run_failures.csv` / `doctorin_run_exceptions.csv` → varsa hata/exception detayları
