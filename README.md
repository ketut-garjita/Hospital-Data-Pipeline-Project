# Hospital Data Pipeline Project

## Objective
This project aims to build an end-to-end data pipeline for hospital service analytics, implementing modern data engineering tools to process both batch and streaming data. The solution will provide insights into patient visits, doctor performance, medication usage, and billing information.

---
## Problem Statement
Hospitals generate vast amounts of operational data that often sits in silos. This makes it difficult to:

- Gain real-time insights into hospital operations
- Analyze doctor performance and resource utilization
- Monitor medication usage patterns
- Generate accurate financial reports

Our solution integrates this data into a unified analytics platform with near real-time capabilities.

Schema tables Entity Relationship Diagram (ERD)

[Hospital Tables ERD](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/images/Hospital_ERD.png)

![image](https://github.com/user-attachments/assets/49c00983-2d25-4720-8c9a-ca280970caf1)


---
## Data Pipeline Architecture
**Hospital Data Pipeline**

![image](https://github.com/user-attachments/assets/a35eff73-a35f-4a89-8187-6f3a947a4c42)

**1. Data Generation & Collection:**
- PostgreSQL as the operational database
- Python scripts generating synthetic hospital data
- Redpanda (Kafka-compatible) for streaming data ingestion

**2. Stream Processing:**
- Apache Flink for real-time data processing
- Debezium for Change Data Capture (CDC) from PostgreSQL

**3. Cloud Storage & Warehousing:**
- Google Cloud Storage (GCS) as data lake
- BigQuery as data warehouse with external tables

**4. Transformation & Modeling:**
- dbt for transforming raw data into analytical models
- Structured in staging, intermediate, and mart layers

**5. Orchestration & Visualization:**
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
## How to Run the Project

**Prerequisites**
- Docker and Docker Compose installed
- Google Cloud account with GCS and BigQuery access
- Json credentials file (rename to gcs.json)
- Terraform installed (for GCP setup)
- Kestra installed. You can install using Dockerfile.kestra and docker-compose.kestra.yaml files inside this repository
- pgadmin

**Setup Instructions**

**1. Clone the repository:**

```
git clone https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project.git
cd hospital-data-pipeline
```

**2. GCP Credentilas File, Bucket and Dataset**
- Put gsc.json file in ./dbt/gcs.json and ./src/pipeline/gcs.json
- Bucket name: hospital_datalake
- Dataset: hospital

**3. Setup network connection for kestra and pgadmin**

Kestra container: kestra
Pgadmin container: pgadmin

```
docker network connect hospital_project_net kestra
docker network connect hospital_project_net pgadmin
```

**4. Initialize infrastructure:**

Note: make sure terraform has been installed

```
cd terraform/
terraform init
terraform plan
terraform apply
```

**5. Build and start containers:**

```
docker compose up -d --build
```

**6. Initialize database:**

```
docker cp ./src/create_tables.sql project_postgres:/opt
docker exec -it project_postgres psql -U postgres -d hospital -f /opt/create_tables.sql
```

**7. Generate sample data:**

```
python ./src/generate_data_postgres.py
```

**8. Install dbt-biquery on dbt**
```
docker exec -it project_dbt_runner bash -c "pip install dbt-bigquery"
```

**9. Setup Debezium**
```
docker exec -it project_debezium bash

curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
  "name": "postgres-source",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "project_postgres",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "postgres",
    "database.dbname": "hospital",
    "database.server.name": "postgres_source",
    "slot.name": "debezium_slot",
    "plugin.name": "pgoutput",
    "table.include.list": "public.visits,public.billing_payments,public.prescriptions", 
    "topic.prefix": "postgres-source",
    "database.history.kafka.bootstrap.servers": "project_redpanda:29092",
    "database.history.kafka.topic": "schema-changes"
  }
}'
```

**10. Check Redpanda Topic**
```
rpk topic list
```

**11. Copy Kestra Flow Files**
```
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@src/flows/dbt_run.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@src/flows/dim_doctors.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@src/flows/dim_patients.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@src/flows/dim_medicines.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@src/flows/dim_gcs_to_bigquery.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@src/flows/fact_gcs_to_bigquery.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@src/flows/flink_topic_to_postgres.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@src/flows/redpanda_debezium_to_gcs.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@src/flows/streaming_producer.yaml
```
Kestra Namespace: **project**


**12. Start streaming pipeline via Kestra GUI:**

Access Kestra UI at [http://localhost:8080](http://localhost:8080) and execute the following workflows sequentially:
- dim_doctors (send json topic files to gs://{GCS_BUCKET}/debezium/doctors}
- dim_patients (send json topic files to gs://{GCS_BUCKET}/debezium/patients}
- dim_medicines (send json topic files to gs://{GCS_BUCKET}/debezium/medicines}
- dim_gcs_to_bigquery (upload dimension tables from GCS to BigQuery)
- streaming_producer (start streaming data to Redpanda topic)
- flink_topic_to_postgres (upload topic data to PostgreSQL. Debezium will automatically send data changes to Redpanda topic)
- redpanda_debezium_to_gcs (send json topic files to GCS)
- fact_gcs_to_bigquery (upload fact tables from GCS to BigQuery)
- dbt_run (run dbt for creating data mart for analytics purpose)

Monitor topic using rpk commamd
- rpk --help
- rpk topic list
- rpk topic consume
- etc.
  
![image](https://github.com/user-attachments/assets/a89b3cd2-7c62-4272-9cd6-b3581cfa2c32)

Monitor data transfer from topic to postgres using Apache Flink Dashboad.

[http://localhost:8081](http://localhost:8081)

![image](https://github.com/user-attachments/assets/e1274c6d-18ac-402a-b121-210455cf4d81)

Monitor executions of flows pipeline on Kestra UI: [http://localhost:8080](http://localhost:8080)

<img width="1067" alt="image" src="https://github.com/user-attachments/assets/cc3abd2e-d741-4dd7-810f-7da451ed6df9" />


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

1. Real-time Alerting:
- Implement anomaly detection for unusual patient volumes
- Medication interaction warnings

2. Enhanced Data Quality:
- Add Great Expectations for data validation
- Implement data reconciliation checks

3. Advanced Analytics:
- Predictive models for patient admission rates
- Resource optimization suggestions

4. Leverage Apache Flink more effectively for streaming data processing, particularly in cloud environments.
   

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

