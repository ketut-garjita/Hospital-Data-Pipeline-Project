from google.cloud import bigquery

client = bigquery.Client()
dataset_id = "hospital"

tables = {
    "doctors": [
        bigquery.SchemaField("doctor_id", "INTEGER"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("specialization", "STRING"),
        bigquery.SchemaField("experience_years", "INTEGER"),
        bigquery.SchemaField("contact_info", "STRING"),
    ],
    "patients": [
        bigquery.SchemaField("patient_id", "INTEGER"),
        bigquery.SchemaField("full_name", "STRING"),
        bigquery.SchemaField("date_of_birth", "DATE"),
        bigquery.SchemaField("gender", "STRING"),
        bigquery.SchemaField("blood_type", "STRING"),
        bigquery.SchemaField("contact_info", "STRING"),
        bigquery.SchemaField("insurance_id", "STRING"),
    ],
    "medicines": [
        bigquery.SchemaField("medicine_id", "INTEGER"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("category", "STRING"),
        bigquery.SchemaField("manufacturer", "STRING"),
        bigquery.SchemaField("price", "FLOAT"),
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

