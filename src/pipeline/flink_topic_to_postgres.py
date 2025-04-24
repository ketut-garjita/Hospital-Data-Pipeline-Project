from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)  
table_env = StreamTableEnvironment.create(env)

table_env.execute_sql("""
    CREATE TABLE visits_kafka (
        visit_id INT,
        patient_id INT,
        doctor_id INT,
        visit_date TIMESTAMP(3),
        diagnosis STRING,
        total_cost DECIMAL(10,2),
        WATERMARK FOR visit_date AS visit_date - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'topic_visits',
        'properties.bootstrap.servers' = 'project_redpanda:29092',
        'format' = 'json',
        'scan.startup.mode' = 'earliest-offset'
    )
""")

# Define Kafka Source Table for BILLING
table_env.execute_sql("""
    CREATE TABLE billing_kafka (
        billing_id INT,
        patient_id INT,
        visit_id INT,
        billing_date TIMESTAMP(3),
        total_amount DECIMAL(10,2),
        payment_status STRING,
        WATERMARK FOR billing_date AS billing_date - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'topic_billing',
        'properties.bootstrap.servers' = 'project_redpanda:29092',
        'format' = 'json',
        'scan.startup.mode' = 'earliest-offset'
    )
""")

# Define Kafka Source Table for PRESCRIPTIONS
table_env.execute_sql("""
    CREATE TABLE prescriptions_kafka (
        prescription_id INT,
        patient_id INT,
        doctor_id INT,
        medicine_id INT,
        dosage STRING,
        duration STRING
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'topic_prescriptions',
        'properties.bootstrap.servers' = 'project_redpanda:29092',
        'format' = 'json',
        'scan.startup.mode' = 'earliest-offset'
    )
""")

# Define PostgreSQL Sink Table for VISITS
table_env.execute_sql("""
    CREATE TABLE visits (
        visit_id INT PRIMARY KEY NOT ENFORCED,
        patient_id INT,
        doctor_id INT,
        visit_date TIMESTAMP(3),
        diagnosis STRING,
        total_cost DECIMAL(10,2)
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://project_postgres:5432/hospital',
        'table-name' = 'visits',
        'username' = 'postgres',
        'password' = 'postgres',
        'driver' = 'org.postgresql.Driver'
    )
""")

# Define PostgreSQL Sink Table for BILLING
table_env.execute_sql("""
    CREATE TABLE billing_payments (
        billing_id INT PRIMARY KEY NOT ENFORCED,
        patient_id INT,
        visit_id INT,
        billing_date TIMESTAMP(3),
        total_amount DECIMAL(10,2),
        payment_status STRING
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://project_postgres:5432/hospital',
        'table-name' = 'billing_payments',
        'username' = 'postgres',
        'password' = 'postgres',
        'driver' = 'org.postgresql.Driver'
    )
""")

# Define PostgreSQL Sink Table for PRESCRIPTIONS
table_env.execute_sql("""
    CREATE TABLE prescriptions (
        prescription_id INT PRIMARY KEY NOT ENFORCED,
        patient_id INT,
        doctor_id INT,
        medicine_id INT,
        dosage STRING,
        duration STRING
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://project_postgres:5432/hospital',
        'table-name' = 'prescriptions',
        'username' = 'postgres',
        'password' = 'postgres',
        'driver' = 'org.postgresql.Driver'
    )
""")

print("tables list: ")
print(table_env.list_tables())

visits_stream = table_env.from_path("visits_kafka")
billing_stream = table_env.from_path("billing_kafka")
prescriptions_stream = table_env.from_path("prescriptions_kafka")

from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema

kafka_props = {'bootstrap.servers': 'project_redpanda:29092', 'group.id': 'flink-group'}
visits_source = FlinkKafkaConsumer("visits_topic", SimpleStringSchema(), kafka_props)
stream = env.add_source(visits_source)

stream.print()


# Insert into PostgreSQL using Flink SQL
table_env.execute_sql("INSERT INTO visits SELECT * FROM visits_kafka")
table_env.execute_sql("INSERT INTO billing_payments SELECT * FROM billing_kafka")
table_env.execute_sql("INSERT INTO prescriptions SELECT * FROM prescriptions_kafka")


# Execute Flink Table API job
# env.execute("Flink Kafka to PostgreSQL Job")
