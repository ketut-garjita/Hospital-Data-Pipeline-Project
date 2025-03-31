from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os

POSTGRES_URL = "jdbc:postgresql://project_postgres:5432/hospital"
POSTGRES_PROPERTIES = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

GCS_BUCKET = "hospital_datalake"
TABLES = ["doctors", "patients", "medicines", "visits", "billing_payments", "prescriptions"]

spark = SparkSession.builder \
    .appName("PostgresToGCS") \
    .config("spark.jars", "/home/dataeng/jars/postgresql-42.7.1.jar,/home/dataeng/jars/gcs-connector-hadoop3-latest.jar") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
    .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/home/dataeng/projects/dez-2025/hospital/gcs.json") \
    .getOrCreate()

print(spark.conf.get("spark.hadoop.fs.gs.impl")) 
print(spark.conf.get("spark.hadoop.google.cloud.auth.service.account.json.keyfile")) 

for table in TABLES:
    print(f"Processing table: {table}")

    df = spark.read.jdbc(url=POSTGRES_URL, table=table, properties=POSTGRES_PROPERTIES)

    gcs_path = f"gs://{GCS_BUCKET}/postgres/{table}/"

    df.write.mode("overwrite").json(gcs_path)
    
    print(f"Uploaded {table} to {gcs_path}")

spark.stop()

