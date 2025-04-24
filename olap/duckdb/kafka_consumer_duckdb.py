import json
import duckdb
from kafka import KafkaConsumer
from datetime import datetime, timedelta

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

from datetime import datetime, timedelta, date
import duckdb

def epoch_to_date(epoch_val, format='days'):
    """
    Convert epoch value to date string with validation
    Supported formats:
    - 'days' (default): days since 1970-01-01 (Kafka Connect Date)
    - 'seconds': seconds since epoch
    - 'millis': milliseconds since epoch
    """
    if epoch_val is None:
        return None
        
    try:
        epoch_val = int(epoch_val)
        
        if format == 'days':
            return (date(1970, 1, 1) + timedelta(days=epoch_val)).isoformat()
        elif format == 'seconds':
            return datetime.utcfromtimestamp(epoch_val).date().isoformat()
        elif format == 'millis':
            return datetime.utcfromtimestamp(epoch_val/1000).date().isoformat()
        else:
            raise ValueError(f"Unsupported epoch format: {format}")
            
    except Exception as e:
        print(f"Error converting epoch {epoch_val} ({format}): {str(e)}")
        return None

def insert_to_duckdb(table, payload, schema_info=None):
    """
    Improved insert with proper type handling
    
    Parameters:
    - table: target table name
    - payload: dictionary of {column: value}
    - schema_info: optional schema information for type awareness
    """
    con = duckdb.connect('/app/olap/duckdb/hospital.db')
    
    try:
        # Prepare columns and values with type handling
        columns = []
        values = []
        
        for col, val in payload.items():
            col_type = None
            if schema_info:
                col_type = schema_info.get(col, {}).get('type')
            
            # Handle date conversion
            if col_type == 'date' or (schema_info is None and 'date' in col.lower()):
                converted_val = epoch_to_date(val)
                values.append(f"DATE '{converted_val}'" if converted_val else 'NULL')
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                values.append(str(val))
            elif isinstance(val, str):
                # Escape single quotes and wrap in quotes
                safe_val = val.replace("'", "''")
                values.append(f"'{safe_val}'")
            elif val is None:
                values.append('NULL')
            else:
                values.append(f"'{str(val)}'")
                
            columns.append(col)
        
        # Build and execute safe query
        query = f"""
        INSERT INTO {table} ({', '.join(columns)})
        VALUES ({', '.join(values)})
        """
        con.execute(query)
        
    except Exception as e:
        print(f"Error inserting into {table}: {str(e)}")
        raise
    finally:
        con.close()

def main():
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers='project_redpanda:29092',
        group_id='olap-duckdb-consumer',
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    for msg in consumer:
        try:
            payload = msg.value.get('payload', {})
            table = msg.topic.split('.')[-1]
            insert_to_duckdb(table, payload)
            print(f"[DuckDB] Inserted into {table}: {payload}")
        except Exception as e:
            print(f"[DuckDB] Error: {e}")

if __name__ == "__main__":
    main()

