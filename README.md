# 🇮🇩 RWH-OS: Enterprise Distributed Data Mesh & Lakehouse Control Plane

[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![DuckDB](https://img.shields.io/badge/DuckDB-OLAP%20Engine-FFF000.svg?style=flat&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5-E25A1C.svg?style=flat&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Apache Iceberg](https://img.shields.io/badge/Apache%20Iceberg-ACID%20Lakehouse-2684FF.svg?style=flat)](https://iceberg.apache.org/)
[![Multi-Cloud](https://img.shields.io/badge/Multi--Cloud-AWS%20|%20GCP%20|%20Azure-232F3E.svg?style=flat)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**RWH-OS** adalah platform *Data Engineering Operating System* skala enterprise yang menggabungkan kemampuan pemrosesan streaming berkecepatan sub-detik, *in-memory OLAP analytics*, pemodelan dimensional *Kimball Star Schema*, tata kelola data berbasis enkripsi satu arah (kepatuhan UU PDP & GDPR), orkestrasi pipeline otomatis, serta integrasi *Multi-Cloud Lakehouse* (AWS S3, GCP Storage, Azure Blob).

---

##  Arsitektur Sistem

```text
 [ INGRESS LAYER ]        [ PROCESSING & GOVERNANCE ]        [ STORAGE & ANALYTICS ]
 ┌─────────────────┐      ┌─────────────────────────┐        ┌─────────────────────┐
 │ Relational DB   │ ───► │ DuckDB (In-Memory OLAP) │ ─────► │ Apache Iceberg / S3 │
 │ Live WebSocket  │ ───► │ PySpark Distributed     │ ─────► │ Google Cloud Bucket │
 │ Apache Kafka    │ ───► │ SHA-256 PII Shield      │ ─────► │ Azure Blob Storage  │
 │ REST API / Docs │ ───► │ Kimball Star Schema     │ ─────► │ Plotly BI Dashboard │
 └─────────────────┘      └─────────────────────────┘        └─────────────────────┘
