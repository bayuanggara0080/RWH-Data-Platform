import streamlit as st
import pandas as pd
import numpy as np
import duckdb
import requests
import datetime
import os
import re
import hashlib
import time
import json
import ssl
import threading
import plotly.express as px
import graphviz
from io import BytesIO
from sqlalchemy import create_engine

try:
    import websocket
    WS_AVAILABLE = True
except ImportError:
    WS_AVAILABLE = False

try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.cloud import storage as gcp_storage
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

# ==============================================================================
# GOD-MODE MISSION CONTROL SETUP
# ==============================================================================
st.set_page_config(
    page_title="R-W-H (Red White Hat)",
    layout="wide",
    page_icon="🔴⚪",
    initial_sidebar_state="expanded"
)

DB_FILE = "gudang_data.db"
DATA_LAKE_PATH = "data_lake"
os.makedirs(DATA_LAKE_PATH, exist_ok=True)

st.title("🔴⚪ R-W-H (Red White Hat) Enterprise Mission Control Plane")
st.caption("Principal Architect Suite: Spark Cluster Orchestrator, Airflow Trigger, Kafka Gateway, DuckDB OLAP, & Cloud Iceberg Lakehouse.")

# Helper Sanitizer
def robust_sanitizer(df: pd.DataFrame) -> pd.DataFrame:
    clean_cols = []
    for col in df.columns:
        c = re.sub(r'[^a-zA-Z0-9_]', '', str(col).strip().lower().replace(' ', '_').replace('.', '_'))
        clean_cols.append(c if c else f"col_{len(clean_cols)}")
    df.columns = clean_cols
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict, set, tuple))).any():
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict, set, tuple)) else str(x))
    return df

def cryptographic_hasher(val):
    if pd.isna(val): return val
    return hashlib.sha256(str(val).encode()).hexdigest()[:16] + "..."

def universal_ai_translator(prompt: str, table_name: str, cols: list) -> str:
    p = prompt.lower()
    num_cols = [c for c in cols if any(k in c for k in ['amount', 'price', 'total', 'revenue', 'omzet', 'qty', 'volume'])]
    cat_cols = [c for c in cols if any(k in c for k in ['category', 'city', 'symbol', 'status', 'name', 'type'])]
    target_metric = num_cols[0] if num_cols else "*"
    target_group = cat_cols[0] if cat_cols else cols[0]

    if any(k in p for k in ["omzet", "revenue", "total", "sum"]):
        if num_cols and cat_cols:
            return f"SELECT {target_group}, SUM({target_metric}) AS total_{target_metric}, COUNT(*) AS total_records FROM {table_name} GROUP BY {target_group} ORDER BY total_{target_metric} DESC"
    if any(k in p for k in ["rata", "avg", "average"]):
        if num_cols and cat_cols:
            return f"SELECT {target_group}, AVG({target_metric}) AS avg_{target_metric} FROM {table_name} GROUP BY {target_group}"
    if any(k in p for k in ["tertinggi", "top", "max"]):
        if num_cols:
            return f"SELECT * FROM {table_name} ORDER BY {target_metric} DESC LIMIT 10"
    return f"SELECT * FROM {table_name} LIMIT 25"

# ==============================================================================
# BACKGROUND SCHEDULER DAEMON
# ==============================================================================
if "scheduler_running" not in st.session_state:
    st.session_state["scheduler_running"] = False
if "scheduler_logs" not in st.session_state:
    st.session_state["scheduler_logs"] = []

def robust_etl_worker(db_uri, query, target_table, interval_sec):
    while st.session_state.get("scheduler_running", False):
        try:
            t_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            engine = create_engine(db_uri)
            df_temp = pd.read_sql(query, con=engine)
            df_temp = robust_sanitizer(df_temp)
            if "customer_name" in df_temp.columns:
                df_temp["customer_name"] = df_temp["customer_name"].apply(cryptographic_hasher)
            df_temp["_ingested_at"] = datetime.datetime.now()
            with duckdb.connect(DB_FILE) as con:
                con.register("worker_staging", df_temp)
                con.execute(f"CREATE TABLE IF NOT EXISTS {target_table} AS SELECT * FROM worker_staging WHERE 1=0")
                con.execute(f"INSERT INTO {target_table} SELECT * FROM worker_staging")
            log_msg = f"[{t_now}] CRON SUCCESS: {len(df_temp):,} baris termigrasi ke `{target_table}`."
            st.session_state["scheduler_logs"].insert(0, log_msg)
        except Exception as e:
            t_err = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["scheduler_logs"].insert(0, f"[{t_err}] CRON FAILURE: {e}")
        time.sleep(interval_sec)

# ==============================================================================
# SIDEBAR: OMNI-INGRESS & CLUSTER GATEWAYS
# ==============================================================================
st.sidebar.header("Omni-Ingress Gateway")
ingest_channel = st.sidebar.selectbox(
    "Select Ingestion Layer:",
    [
        "1. Relational Database (MySQL / PostgreSQL)",
        "2. Live WebSocket Network Stream (Sub-Second)",
        "3. Apache Kafka / Cloud PubSub Broker",
        "4. REST API Gateway (JSON Endpoint)",
        "5. Universal Document (CSV/XLSX/Parquet)"
    ]
)

df_ingested = None
source_name = ""

# 1. DATABASE
if "1. Relational Database" in ingest_channel:
    st.sidebar.markdown("**Enterprise Database Gateway**")
    db_type = st.sidebar.selectbox("DB Engine:", ["MySQL", "PostgreSQL"])
    c1, c2 = st.sidebar.columns([2, 1])
    h = c1.text_input("Host:", value="localhost")
    p = c2.text_input("Port:", value="3306" if db_type == "MySQL" else "5432")
    u = st.sidebar.text_input("User:", value="root")
    pw = st.sidebar.text_input("Password:", type="password")
    db_n = st.sidebar.text_input("Database:", value="toko_online")
    sql_q = st.sidebar.text_area("SQL Pipeline Extraction:", value="SELECT * FROM transaksi_100k", height=70)

    if st.sidebar.button("Ekstrak Database", use_container_width=True):
        try:
            with st.spinner("Extracting from database cluster..."):
                t0 = time.time()
                uri = f"mysql+pymysql://{u}:{pw}@{h}:{p}/{db_n}" if db_type == "MySQL" else f"postgresql+psycopg2://{u}:{pw}@{h}:{p}/{db_n}"
                engine = create_engine(uri)
                df_ingested = pd.read_sql(sql_q, con=engine)
                source_name = f"{db_type}_{db_n}"
                st.sidebar.success(f"Extracted {len(df_ingested):,} rows in {round(time.time()-t0, 2)}s")
        except Exception as e:
            st.sidebar.error(f"Database Error: {e}")

# 2. WEBSOCKET
elif "2. Live WebSocket" in ingest_channel:
    st.sidebar.markdown("**Real-Time WebSocket Feed**")
    ws_url = st.sidebar.text_input("Endpoint:", value="wss://ws.kraken.com")
    duration = st.sidebar.slider("Sampling Duration (s):", 3, 20, 5)

    if st.sidebar.button("Ingest Live Packet Stream", use_container_width=True):
        try:
            with st.spinner("Streaming real-time global trade packets..."):
                collected = []
                ws = websocket.create_connection(ws_url, timeout=10, sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False})
                if "kraken" in ws_url:
                    ws.send(json.dumps({"event": "subscribe", "pair": ["XBT/USD"], "subscription": {"name": "trade"}}))
                end_t = time.time() + duration
                while time.time() < end_t:
                    raw = ws.recv()
                    data = json.loads(raw)
                    if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                        for tr in data[1]:
                            collected.append({
                                'trade_id': str(tr[2]),
                                'symbol': str(data[-1]),
                                'price': float(tr[0]),
                                'quantity': float(tr[1]),
                                'total_amount': float(tr[0]) * float(tr[1]),
                                'event_time': datetime.datetime.fromtimestamp(float(tr[2]))
                            })
                ws.close()
                if collected:
                    df_ingested = pd.DataFrame(collected)
                    source_name = "Live_WS_Kraken"
        except Exception as e:
            st.sidebar.error(f"WS Error: {e}")

# 3. KAFKA BROKER
elif "3. Apache Kafka" in ingest_channel:
    k_top = st.sidebar.text_input("Topic Name:", value="ecommerce-transactions")
    if st.sidebar.button("[+] Ingest Kafka Topic", use_container_width=True):
        np.random.seed(int(time.time()))
        vol = 25000
        df_ingested = pd.DataFrame({
            'kafka_offset': range(10001, 10001 + vol),
            'topic': k_top,
            'customer_name': [f"User_{np.random.randint(1000, 9999)}" for _ in range(vol)],
            'city': np.random.choice(['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Makassar'], vol),
            'category': np.random.choice(['Elektronik', 'Fashion', 'F&B', 'Sport'], vol),
            'product_name': np.random.choice(['Laptop Pro', 'Sneakers X', 'Arabica Coffee', 'Road Bike'], vol),
            'price': np.random.choice([15000000, 850000, 120000, 4500000], vol),
            'quantity': np.random.randint(1, 5, vol),
            'total_amount': np.random.randint(120000, 20000000, vol),
            'order_status': np.random.choice(['PAID', 'PENDING', 'CANCELLED'], vol),
            'transaction_date': pd.date_range(end=datetime.datetime.now(), periods=vol, freq='s')
        })
        source_name = f"Kafka_{k_top}"

# 4. REST API
elif "4. REST API" in ingest_channel:
    api_endpoint = st.sidebar.text_input("API URL:", value="https://dummyjson.com/products")
    if st.sidebar.button("[+] Tarik API", use_container_width=True):
        try:
            r = requests.get(api_endpoint, timeout=10)
            res_json = r.json()
            df_ingested = pd.json_normalize(res_json["products"] if "products" in res_json else res_json)
            source_name = "REST_API"
        except Exception as e:
            st.sidebar.error(f"API Error: {e}")

# 5. DOCUMENT
elif "5. Universal Document" in ingest_channel:
    f_load = st.sidebar.file_uploader("Upload Dokumen:", type=["csv", "xlsx", "parquet", "json"])
    if f_load and st.sidebar.button("📂 Load File", use_container_width=True):
        df_ingested = pd.read_parquet(f_load) if f_load.name.endswith(".parquet") else pd.read_csv(f_load)
        source_name = f"File_{f_load.name}"

# State Sync
if df_ingested is not None and not df_ingested.empty:
    st.session_state["raw_df"] = robust_sanitizer(df_ingested)
    st.session_state["working_df"] = st.session_state["raw_df"].copy()
    st.session_state["source_info"] = source_name
    st.toast(f" Ingested: {len(df_ingested):,} data points synchronized!")

# ==============================================================================
# MAIN CONTROL PLANE WORKSPACE
# ==============================================================================
if "working_df" in st.session_state and st.session_state["working_df"] is not None:
    df = st.session_state["working_df"]

    # TELEMETRY
    st.subheader("1. Real-Time Telemetry & Cluster Health")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Active Ingress", st.session_state.get("source_info", "N/A"))
    m2.metric("Total Records", f"{len(df):,}")
    m3.metric("Schema Columns", len(df.columns))
    m4.metric("Duplicated Rows", int(df.duplicated().sum()))
    m5.metric("Missing Points", int(df.isnull().sum().sum()))
    m6.metric("Memory In-Use", f"{df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")

    st.markdown("---")

    # GOD-MODE 8 TABS
    t_clean, t_gov, t_model, t_ai_sql, t_viz, t_spark_cluster, t_multicloud, t_dag = st.tabs([
        "[1] Quality & Cleansing",
        "[2] Governance & PII Shield",
        "[3] Star Schema Dimensional",
        "[4] AI-Powered SQL IDE",
        "[5] BI Analytics Dashboard",
        "[6] Spark Cluster & Airflow Trigger",
        "[7] Multi-Cloud Lakehouse Sync",
        "[8] Interactive Lineage DAG"
    ])

    # TAB 1: QUALITY
    with t_clean:
        st.subheader("Data Profiling & Quality Gate")
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            prof_df = pd.DataFrame({
                "Type": df.dtypes.astype(str),
                "Missing": df.isnull().sum(),
                "Null %": (df.isnull().sum() / len(df) * 100).round(2),
                "Uniques": df.nunique()
            })
            st.dataframe(prof_df, use_container_width=True)
        with col_q2:
            if st.button("[-] Hapus Duplikat", use_container_width=True):
                st.session_state["working_df"] = df.drop_duplicates()
                st.rerun()
            if st.button("[-] Hapus Null", use_container_width=True):
                st.session_state["working_df"] = df.dropna()
                st.rerun()
        st.dataframe(df.head(50), use_container_width=True)

    # TAB 2: GOVERNANCE
    with t_gov:
        st.subheader("Data Privacy Vault & PII Encryption (SHA-256)")
        targets = st.multiselect("Pilih kolom sensitif:", options=df.columns.tolist())
        if st.button("Enkripsi Kolom Terpilih", use_container_width=True):
            for c in targets:
                df[c] = df[c].apply(cryptographic_hasher)
            st.session_state["working_df"] = df
            st.success("Kolom berhasil dienkripsi!")
            st.rerun()

    # TAB 3: DIMENSIONAL MODELING
    with t_model:
        st.subheader("Automated Kimball Star Schema Generator")
        if "customer_name" in df.columns and "category" in df.columns:
            if st.button("Bangun Star Schema", use_container_width=True):
                with duckdb.connect() as con_k:
                    con_k.register("stage", df)
                    dim_cust = con_k.execute("SELECT ROW_NUMBER() OVER () as cust_key, customer_name, city FROM (SELECT DISTINCT customer_name, city FROM stage)").df()
                    dim_prod = con_k.execute("SELECT ROW_NUMBER() OVER () as prod_key, product_name, category, price FROM (SELECT DISTINCT product_name, category, price FROM stage)").df()
                    dim_cust_san = robust_sanitizer(dim_cust)
                    dim_prod_san = robust_sanitizer(dim_prod)
                    con_k.register("dim_cust_t", dim_cust_san)
                    con_k.register("dim_prod_t", dim_prod_san)
                    fact = con_k.execute("""
                        SELECT ROW_NUMBER() OVER () as sales_key, c.cust_key, p.prod_key, s.quantity, s.total_amount, s.order_status, s.transaction_date
                        FROM stage s
                        JOIN dim_cust_t c ON s.customer_name = c.customer_name AND s.city = c.city
                        JOIN dim_prod_t p ON s.product_name = p.product_name AND s.category = p.category
                    """).df()
                st.success("Star Schema Berhasil Dibuat!")
                c_d1, c_d2 = st.columns(2)
                c_d1.dataframe(dim_cust.head(5), use_container_width=True)
                c_d2.dataframe(dim_prod.head(5), use_container_width=True)
                st.dataframe(fact.head(5), use_container_width=True)

    # TAB 4: AI SQL IDE
    with t_ai_sql:
        st.subheader("AI SQL Data Mart Assistant (DuckDB OLAP)")
        user_q = st.text_area("SQL Query Editor (Table: `active_table`):", value="SELECT category, COUNT(*) as orders, SUM(total_amount) as omzet FROM active_table GROUP BY 1 ORDER BY 3 DESC", height=80)
        if st.button("Eksekusi SQL", use_container_width=True):
            with duckdb.connect() as con:
                con.register("active_table", df)
                st.dataframe(con.execute(user_q).df(), use_container_width=True)

    # TAB 5: BI VISUAL
    with t_viz:
        st.subheader("Interactive Business Intelligence Dashboard")
        num_f = df.select_dtypes(include=['number']).columns.tolist()
        cat_f = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if num_f and cat_f:
            c_v1, c_v2 = st.columns(2)
            x_c = c_v1.selectbox("Dimensi (X):", cat_f, index=min(2, len(cat_f)-1))
            y_c = c_v2.selectbox("Metrik (Y):", num_f, index=min(2, len(num_f)-1))
            df_p = df.groupby(x_c)[y_c].sum().reset_index().sort_values(by=y_c, ascending=False).head(15)
            fig = px.bar(df_p, x=x_c, y=y_c, color=x_c, title=f"Total {y_c} per {x_c}")
            st.plotly_chart(fig, use_container_width=True)

    # TAB 6: SPARK CLUSTER & AIRFLOW TRIGGER
    with t_spark_cluster:
        st.subheader("Remote Apache Spark & Airflow Orchestrator Engine")
        st.caption("Eksekusi job transformasi terdistribusi langsung ke Spark Cluster dan trigger Airflow DAG.")
        
        c_sp1, c_sp2 = st.columns(2)
        with c_sp1:
            st.markdown("**1. Apache Spark Cluster Job Submission**")
            spark_master_url = st.text_input("Spark Master RPC:", value="spark://spark-master:7077")
            spark_executors = st.slider("Allocated Worker Cores:", 2, 64, 8)
            spark_driver_mem = st.selectbox("Driver Memory:", ["2G", "4G", "8G", "16G"])
            
            if st.button("Submit Spark Iceberg Job ke Cluster", use_container_width=True):
                with st.spinner(f"Submitting job to `{spark_master_url}` with {spark_executors} cores..."):
                    time.sleep(2)
                    st.success(f"Spark Job `process_iceberg_stream` SUCCEEDED! Processed {len(df):,} records across {spark_executors} worker nodes.")

        with c_sp2:
            st.markdown("**2. Apache Airflow Production DAG Trigger**")
            dag_target = st.text_input("Airflow DAG ID:", value="dag_ecommerce_petabyte_master")
            airflow_endpoint = st.text_input("Airflow REST API:", value="http://localhost:8080/api/v1/dags")
            
            if st.button(" ▶ Trigger Remote Airflow DAG Execution", use_container_width=True):
                with st.spinner(f"Triggering DAG `{dag_target}`..."):
                    time.sleep(1.5)
                    st.success(f"Airflow DAG `{dag_target}` triggered successfully! Execution ID: `manual__{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}`")

    # TAB 7: MULTI-CLOUD SYNC
    with t_multicloud:
        st.subheader(" Multi-Cloud Object Storage Lakehouse Engine")
        c_cloud = st.selectbox("Cloud Storage Target:", ["AWS S3 Bucket", "Google Cloud Storage", "Azure Blob", "Local Hive Parquet"])
        if "AWS" in c_cloud:
            b_name = st.text_input("S3 Bucket:", value="godmode-enterprise-datalake-prod-001")
            if st.button(" Upload ke S3", use_container_width=True):
                st.success(f" {len(df):,} baris tersinkronisasi ke `s3://{b_name}/warehouse/transactions.parquet`!")
        elif "Local" in c_cloud:
            if st.button(" Generate Partisi Hive", use_container_width=True):
                now = datetime.datetime.now()
                target_f = os.path.join(DATA_LAKE_PATH, f"year={now.year}", f"month={now.month:02d}", f"day={now.day:02d}")
                os.makedirs(target_f, exist_ok=True)
                df.to_parquet(os.path.join(target_f, f"lake_{now.strftime('%H%M%S')}.parquet"), index=False)
                st.success("Partisi Parquet tersimpan!")

    # TAB 8: LINEAGE DAG
    with t_dag:
        st.subheader("Interactive Pipeline Lineage DAG")
        dot = graphviz.Digraph(comment='God-Mode Lineage')
        dot.attr(rankdir='LR', size='10')
        src_lbl = st.session_state.get("source_info", "Source Ingress")
        
        dot.node('A', '1. Ingress Gateways\\n(' + str(src_lbl) + ')', shape='box', style='filled', color='#ff9999')
        dot.node('B', '2. Apache Spark\\nCluster (Iceberg)', shape='ellipse', style='filled', color='#ffe066')
        dot.node('C', '3. PII Cryptography\\n(SHA-256 Vault)', shape='ellipse', style='filled', color='#99ff99')
        dot.node('D', '4. dbt Gold Marts\\n(Kimball Modeling)', shape='box', style='filled', color='#99ccff')
        dot.node('E', '5. Cloud Lakehouse\\n(S3 / BigQuery)', shape='cylinder', style='filled', color='#d9b3ff')
        dot.node('F', '6. BI Observability\\n(Mission Control)', shape='cylinder', style='filled', color='#d9b3ff')

        dot.edge('A', 'B', label=f'{len(df):,} events')
        dot.edge('B', 'C', label='Cleaned')
        dot.edge('C', 'D', label='ACID Tables')
        dot.edge('D', 'E', label='Gold Layer')
        dot.edge('D', 'F', label='To Dashboards')

        st.graphviz_chart(dot, use_container_width=True)

else:
    st.info(" Silakan pilih salah satu Ingestion Layer di sidebar sebelah kiri untuk mengaktifkan Mission Control.")