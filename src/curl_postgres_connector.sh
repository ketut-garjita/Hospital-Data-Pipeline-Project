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
