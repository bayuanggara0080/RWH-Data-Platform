# 🇮🇩 RWH-OS: Enterprise Distributed Data Mesh & Lakehouse Control Plane

[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![DuckDB](https://img.shields.io/badge/DuckDB-OLAP%20Engine-FFF000.svg?style=flat&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5-E25A1C.svg?style=flat&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Apache Iceberg](https://img.shields.io/badge/Apache%20Iceberg-ACID%20Lakehouse-2684FF.svg?style=flat)](https://iceberg.apache.org/)
[![Multi-Cloud](https://img.shields.io/badge/Multi--Cloud-AWS%20|%20GCP%20|%20Azure-232F3E.svg?style=flat)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**RWH-OS** adalah platform *Data Engineering Operating System* skala enterprise yang menggabungkan kemampuan pemrosesan streaming berkecepatan sub-detik, *in-memory OLAP analytics*, pemodelan dimensional *Kimball Star Schema*, tata kelola data berbasis enkripsi satu arah (kepatuhan UU PDP & GDPR), orkestrasi pipeline otomatis, serta integrasi *Multi-Cloud Lakehouse* (AWS S3, GCP Storage, Azure Blob).

---

## 🏛️ Arsitektur Sistem

```text
 [ INGRESS LAYER ]        [ PROCESSING & GOVERNANCE ]        [ STORAGE & ANALYTICS ]
 ┌─────────────────┐      ┌─────────────────────────┐        ┌─────────────────────┐
 │ Relational DB   │ ───► │ DuckDB (In-Memory OLAP) │ ─────► │ Apache Iceberg / S3 │
 │ Live WebSocket  │ ───► │ PySpark Distributed     │ ─────► │ Google Cloud Bucket │
 │ Apache Kafka    │ ───► │ SHA-256 PII Shield      │ ─────► │ Azure Blob Storage  │
 │ REST API / Docs │ ───► │ Kimball Star Schema     │ ─────► │ Plotly BI Dashboard │
 └─────────────────┘      └─────────────────────────┘        └─────────────────────┘
```

---

## 🚀 Fitur Utama

* **Omni-Source Ingestion**: Ekstraksi batch dari RDBMS (MySQL & PostgreSQL), file dokumen (CSV, Parquet, JSON, Excel), serta *stream listener* untuk Live WebSocket jaringan global dan Apache Kafka.
* **Sub-Second OLAP Engine**: Agregasi analitik instan dengan **DuckDB** tanpa membebani memori utama (*Zero-Copy Query Engine*).
* **Data Privacy Vault (UU PDP / GDPR)**: Modul *cryptographic hashing* satu arah SHA-256 untuk menyamarkan identitas sensitif pengguna secara permanen.
* **Automated Kimball Modeling**: Pemecahan otomatis tabel datar transaksi e-commerce menjadi arsitektur *Star Schema* (*Fact Table* & *Dimension Tables*).
* **AI-Assisted SQL IDE**: Penerjemah instruksi bahasa alami menjadi query analitik DuckDB teroptimasi secara instan.
* **Distributed Spark & Airflow Trigger**: Antarmuka kontrol terpadu untuk *remote job submission* ke cluster Apache Spark dan pemicu otomatis *Apache Airflow DAG*.
* **Multi-Cloud Lakehouse Sync**: Sinkronisasi dataset Parquet terkompresi langsung ke AWS S3, Google Cloud Storage, Azure Blob, dan partisi fisik lokal (Hive Partitioning).
* **Interactive Lineage DAG**: Visualisasi silsilah aliran data (*Data Lineage Graph*) secara dinamis dari hulu ke hilir.

---

## 📂 Struktur Repositori

```text
god-data-platform/
│
├── docker-compose.yml              # Cluster Kafka, Zookeeper, Spark Master/Workers, Airflow
├── terraform/
│   └── main.tf                     # Infrastructure as Code (AWS S3 Bucket & KMS)
├── dags/
│   └── dag_ecommerce_master.py     # Production Airflow Orchestration Pipeline
├── spark_jobs/
│   └── process_iceberg_stream.py   # Distributed PySpark & Iceberg ACID Stream Job
├── dbt_project/
│   └── models/                     # Medallion Architecture (Bronze -> Silver -> Gold)
├── requirements.txt                # Python Dependencies
├── app.py                          # Streamlit Mission Control Plane
└── README.md                       # Dokumentasi Arsitektur
```

---

## 🛠️ Panduan Instalasi Lengkap (Step-by-Step)

### 1. Prasyarat Sistem
* **Python 3.9+** ([Unduh Python](https://www.python.org/downloads/))
* **Git** ([Unduh Git](https://git-scm.com/downloads))
* *(Opsional)* **Docker Desktop** ([Unduh Docker](https://www.docker.com/products/docker-desktop/)) untuk menjalankan cluster Apache Spark & Kafka terdistribusi.

---

### 2. Kloning Repositori
Buka terminal (PowerShell / Command Prompt / Terminal), lalu jalankan:
```bash
git clone https://github.com/username-kamu/garuda-data-platform.git
cd garuda-data-platform
```
*(Ganti `username-kamu` dengan username GitHub milikmu).*

---

### 3. Setup Virtual Environment

#### 🪟 Windows (PowerShell):
```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
. env\Scripts\Activate.ps1
```
*(Setelah aktif, akan muncul tanda `(venv)` di sebelah kiri terminal).*

#### 🍏 macOS / 🐧 Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Instalasi Dependensi Python
Pastikan `pip` sudah dalam versi terbaru, lalu instal semua dependensi:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

*Jika belum memiliki `requirements.txt`, jalankan perintah instalasi langsung berikut:*
```bash
pip install streamlit pandas numpy duckdb sqlalchemy pymysql requests websocket-client plotly graphviz boto3 azure-storage-blob google-cloud-storage openpyxl pyarrow
```

---

### 5. Menjalankan Aplikasi
Jalankan perintah ini di terminal yang sedang aktif `(venv)`:
```bash
streamlit run app.py
```

Platform akan otomatis terbuka di browser pada alamat:
👉 **`http://localhost:8501`**

---

### 6. (Opsional) Menjalankan Cluster Spark & Kafka (Docker)
Jika ingin mengaktifkan infrastruktur cluster compute nyata di lokal:
1. Buka aplikasi **Docker Desktop** hingga statusnya running.
2. Jalankan perintah:
```bash
docker compose up -d
```
3. Cluster Apache Spark Master/Worker (`localhost:8080`), Kafka Broker (`localhost:9092`), dan PostgreSQL Warehouse (`localhost:5432`) akan aktif di latar belakang.

---

## 📄 Lisensi
Didistribusikan di bawah lisensi MIT. Lihat file `LICENSE` untuk informasi lebih lanjut.
