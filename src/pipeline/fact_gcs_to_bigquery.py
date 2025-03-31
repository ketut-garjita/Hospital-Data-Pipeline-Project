from google.cloud import bigquery

client = bigquery.Client()
dataset_id = "hospital"

tables = {
    "visits": [
        bigquery.SchemaField("visit_id", "INTEGER"),
        bigquery.SchemaField("patient_id", "INTEGER"),
        bigquery.SchemaField("doctor_id", "INTEGER"),
        bigquery.SchemaField("visit_date", "DATE"),
        bigquery.SchemaField("diagnosis", "STRING"),
        bigquery.SchemaField("total_cost", "FLOAT"),
    ],
    "billing_payments": [
        bigquery.SchemaField("billing_id", "INTEGER"),
        bigquery.SchemaField("patient_id", "INTEGER"),
        bigquery.SchemaField("visit_id", "INTEGER"),
        bigquery.SchemaField("billing_date", "DATE"),
        bigquery.SchemaField("total_amount", "FLOAT"),
        bigquery.SchemaField("payment_status", "STRING"),
    ],
    "prescriptions": [
        bigquery.SchemaField("prescription_id", "INTEGER"),
        bigquery.SchemaField("patient_id", "INTEGER"),
        bigquery.SchemaField("doctor_id", "INTEGER"),
        bigquery.SchemaField("medicine_id", "INTEGER"),
        bigquery.SchemaField("dosage", "STRING"),
        bigquery.SchemaField("duration", "STRING"),
    ]
}

for table_name, schema in tables.items():
    uri = f"gs://hospital_datalake/debezium/{table_name}/*.json"
    table_ref = client.dataset(dataset_id).table(table_name)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE  
    )

    print(f"Uploading {table_name} from {uri} to BigQuery...")

    job = client.load_table_from_uri(uri, table_ref, job_config=job_config)
    job.result()  

    print(f"✅ Upload {table_name} complete!")

print("🎉 All tables uploaded successfully!")

