# Hospital Data Pipeline Project

## Objective
This project aims to build an end-to-end data pipeline for hospital service analytics by implementing modern data engineering tools. The pipeline will process both streaming and batch data, enabling actionable insights into:

- Patient visits,
- Doctor performance,
- Medication usage, and
- Billing information.

  
---
## Problem Statement
Hospitals generate vast amounts of operational data, but this data often remains siloed, making it difficult to:

- Gain real-time insights into hospital operations,
- Analyze doctor performance and resource utilization,
- Monitor medication usage patterns, or
- Generate accurate financial reports.

Our solution integrates this dispersed data into a unified analytics platform with near real-time processing capabilities.

**Schema Tables & Entity Relationship Diagram (ERD)**:

![image](https://github.com/user-attachments/assets/9c82b2f7-37a2-496a-b773-4e9d01d565bc)

[https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/images/Hospital_Schema_ERD.png](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/images/Hospital_Schema_ERD.png)


---
## Data Pipeline Architecture
**Hospital Data Pipeline**

![image](https://github.com/user-attachments/assets/19b2fff4-5be6-4668-8bb7-a261461da097)

### Input
- Postgres table creation and data initialization (dimension and fact tables) 
- Producer streaming data (continue running to redpanda topics)

### Output
- Postgres tables (doctors, patients, medicines, visits, prescriptions, billing_payments)
- GCS json files
- BigQuery tables
- dbt BigQuery tables (data mart)
- Dashboard (Visualization)

### Process
**1. Data Generation & Collection**
- Producing data into a Redpanda topic
- A Python script generates synthetic hospital data
- PostgreSQL serves as the operational database
- Redpanda (Kafka-compatible) is used for streaming data

**2. Stream Processing**
- Apache Flink for real-time data processing
- Debezium for Change Data Capture (CDC) from PostgreSQL

**3. Cloud Storage & Warehousing**
- Google Cloud Storage (GCS) as data lake
- BigQuery as data warehouse with external tables

**4. Transformation & Modeling**
- dbt for transforming raw data into analytical models
- Structured in staging, intermediate, and mart layers

**5. Orchestration & Visualization**
- Kestra for workflow orchestration
- Looker for dashboards and business intelligence


---
## Technologies

| Component         | Technology        | Purpose                       |
|-------------------|-------------------|-------------------------------|
| Containerization  | Docker            | Environment consistency       |
| Infrastructure    | Terraform         | GCP resource provisioning     |
| Database          | PostgreSQL        | Operational data storage      |
| Streaming         | Redpanda          | Message brokering             |
| Processing        | Apache Flink      | Stream processing             |
| CDC               | Debezium          | Database change capture       |
| Storage           | GCS               | Data lake storage             |
| Warehouse         | BigQuery          | Analytical storage            |
| Transformation    | dbt               | Data modeling & analytics     |
| Orchestration     | Kestra            | Pipeline scheduling           |
| Visualization     | Looker            | Dashboards and analytics      |
| Batch Processing  | PySpark (optional)| Large-scale data processing   |


---
## Docker Containers Port

| Container_Name            | Localhost_Port | Container_Port  |
|---------------------------|----------------|-----------------|
| project_redpanda          | 9092           | 9092, 29092     |
| project_debezium          | 8083           | 8083            |
| project_flink_taskmanager |                | 8081            |
| project_flink_jobmanager  | 8081           | 8081            |
| project_postgres          | 5433           | 5432            |
| project_dbt_runner        | 8087           | 8080            |
| kestra-kestra-1           | 8080, 8084     | 8080, 8081      |
| kestra-metadata-1         | 5432           | 5432            |
| kestra-pgadmin-1          | 8085           | 80              |


---
## How to Run the Project

**Prerequisites**
- Docker and Docker Compose installed
- Google Cloud account with GCS and BigQuery access with minimal the following roles:
    - BigQuery Admin
    - BigQuery Data Viewer
    - Storage Admin
- Json credentials file (rename to gcs.json) and save on your $HOME directory
- Terraform installed (for GCP setup)
- Kestra installed
- Install Docker CLI (docker.io) from Ubuntu repositories on Kestra Container
    ```
    apt-get update && apt-get install -y docker.io
    ```
- pgadmin

**Setup Instructions**

**1. Clone the repository**

```
git clone https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project.git
cd Hospital-Data-Pipeline-Project
```

**2. Build and start containers**

```
docker compose up -d --build
```

**3. Setup network connection for kestra and pgadmin**

Check Kestra related containers
```
$ docker ps -a |grep kestra
a92090a93684   kestra/kestra:latest   "docker-entrypoint.s…"   3 days ago       Exited (137) 3 days ago    kestra-kestra-1
aa12c352d71e   postgres               "docker-entrypoint.s…"   3 days ago       Exited (0) 3 days ago      kestra-metadata-1     
57a9f773dd7a   dpage/pgadmin4         "/entrypoint.sh"         7 days ago       Exited (0) 3 days ago      kestra-pgadmin-1
4d875986fef1   postgres               "docker-entrypoint.s…"   7 days ago       Exited (0) 7 days ago      kestra-postgres_zoomcamp-1
```

**kestra-metadata-1** --> Kestra metadata container

**kestra-kestra-1**   --> Kestra container

**kestra-pgadmin-1**  --> Pgadmin container

Customize with your kestra and pgadmin container name.

```
docker start kestra-metadata-1 
docker start kestra-kestra-1
docker start kestra-pgadmin-1
docker network connect hospital-data-pipeline-project_project_net kestra-metadata-1
docker network connect hospital-data-pipeline-project_project_net kestra-kestra-1
docker network connect hospital-data-pipeline-project_project_net kestra-pgadmin-1
docker restart kestra-metadata-1 
docker restart kestra-kestra-1
docker restart kestra-pgadmin-1
```

**4. Initialize infrastructure**

Ensure terraform has been installed.

Edit terraform/main.tf file:

```
provider "google" {
  project = "your project"
  region  = "your region"
}

resource "google_storage_bucket" "hospital_bucket" {
  name     = "hospital_datalake"
  location = "your region"
}

resource "google_bigquery_dataset" "hospital_dataset" {
  dataset_id = "hospital"
}
```

- Entry your ProjectID and Region
- Bucket name: hospital_datalake
- Dataset: hospital
  
```
cd terraform/
terraform init
terraform plan
terraform apply
```

**5. Edit ./dbt/profiles.yml**

```
hospital:
  outputs:
    dev:
      dataset: hospital
      job_execution_timeout_seconds: 300
      job_retries: 1
      keyfile: /usr/app/dbt/gcs.json
      location: <region>
      method: service-account
      priority: interactive
      project: <project-id>
      threads: 4
      type: bigquery
  target: dev


hospital_analytics:
  outputs:
    dev:
      dataset: hospital
      job_execution_timeout_seconds: 300
      job_retries: 1
      keyfile: /usr/app/dbt/gcs.json
      location: <region>
      method: service-account
      priority: interactive
      project: <project-id>
      threads: 4
      type: bigquery
  target: dev
```
Entry project-id and region name.

**6. Change wal_level parameter from replica to logical in postgresql.conf file**

This modification enables logical decoding for transaction logs.

Copy ./src/postgresql.conf to project_postgres:/var/lib/postgresql/data/

```
docker cp ./src/postgresql.conf project_postgres:/var/lib/postgresql/data/postgresql.conf 
docker restart project_postgres
```

**7. Create Postgres tables**

```
docker exec -it project_postgres psql -U postgres -d hospital -f /opt/src/create_tables.sql
```

**8. Setup Debezium**
```
# Setup connector for postgres schema tables:
docker exec -it project_debezium bash -c "/opt/src/curl_postgres_connector.sh"

# Check connection:
curl -X GET http://localhost:8083/connectors

# Check connection status:
curl -X GET http://localhost:8083/connectors/postgres-source/status
```

**9. Generate sample data for dimension and fact tables**

```
# via local server
pip install faker
python ./src/generate_data_postgres.py
```

**10. Check Redpanda Topics**
```
docker exec -it project_redpanda bash
```

```
rpk topic list
```
```
NAME                                     PARTITIONS  REPLICAS
connect_configs                          1           1
connect_offsets                          25          1
connect_statuses                         5           1
postgres-source.public.billing_payments  1           1
postgres-source.public.doctors           1           1
postgres-source.public.medicines         1           1
postgres-source.public.patients          1           1
postgres-source.public.prescriptions     1           1
postgres-source.public.visits            1           1
```
```
rpk topic consume postgres-source.public.visits
```
Ctrl+C

**11. Import flow files from repository to Kestra**
```
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/01_dim_doctors.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/02_dim_patients.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/03_dim_medicines.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/04_dim_gcs_to_bigquery.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/05_streaming_producer.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/06_flink_topic_to_postgres.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/07_redpanda_debezium_to_gcs.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/08_fact_gcs_to_bigquery.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/09_dbt_run.yaml
```
Namespace: project

<img width="328" alt="image" src="https://github.com/user-attachments/assets/f31a331e-d4d0-46ec-bb4f-df9a05d53b8e" />

**13. Start streaming pipeline via Kestra GUI**

Access Kestra UI at [http://localhost:8080](http://localhost:8080) and execute the following workflows sequentially:

**Dimension Tables**

- **01_dim_doctors**
  - This is for sending doctors json topic file to GCS

- **02_dim_patients**
  - This is for sending patients json topic file to GCS
  
- **03_dim_medicines**
  - This is for sending medicines json topic file to GCS

- **04_dim_gcs_to_bigquery**
  - This is for uploading dimension tables from GCS to BigQuery
  

**Fact Tables**

- **05_streaming_producer**
  This is for start streaming data to Redpanda topic

- **06_flink_topic_to_postgres**
  - This is for uploading topic data to PostgreSQL. Debezium will automatically sending data changes to Redpanda topic,

- **07_redpanda_debezium_to_gcs**
  - This is for sending json topic files to GCS

- **08_fact_gcs_to_bigquery**
  - This is for uploading fact tables from GCS to BigQuery


**dbt**

- **09_dbt_run**
  - This is for debugging, running, generating, and serving documentation for dbt (data build tool) to create a data mart for analytics.

Monitor topic using rpk commamd
- rpk --help
- rpk topic list
- rpk topic consume
- etc.
  
Monitor data transfer from topic to postgres using Apache Flink Dashboad.

[http://localhost:8081](http://localhost:8081)

![image](https://github.com/user-attachments/assets/e1274c6d-18ac-402a-b121-210455cf4d81)

Monitor executions of flows pipeline on Kestra UI: [http://localhost:8080](http://localhost:8080)

![image](https://github.com/user-attachments/assets/5d097cfc-e159-4861-a61e-6b6ac69ec1e5)


**dbt**
- url: [http://localhost:8087](http://localhost:8087)

  ![image](https://github.com/user-attachments/assets/6eeb8f45-b458-4620-9686-b6c9fe50cf85)

  ![image](https://github.com/user-attachments/assets/7a8d326a-b69d-4cc0-99d4-83681832482c)

**PySpark**

-  Extract data from Postgres and upload to GCS in json format files [here](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/src/pipeline/pyspark_extract_upload_gcs.py)
-  [Sample visualization script and reports](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/src/pipeline/hospital_visualization_reports.ipynb)
   
**NOTES**

Shell scripts:
- Stopping all dockers: ./src/stop-dockers
- Starting all dockers: ./src/start-dockers


---
## Dashboard

The Looker dashboard provides several key views:

[https://lookerstudio.google.com/reporting/22cfa44a-2e7a-4342-83c5-1bad02cd9c45](https://lookerstudio.google.com/reporting/22cfa44a-2e7a-4342-83c5-1bad02cd9c45)

distribution-of-diagnosis-type (1)

![image](https://github.com/user-attachments/assets/b53dd91c-98c2-4219-b3c7-a34dde7a27ca)

distribution-of-diagnosis-type (2)

![image](https://github.com/user-attachments/assets/ef657d48-f293-4da1-b8bd-3fed4258e320)


[https://lookerstudio.google.com/reporting/cfecb452-76e5-4f87-adf2-17f043b4434b](https://lookerstudio.google.com/reporting/cfecb452-76e5-4f87-adf2-17f043b4434b)

total-revenue-by-month

![image](https://github.com/user-attachments/assets/b57a3576-c9b2-423f-a5e3-1a14b4a7f83e)


[https://lookerstudio.google.com/reporting/fe0b9c34-2c48-42ba-b34b-902cec94b8ed](https://lookerstudio.google.com/reporting/fe0b9c34-2c48-42ba-b34b-902cec94b8ed)


total-revenue-by-doctor

![image](https://github.com/user-attachments/assets/e4dd3f12-54b2-4703-a149-bfd5bfd5ec9f)


---
## Future Improvements

1. Redpanda Optimization
    - Performance Tuning
        - Adjust batch_timeout_ms and batch_size_bytes to balance latency/throughput.
        - Optimize retention policies (e.g., retention.ms for HIPAA compliance).
        - Enable compression (zstd for high throughput, snappy for low latency).    

2. Apache Flink Deep Dive
    - Stream Processing:
        - Upgrade to Flink 1.18+ for features like incremental checkpointing.
        - Use KeyedCoProcessFunction for real-time alerts (e.g., drug interactions).
        - Optimize windowing (e.g., session windows for patient activity tracking).
    - State Management:
        - RocksDBStateBackend with local SSDs for large state workloads.
        - Enable incremental checkpoints and tune checkpointing.interval.
    - Integration:
        - Use Flink’s FileSink for streaming writes to GCS (Parquet/ORC format).
        - Leverage Redpanda’s Kafka-compatible connector for low-latency ingestion.

3. Google Cloud Storage (GCS) for Streaming
    - Cost Optimization:
        - Auto-transition data to Nearline/Coldline via lifecycle policies.
        - Partition data by timestamp (e.g., gs://bucket/patient_data/date=20240401/).
    - Performance & Security:
        - Use Flink’s GCS connector with Hadoop-like output formats.
        - Enable CSEK (Customer-Supplied Encryption Keys) for sensitive data.
   

---
## Acknowledgments

- Redpanda team for developing the Kafka-compatible streaming platform.
- dbt Labs for creating the transformation framework.
- Apache Foundation for providing Flink and Spark.
- Google Cloud for offering a robust data warehousing platform.
- Debezium community for developing the CDC solution.
- Python Software Foundation, which has produced a very efficient programming language.
- SQL, as a powerful language for data manipulation.
- Terraform for enabling GCP resource provisioning.
- DataTalksClub Community, which is truly a great learning platform.

