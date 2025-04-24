#!/bin/bash

echo "Waiting for Kafka Connect to be ready..."
#sleep 20 

curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d '{
  "name": "postgres-source",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "project_postgres",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "postgres",
    "database.dbname": "hospital",
    "database.server.name": "postgres-source",
    "slot.name": "debezium_slot",
    "plugin.name": "pgoutput",
    "table.include.list": "public.*",
    "topic.prefix": "postgres-source",
    "database.history.kafka.bootstrap.servers": "project_redpanda:29092",
    "database.history.kafka.topic": "schema-changes",
    "time.precision.mode": "connect",
    "temporal.processing.mode": "string",
    "transforms": "unwrap,castDate,castDecimal",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.castDate.type": "org.apache.kafka.connect.transforms.Cast$Value",
    "transforms.castDate.spec": "visit_date:string,billing_date:string",
    "transforms.castDecimal.type": "org.apache.kafka.connect.transforms.Cast$Value",
    "transforms.castDecimal.spec": "total_amount:float64,total_cost:float64"
  }
}'
