from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sha2, current_timestamp, to_date, when

def create_god_spark_session():
    return SparkSession.builder \
        .appName("GodMode_Distributed_Iceberg_Pipeline") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.lakehouse", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.lakehouse.type", "hadoop") \
        .config("spark.sql.catalog.lakehouse.warehouse", "s3a://godmode-enterprise-datalake-prod-001/warehouse") \
        .config("spark.sql.shuffle.partitions", "200") \
        .getOrCreate()

def run_distributed_pipeline():
    spark = create_god_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print(">>> [SPARK CLUSTER] Ingesting & Partitioning Distributed Datasets...")

    # Membaca data mentah (Bronze Layer)
    raw_df = spark.read.format("parquet").load("data_lake/")

    # Transformasi & Governance (Silver Layer)
    # 1. PII Masking dengan SHA-256
    # 2. Data Cleansing & Data Quality Enforcement
    cleaned_df = raw_df.filter(col("total_amount") > 0) \
        .withColumn("customer_name_masked", sha2(col("customer_name"), 256)) \
        .withColumn("ingested_at", current_timestamp()) \
        .withColumn("tx_date", to_date(col("transaction_date"))) \
        .drop("customer_name")

    # Menulis ke Apache Iceberg Table (ACID Compliant + Hidden Partitioning)
    cleaned_df.write \
        .format("iceberg") \
        .mode("append") \
        .partitionBy("tx_date") \
        .save("lakehouse.prod_db.fact_transactions_gold")

    print(">>> [SPARK CLUSTER] Pipeline Berhasil Dieksekusi secara Paralel!")
    spark.stop()

if __name__ == "__main__":
    run_distributed_pipeline()