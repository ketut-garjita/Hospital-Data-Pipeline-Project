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

![image](https://github.com/user-attachments/assets/19b2fff4-5be6-4668-8bb7-a261461da097)

### Input
- Postgres table creation and data initialization (dimension and fact tables) 
- Producer streaming data (continue running to redpanda topics)

### Output
- Postgres tables (doctors, patients, medicines, visits, prescriptions, billing_payments)
- GCS json files
- BigQuery tables (GCS --> hospital's tables)
- dbt BigQuery tables

### Processes
**1. Data Generation & Collection:**
- Producing data into a Redpanda topic
- A Python script generates synthetic hospital data
- PostgreSQL serves as the operational database
- Redpanda (Kafka-compatible) is used for streaming data

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
## Docker Containers Port

| Container_Name            | Localhost_Port | Container_Port  |
|---------------------------|----------------|-----------------|
| project_redpanda          | 9092           | 9092, 29092     |
| project_flink_taskmanager |                | 8081            |
| project_flink_jobmanager  | 8081           | 8081            |
| project_debezium          | 8083           | 8083            |
| project_postgres          | 5433           | 5432            |
| project_dbt_runner        | 8087           | 8080            |
| kestra-kestra-1           | 8080, 8084     | 8080, 8081      |
| kestra-metadata           | 5432           | 5432            |
| kestra-pgadmin-1          | 8085           | 80              |


---
## How to Run the Project

**Prerequisites**
- Docker and Docker Compose installed
- Google Cloud account with GCS and BigQuery access with minimal the following roles:
    - BigQuery Admin
    - BigQuery Data Viewer
    - Storage Admin
- Json credentials file (rename to gcs.json)
- Terraform installed (for GCP setup)
- Kestra installed. You can install using Dockerfile.kestra and docker-compose.kestra.yaml files inside this repository
- pgadmin

**Setup Instructions**

**1. Clone the repository:**

```
git clone https://github.com/ketut-garjita/Hospital-Data-Pipeline-Project.git
cd Hospital-Data-Pipeline-Project
```

**2. GCP Credentilas File, Bucket and Dataset**
- Put gsc.json file in ./dbt/gcs.json and ./src/pipeline/gcs.json
- Bucket name: hospital_datalake
- Dataset: hospital

**3. Build and start containers:**

```
docker compose up -d --build
```

**4. Setup network connection for kestra and pgadmin**

Kestra metadata container: kestra-metadata

Kestra container: kestra

Pgadmin container: pgadmin

Customize with your kestra and pgadmin container name.

```
docker start kestra-metadata
docker staet kestra
docker start pgadmin 
docker network connect hospital-data-pipeline-project_project_net kestra-metadata
docker network connect hospital-data-pipeline-project_project_net kestra
docker network connect hospital-data-pipeline-project_project_net pgadmin
docker restart kestra-metadata
docker restart kestra
docker restart pgadmin 
```

**5. Edit /etc/hosts on local server**

Check IP Address of the project_redpanda and project_postgres container server, and take IPv4Address values.
```
docker network list
docker network inspect hospital-data-pipeline-project_project_net
```

Edit the /etc/hosts and add two lines on local server
```
<IPv4Address> project_redpanda
<IPv4Address> project_postgres
```

**6. Initialize infrastructure:**

Note: make sure terraform has been installed

Edit main.tf file, entry ProjectID name.

```
cd terraform/
terraform init
terraform plan
terraform apply
```

**7. Change wal_level = logical in postgresql.conf file**
```
docker exec -it project_postgres bash
```
```
apt update
apt install -y vim
su - postgres
cd data
vi postgresql.conf
==> Search wal_level word and then change parameter wal_level = replica to wal_level = logical
save and exit
```
Restart project_postgres container
```
docker restart project_postgres
```

**8. Initialize database:**

```
docker cp ./src/create_tables.sql project_postgres:/opt
docker exec -it project_postgres psql -U postgres -d hospital -f /opt/create_tables.sql
```

**9. Setup Debezium**
```
docker exec -it project_debezium bash
```

Type (copy & paste) commands below:

```
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
    "table.include.list": "public.*", 
    "topic.prefix": "postgres-source",
    "database.history.kafka.bootstrap.servers": "project_redpanda:29092",
    "database.history.kafka.topic": "schema-changes"
  }
}'
```

Check connection:
```
$ curl -X GET http://localhost:8083/connectors

["postgres-source"][kafka@d63b2692723d ~]
```

Check conenction status:
```
$ curl -X GET http://localhost:8083/connectors

["postgres-source"][kafkcurl -X GET http://localhost:8083/connectors/postgres-source/statustgres-source/status
{"name":"postgres-source","connector":{"state":"RUNNING","worker_id":"172.23.0.3:8083"},"tasks":[{"id":0,"state":"RUNNING","worker_id":"172.23.0.3:8083"}],"type":"source"}[kafka@d63b2692723d ~]$ 
[kafka@d63b2692723d ~]
```

**10. Generate sample data for dimension and fact tables**

```
pip install faker
python ./src/generate_data_postgres.py
```

**11. Check Redpanda Topic**
```
rpk topic list
```
```
redpanda@4350801d7c77:/$ rpk topic list
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


**12. Copy Kestra Flow Files**
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


**13. Install Docker CLI from Ubuntu repositories on Kestra Container**
```
apt-get update && apt-get install -y docker.io
```

**14. Start streaming pipeline via Kestra GUI:**

Access Kestra UI at [http://localhost:8080](http://localhost:8080) and execute the following workflows sequentially:

**Dimension Tables:**

- **dim_doctors**
  _(send doctors json topic file to GCS)_

- **dim_patients**
  _(send patients json topic file to GCS)_
  
- **dim_medicines**
  _(send medicines json topic file to GCS)_

- **dim_gcs_to_bigquery**
  _(upload dimension tables from GCS to BigQuery)_
  

**Fact Tables:**

- **streaming_producer**
  _(start streaming data to Redpanda topic)_

- **flink_topic_to_postgres**
  _(upload topic data to PostgreSQL. Debezium will automatically send data changes to Redpanda topic)_

- **redpanda_debezium_to_gcs**
  _(send json topic files to GCS)_

- **fact_gcs_to_bigquery**
  _(upload fact tables from GCS to BigQuery)_


**dbt:**

- **dbt_run**
  _(run dbt for creating data mart for analytics purpose)_

Monitor topic using rpk commamd
- rpk --help
- rpk topic list
- rpk topic consume
- etc.
  
Monitor data transfer from topic to postgres using Apache Flink Dashboad.

[http://localhost:8081](http://localhost:8081)

![image](https://github.com/user-attachments/assets/e1274c6d-18ac-402a-b121-210455cf4d81)

Monitor executions of flows pipeline on Kestra UI: [http://localhost:8080](http://localhost:8080)

![image](https://github.com/user-attachments/assets/92ea1226-7488-4f7a-9090-d69bd1377afc)

**dbt docs**
- dbt docs generate
- dbt docs serve --port 8080 --host 0.0.0.0
- url: [http://localhost:8087](http://localhost:8087)

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

