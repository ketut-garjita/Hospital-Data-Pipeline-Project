import json
from kafka import KafkaConsumer
from clickhouse_driver import Client 
import clickhouse_connect
from datetime import datetime, timedelta, date
import pandas as pd

# Kafka topics to subscribe
TOPICS = [
    'postgres-source.public.doctors',
    'postgres-source.public.patients',
    'postgres-source.public.medicines',
    'postgres-source.public.visits',
    'postgres-source.public.prescriptions',
    'postgres-source.public.billing_payments'
]

# Mapping Kafka topic to table name
TOPIC_TABLE_MAP = {
    'postgres-source.public.doctors': 'doctors',
    'postgres-source.public.patients': 'patients',
    'postgres-source.public.medicines': 'medicines',
    'postgres-source.public.visits': 'visits',
    'postgres-source.public.prescriptions': 'prescriptions',
    'postgres-source.public.billing_payments': 'billing_payments'
}

topics = TOPIC_TABLE_MAP

def insert_to_clickhouse(table, payload, schema_info=None):
    """
    Improved insert with proper type handling
    Parameters:
    - table: target table name
    - payload: dictionary of {column: value}
    - schema_info: optional schema information for type awareness
    """
    from clickhouse_driver import Client
    client = Client(
        host='clickhouse',
        port=9000,
        user='streaming',
        password='password',
        database='hospital'
    )

    try:
        columns = []
        values = []

        for col, val in payload.items():
            col_type = schema_info.get(col, {}).get('type') if schema_info else None
            columns.append(col)

            if val is None:
                values.append('NULL')
                continue

            # Tangani tipe integer numerik
            if col_type in ['Int32', 'UInt32', 'Int64', 'UInt64']:
                if isinstance(val, int):
                    values.append(str(val))
                else:
                    raise ValueError(f"Expected int for {col}, got {type(val)}: {val}")

            # handle decimal tipe
            elif col_type and col_type.startswith('Decimal'):
                values.append(str(val))  # Decimal tetap ditulis sebagai angka (tanpa kutip)

            # handle epoch date
            elif col_type == 'Date32' or (schema_info is None and 'date' in col.lower()):
                if isinstance(val, int):
                    values.append(f"toDate32({val})")
                else:
                    values.append('NULL')

            # String must be escaped and give double quote
            else:
                escaped = str(val).replace("'", "''")
                values.append(f"'{escaped}'")

        # create and execute query
        query = f"""
        INSERT INTO {table} ({', '.join(columns)})
        VALUES ({', '.join(values)})
        """
        client.execute(query)
        print(f"[ClickHouse] Inserted into {table}: {payload}")

    except Exception as e:
        print(f"[Error] Failed to insert into {table}: {e}")

	

def main():
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers='project_redpanda:29092',
        group_id='olap-clickhouse-consumer',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    for msg in consumer:
        try:
            payload = msg.value.get('payload', {})
            table = msg.topic.split('.')[-1]
            insert_to_clickhouse(table, payload)
            print(f"[ClickHouse] Inserted into {table}: {payload}")
        except Exception as e:
            print(f"[ClickHouse] Error: {e}")

if __name__ == "__main__":
    main()

