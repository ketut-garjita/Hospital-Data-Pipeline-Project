import json
from confluent_kafka import Consumer, KafkaException
from google.cloud import storage
from datetime import datetime, timedelta
import os

REDPANDA_BROKER = "project_redpanda:29092"
GCS_BUCKET = "hospital_datalake"
TOPICS = [
    "postgres-source.public.visits",
    "postgres-source.public.billing_payments",
    "postgres-source.public.prescriptions"
]
GROUP_ID = "redpanda-to-gcs-group"

storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET)

def convert_debezium_date(days_since_epoch):
    """Convert Debezium date (days since epoch) to ISO date string"""
    if days_since_epoch is None:
        return None
    return (datetime(1970, 1, 1) + timedelta(days=days_since_epoch)).strftime('%Y-%m-%d')

def convert_debezium_timestamp(microseconds):
    """Convert Debezium timestamp (microseconds since epoch) to ISO datetime string"""
    if microseconds is None:
        return None
    return datetime.utcfromtimestamp(microseconds / 1000000).strftime('%Y-%m-%d %H:%M:%S')

def convert_debezium_decimal(decimal_value):
    """Convert Debezium decimal value properly"""
    if decimal_value is None:
        return None
    
    try:
        if isinstance(decimal_value, str):
            import base64
            from decimal import Decimal, getcontext
            
            decimal_bytes = base64.b64decode(decimal_value)
            
            scale = 2  
            unscaled = int.from_bytes(decimal_bytes, byteorder='big', signed=True)
            result = Decimal(unscaled) * (Decimal(10) ** -scale)
            
            return float(result)  
            
        elif isinstance(decimal_value, (int, float)):
            return float(decimal_value)
        
    except Exception as e:
        print(f"Decimal conversion error for value {decimal_value}: {e}")
    
    return None

def detect_and_convert_fields(record, schema):
    """Detect and convert temporal fields based on schema information"""
    converted = {}
    
    for field_name, value in record.items():
        field_schema = next((f for f in schema['fields'] if f['field'] == field_name), None)
        
        if field_schema:
            field_type = field_schema.get('name', '').lower()
            
            if 'date' in field_type and isinstance(value, int):
                converted[field_name] = convert_debezium_date(value)
            elif 'timestamp' in field_type and isinstance(value, int):
                converted[field_name] = convert_debezium_timestamp(value)
            elif 'decimal' in field_type:
                converted[field_name] = convert_debezium_decimal(value)
            else:
                converted[field_name] = value
        else:
            converted[field_name] = value
    
    return converted


processed_records = set()

def generate_record_hash(record):
    """Generate a unique hash for a record"""
    return hash(json.dumps(record, sort_keys=True))

def process_debezium_message(msg_value):
    try:
        data = json.loads(msg_value)
        payload = data.get('payload', {})
        schema = data.get('schema', {})
        
        record = payload.get('after', {})
        field_schemas = next((f['fields'] for f in schema.get('fields', []) if f.get('field') == 'after'), [])
        
        after_schema = {
            'fields': field_schemas,
            'name': schema.get('name', '')
        }
        
        converted_record = detect_and_convert_fields(record, after_schema)
        
        record_hash = generate_record_hash(converted_record)
        
        if record_hash in processed_records:
            return None  
        else:
            processed_records.add(record_hash)  
            
        return converted_record
    except Exception as e:
        print(f"Error processing message: {e}")
        return None


def upload_to_gcs(table_name, records):
    if not records:
        return
        
    folder_path = f"debezium/{table_name.split('.')[-1]}"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{folder_path}/{table_name.split('.')[-1]}_{timestamp}.json"
    
    blob = bucket.blob(file_name)
    with blob.open("w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    
    print(f"Uploaded {len(records)} records to gs://{GCS_BUCKET}/debezium/{file_name}")

conf = {
    'bootstrap.servers': REDPANDA_BROKER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}

consumer = Consumer(conf)
consumer.subscribe(TOPICS)

try:
    batch_size = 100  
    records_buffer = {topic: [] for topic in TOPICS}
    
    while True:
        msg = consumer.poll(1.0)
        
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        
        processed_record = process_debezium_message(msg.value())
        if processed_record:
            records_buffer[msg.topic()].append(processed_record)
            
            if len(records_buffer[msg.topic()]) >= batch_size:
                upload_to_gcs(msg.topic(), records_buffer[msg.topic()])
                records_buffer[msg.topic()] = []
                
                consumer.commit(asynchronous=False)

except KeyboardInterrupt:
    print("Interrupted by user")
finally:
    for topic, records in records_buffer.items():
        if records:
            upload_to_gcs(topic, records)
    
    consumer.close()

