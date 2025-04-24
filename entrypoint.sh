#!/bin/sh

echo "Starting Redpanda..."
exec redpanda start \
  --smp 1 \
  --reserve-memory 0M \
  --overprovisioned \
  --node-id 1 \
  --kafka-api PLAINTEXT://0.0.0.0:29092,OUTSIDE://0.0.0.0:9092 \
  --advertise-kafka-api PLAINTEXT://project_redpanda:29092,OUTSIDE://localhost:9092 \
  --pandaproxy-addr PLAINTEXT://0.0.0.0:28082,OUTSIDE://0.0.0.0:8082 \
  --advertise-pandaproxy-addr PLAINTEXT://project_redpanda:28082,OUTSIDE://localhost:8082 \
  --rpc-addr 0.0.0.0:33145 \
  --advertise-rpc-addr project_redpanda:33145

# Wait for Redpanda to start
sleep 10

# Create Kafka topics
exec /usr/bin/rpk topic create _kafka_connect_offsets \
  --partitions 25 \
  --replicas 1 \
  --config cleanup.policy=compact

exec /usr/bin/rpk topic create _kafka_connect_statuses \
  --partitions 25 \
  --replicas 1 \
  --config cleanup.policy=compact

exec /usr/bin/rpk topic create _kafka_connect_configs \
  --partitions 1 \
  --replicas 1 \
  --config cleanup.policy=compact

# Keep container running
wait

