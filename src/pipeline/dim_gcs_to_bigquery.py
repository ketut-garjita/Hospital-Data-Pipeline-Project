from google.cloud import bigquery, storage
import json
import tempfile
import os
from datetime import datetime, timedelta
import base64

def convert_date(days):
    """Convert days since epoch to YYYY-MM-DD"""
    return (datetime(1970,1,1) + timedelta(days=int(days))).strftime('%Y-%m-%d')

def decode_price(encoded):
    """Decode base64 encoded price"""
    try:
        return float(base64.b64decode(encoded).decode('utf-8'))
    except:
        return 0.0

def load_data_to_bigquery():
    client = bigquery.Client()
    storage_client = storage.Client()
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
        bucket_name = "hospital_datalake"
        prefix = f"topics/postgres-source.public.{table_name}/"
        
        bucket = storage_client.get_bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix=prefix))
        
        if not blobs:
            print(f"No files found for {table_name}")
            continue

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            for blob in blobs:
                if blob.name.endswith('.json'):
                    data = json.loads(blob.download_as_text())
                    
                    if isinstance(data, list):
                        for item in data:
                            # Transformasi khusus untuk tiap tabel
                            if table_name == "patients":
                                item['value']['date_of_birth'] = convert_date(item['value']['date_of_birth'])
                            elif table_name == "medicines":
                                item['value']['price'] = decode_price(item['value']['price'])
                            
                            temp_file.write(json.dumps(item['value']) + '\n')
                    else:
                        if table_name == "patients":
                            data['value']['date_of_birth'] = convert_date(data['value']['date_of_birth'])
                        elif table_name == "medicines":
                            data['value']['price'] = decode_price(data['value']['price'])
                        
                        temp_file.write(json.dumps(data['value']) + '\n')
            
            temp_path = temp_file.name

        # Verifikasi data
        with open(temp_path, 'r') as f:
            first_line = f.readline()
            print(f"First line of transformed {table_name}: {first_line}")
            f.seek(0)
            line_count = sum(1 for _ in f)
            print(f"Total lines: {line_count}")

        # Load ke BigQuery
        table_ref = client.dataset(dataset_id).table(table_name)
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            schema=schema,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )

        print(f"Uploading {table_name}...")
        
        with open(temp_path, 'rb') as source_file:
            job = client.load_table_from_file(
                source_file,
                table_ref,
                job_config=job_config
            )
            
            try:
                result = job.result()
                print(f"✅ Uploaded {result.output_rows} rows to {table_name}")
            except Exception as e:
                print(f"❌ Error loading {table_name}: {str(e)}")
                if job.errors:
                    print("Job errors:", job.errors)
        
        os.unlink(temp_path)

if __name__ == "__main__":
    load_data_to_bigquery()
    print("🎉 All tables processed!")
