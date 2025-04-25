# Streaming Data Pipeline - Hospital Medical Services System (sample case)

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

![image](https://github.com/user-attachments/assets/51777e9e-025c-4550-a48f-695f06dc6285)

[Hospital Data Pipeline](https://github.com/ketut-garjita/streaming-project-1/blob/main/images/project-hospital-data-pipeline.svg)

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
| OLAP Databases    | ClickHouse, DuckDB| On-premise data warehouse     |
| Visualization     | Grafana           | On-premise data visualization |


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
| project_clickhouse        | 8123           | 8123            |
| project_olap_consumer     |                |                 |
| project_grafana           | 3000           | 3000            |
| kestra-kestra-1           | 8080, 8084     | 8080, 8081      |
| kestra-metadata-1         | 5432           | 5432            |
| kestra-pgadmin-1          | 8085           | 80              |


---
## How to Run the Project

**Prerequisites**
- Docker and Docker Compose installed
- Terraform installed
- Google Cloud account with GCS and BigQuery access with minimal the following roles:
    - BigQuery Admin
    - BigQuery Data Viewer
    - Storage Admin
- Json credentials file (rename to gcs.json) and save on your $HOME directory
- Kestra installed
- Install Docker CLI (docker.io) from Ubuntu repositories on Kestra Container
  
    ```
    apt-get update && apt-get install -y docker.io
    ```
- pgAdmin, DBeaver
   
---
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

Network name of project docker containers is **hospital-data-pipeline-project_project_net**.
All containers should connect to the same network.

Check Kestra related containers
```
$ docker ps -a |grep kestra
a92090a93684   kestra/kestra:latest   "docker-entrypoint.s…"   3 days ago       Exited (137) 3 days ago    kestra-kestra-1
aa12c352d71e   postgres               "docker-entrypoint.s…"   3 days ago       Exited (0) 3 days ago      kestra-metadata-1     
57a9f773dd7a   dpage/pgadmin4         "/entrypoint.sh"         7 days ago       Exited (0) 3 days ago      kestra-pgadmin-1
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
Entry your project-id and region name.


**6. Setup Debezium Connector**

A Debezium connector is a tool that captures changes in a database and streams them in real time. It's part of the Debezium platform, which is an open-source distributed platform for Change Data Capture (CDC).

Debezium connectors connect to a source database (like MySQL, PostgreSQL, MongoDB, Oracle, SQL Server, etc.).

They monitor the database’s transaction log to detect inserts, updates, and deletes.

These changes are then published to the Kafka topic (or other message broker like Redpanda), allowing other systems to consume the real-time changes.

```
# Setup connector for postgres schema tables:
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @./connectors/postgres-source.json
curl -X POST http://localhost:8183/connectors -H "Content-Type: application/json" -d @./connectors/postgres-debezium-gcs.json

# Check connection:
curl -X GET http://localhost:8083/connectors
curl -X GET http://localhost:8183/connectors

# Check connection status:
curl -X GET http://localhost:8083/connectors/postgres-source/status
curl -X GET http://localhost:8183/connectors/postgres-debezium-gcs/status
```


**7. Create Database Tables**

- **PostgreSQL**
  ```
  docker exec -it project_postgres psql -U postgres -d hospital -f /opt/src/create_tables.sql
  ```

- **ClickHouse**
  ```
  docker exec -it project_clickhouse bash -c "clickhouse-client -u streaming --password password -d hospital < /opt/clickhouse/create_tables.sql"
  ```
  
- **DuckDB**
  ```
  docker exec -it project_olap_consumer /root/.duckdb/cli/*/duckdb /app/olap/duckdb/hospital.db < ./olap/duckdb/create_tables.sql
  ```
  
You can use tools like pgAdmin for PostgreSQL and DBeaver for working with various database platforms.


**8. Generate sample data for dimension and fact tables on PostgreSQL**

On local server:

```
pip install faker
```
```
python ./src/generate_data_postgres.py
```

**9. Check Redpanda Topics**
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

exit

**10. Import flow files from repository to Kestra**
```
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/01_streaming_producer.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/02_topic_flink_postgres.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/03_dim_gcs_to_bigquery.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/04_fact_gcs_to_bigquery.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/05_dbt_run.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/06_kafka_consumer_clickhouse.yaml
curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@./src/flows/07_kafka_consumer_duckdb.yaml
```

**11. Review flows list**

Login to Kestra UI at [http://localhost:8080](http://localhost:8080) 

Flows --> Namespace --> filter --> project

![image](https://github.com/user-attachments/assets/e724745b-be35-4370-8e66-90e702442acb)

![image](https://github.com/user-attachments/assets/9a7940b2-d0b6-4fe5-b43a-6267d0a4eb59)


**12. Start streaming pipeline via Kestra GUI**

Access Kestra UI at [http://localhost:8080](http://localhost:8080) and execute the following workflows:

```
01_streaming_producer.yaml
02_topic_flink_postgres.yaml
03_dim_gcs_to_bigquery.yaml
04_fact_gcs_to_bigquery.yaml
05_dbt_run.yaml
06_kafka_consumer_clickhouse.yaml
07_kafka_consumer_duckdb.yaml

Note: 05_dbt_run.yaml can be run last
```

---
**13. Monitoring**

- **Monitor executions of flows pipeline on Kestra UI**

  [http://localhost:8080](http://localhost:8080)

  ![image](https://github.com/user-attachments/assets/857b0acf-5572-4cf7-941d-937cee06a98f)

- **Monitor data transfer from topic to postgres using Apache Flink Dashboard**

  [http://localhost:8081](http://localhost:8081)

  ![image](https://github.com/user-attachments/assets/45c8f478-dee8-4e79-9a75-2fd3ae8238f9)

- **Monitor topics status via AKHQ tool**
  
  [AKHQ](https://akhq.io/) is Kafka GUI for Apache Kafka ® to manage topics, topics data, consumers group, schema registry, connect and more.
  
  [http://localhost:8180/ui/redpanda/topic](http://localhost:8180/ui/redpanda/topic)

  ![image](https://github.com/user-attachments/assets/f4808633-d153-4666-aa96-8e4081054d5d)

- **Google Cloud Storage (GCS)**

  ![image](https://github.com/user-attachments/assets/39144663-0a38-4df7-b236-7e27df4015f9)

- **BiqQuery Datasets**
   
  ![image](https://github.com/user-attachments/assets/14493dfe-c841-4f49-8914-88091aa9433f)

  ![image](https://github.com/user-attachments/assets/15553ba4-ff8f-41d9-8a95-ccd5e905594d)

- **Data build tools (dbt)**
  - Serve dbt document:
    ```
    docker exec -it project_dbt_runner dbt docs serve --port 8080 --host 0.0.0.0
    ```
  - Open: url: [http://localhost:8087](http://localhost:8087)

    ![image](https://github.com/user-attachments/assets/6eeb8f45-b458-4620-9686-b6c9fe50cf85)
  
    ![image](https://github.com/user-attachments/assets/7a8d326a-b69d-4cc0-99d4-83681832482c)


---
## Dashboard

- **GCP Looker**
  The Looker dashboard provides several key views:

[https://lookerstudio.google.com/reporting/22cfa44a-2e7a-4342-83c5-1bad02cd9c45](https://lookerstudio.google.com/reporting/22cfa44a-2e7a-4342-83c5-1bad02cd9c45)

**distribution-of-diagnosis-type (1)**

![image](https://github.com/user-attachments/assets/b53dd91c-98c2-4219-b3c7-a34dde7a27ca)

**distribution-of-diagnosis-type (2)**

![image](https://github.com/user-attachments/assets/ef657d48-f293-4da1-b8bd-3fed4258e320)


[https://lookerstudio.google.com/reporting/cfecb452-76e5-4f87-adf2-17f043b4434b](https://lookerstudio.google.com/reporting/cfecb452-76e5-4f87-adf2-17f043b4434b)

**total-revenue-by-month**

![image](https://github.com/user-attachments/assets/b57a3576-c9b2-423f-a5e3-1a14b4a7f83e)


[https://lookerstudio.google.com/reporting/fe0b9c34-2c48-42ba-b34b-902cec94b8ed](https://lookerstudio.google.com/reporting/fe0b9c34-2c48-42ba-b34b-902cec94b8ed)


**total-revenue-by-doctor**

![image](https://github.com/user-attachments/assets/e4dd3f12-54b2-4703-a149-bfd5bfd5ec9f)

- **Grafana**
- Create Materialized Views
  ```
  docker exec -it project_clickhouse bash -c "clickhouse-client -u streaming --password password -d hospital < /opt/clickhouse/create_MV.sql"
  ```
  <img width="353" alt="image" src="https://github.com/user-attachments/assets/2c3f4058-783e-4060-af17-cfcbba636249" />

- Open URL: [http://localhost:3000](http://localhost:3000)
  
  <img width="323" alt="image" src="https://github.com/user-attachments/assets/570988a0-1213-45b8-ae9f-08257c954fcf" />

- Connection --> Add new connection --> Data source --> ClickHouse --> Install

- Add new data source:
  - Server addres: project_clickhouse
  - Server port: 8123
  - Protocol: HTTP
  - Username: streaming
  - Password: password
    Save & test
    
-  building a dashboard --> + Add Visualization --> Select data source (grafana-clickhouse-datasource (default)) --> SQL Editor:
   
   ```
   -- Top Diagnoses
    SELECT
        diagnosis,
        sum(diagnosis_count) AS total
    FROM hospital.mv_top_diagnosis
    GROUP BY diagnosis
    ORDER BY total DESC
    LIMIT 10
   ```
   ```
   -- Most Prescribed Medicines
    SELECT
        m.name AS medicine,
        p.total_prescribed
    FROM hospital.mv_prescription_stats p
    JOIN hospital.medicines m ON p.medicine_id = m.medicine_id
    ORDER BY total_prescribed DESC
    LIMIT 10
   ```
   
- Sample visualization

  <img width="452" alt="image" src="https://github.com/user-attachments/assets/9a505a15-a063-4b6e-b170-9f666cc7bc61" />

  <img width="452" alt="image" src="https://github.com/user-attachments/assets/8948fd35-c2db-4ac2-bfbd-9ef75272ed17" />


---
## PySpark Batch Processing (optional)

Notes:
- In a production environment, this batch processing option should not be run during peak hours of OLTP database operations because it will affect the operational performance of the OLTP database. The reason is that this batch processing will directly access the operational database.
- Ideally, the database for analytical purposes (OLAP) should be separated from the operational or transaction database (OLTP).
  
- Pre-requisites:
  - Apache Spark installed on local server
  - Anaconda or Jupyter Notebook installed 
  - Downnload jars
    ```
    sudo mkdir /usr/lib/jars
    cd /usr/lib//jars
    sudo wget  https://jdbc.postgresql.org/download/postgresql-42.7.1.jar
    sudo wget https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar
    ```
- Extract data from Postgres and upload to GCS in json format file

  Execute [pyspark_extract_upload_gcs.py](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/src/pipeline/pyspark_extract_upload_gcs.py)

  ```
  python ./src/pipeline/pyspark_extract_upload_gcs.py
  ```
  
- PySpark GCS files

  ![image](https://github.com/user-attachments/assets/3b0496aa-a4dc-463f-8c31-d613f85c207d)

- Execute jupyter notebook code for creating sample visualization

  Input datasets: [pyspark GCS files](https://github.com/user-attachments/assets/3b0496aa-a4dc-463f-8c31-d613f85c207d)
  
  Run [hospital_visualization_reports.ipynb](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/src/pipeline/hospital_visualization_reports.ipynb) code through Jupyter Notebook
  
  ```
  jupyter-notebook
  Click :  http://localhost:8888/tree?token=xxxxxxx

  Open and Run hospital_visualization_reports.ipynb
  ```
- Visualization Reports
  - [Top 10 Doctors by Number of Visits](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/images/pyspark_doctor_performance.png)
  - [Monthly Revenue](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/images/pyspark_monthly_revenue.png)
  - [Patient Age Distribution](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/images/pyspark_patient_age_distribution.png)
  - [Payment Status Distribution](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/images/pyspark_payment_status.png)
  - [Prescription Medicine Analysis](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/images/pyspark_top_medicines.png)
  - [Doctor Specialization Distribution](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/images/pyspark_doctor_specializations.png)
  - [Visit Diagnosis Word Cloud](https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project/blob/main/images/pyspark_diagnosis_wordcloud.png)


## Scripts to Stop and Start the Docker Services for the Project
  - Stopping services: ./src/stop-dockers
  - Starting services: ./src/start-dockers
    
These scripts do not include stop and start of Kestra services.


---
## Future Improvements

1. Apply to various real-world tables used by hospitals in their operations. The data tables include both dimension and fact tables, which can be generated through either batch or streaming processes.
   - Appointments
   - Medical Records
   - Insurance
   - Laboratory Tests
   - Hospital Rooms & Beds
   - Emergency Cases 
   - Staff
   
2. Redpanda Optimization
    - Performance Tuning
        - Adjust batch_timeout_ms and batch_size_bytes to balance latency/throughput.
        - Optimize retention policies (e.g., retention.ms for HIPAA compliance).
        - Enable compression (zstd for high throughput, snappy for low latency).    

3. Apache Flink Deep Dive
    - Stream Processing:
        - Use KeyedCoProcessFunction for real-time alerts (e.g., drug interactions).
        - Optimize windowing (e.g., session windows for patient activity tracking).
    - State Management:
        - RocksDBStateBackend with local SSDs for large state workloads.
        - Enable incremental checkpoints and tune checkpointing.interval.
    - Integration:
        - Use Flink’s FileSink for streaming writes to GCS (Parquet/ORC format).
        - Leverage Redpanda’s Kafka-compatible connector for low-latency ingestion.

4. Google Cloud Storage (GCS) for Streaming
    - Cost Optimization:
        - Auto-transition data to Nearline/Coldline via lifecycle policies.
        - Partition data by timestamp (e.g., gs://bucket/patient_data/date=20240401/).
    - Performance & Security:
        - Use Flink’s GCS connector with Hadoop-like output formats.
        - Enable CSEK (Customer-Supplied Encryption Keys) for sensitive data.
   

---
## Acknowledgments

- Redpanda — for developing a Kafka-compatible, high-performance streaming platform.
- dbt Labs — for creating a powerful transformation framework that simplifies data modeling.
- The Apache Software Foundation — for contributing essential open-source tools like Flink and Spark.
- Google Cloud Platform (GCP) — for providing a reliable and scalable data warehousing infrastructure.
- Debezium Community — for building an open-source Change Data Capture (CDC) solution.
- Python Software Foundation — for developing Python, a versatile and efficient programming language.
- SQL — as a foundational language for querying and manipulating structured data.
- Terraform — for enabling Infrastructure as Code (IaC) and seamless provisioning of GCP resources.
- ClickHouse, DuckDB, and Grafana — for enabling fast analytics, in-memory processing, and intuitive data visualization.
- DataTalks.Club Community — for fostering a vibrant and collaborative learning environment in data engineering and analytics.

