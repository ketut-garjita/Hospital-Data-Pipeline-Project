import time
import json
import random
from datetime import datetime
from confluent_kafka import Producer

KAFKA_CONFIG = {
    "bootstrap.servers": "project_redpanda:29092"
}

TOPIC_VISITS = "topic_visits"
TOPIC_BILLING = "topic_billing"
TOPIC_PRESCRIPTIONS = "topic_prescriptions"

# Kafka Producer
producer = Producer(KAFKA_CONFIG)

def generate_visit():
    """Generate random visit data."""
    visit = {
        "visit_id": random.randint(1000, 9999),
        "patient_id": random.randint(1, 100),
        "doctor_id": random.randint(1, 10),
        "visit_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "diagnosis": random.choice(["Flu", "Cold", "Covid-19", "Allergy", "Diabetes"]),
        "total_cost": round(random.uniform(50, 500), 2)
    }
    return visit

def generate_billing(visit_id, patient_id):
    """Generate random billing data."""
    billing = {
        "billing_id": random.randint(10000, 99999),
        "patient_id": patient_id,
        "visit_id": visit_id,
        "billing_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_amount": round(random.uniform(50, 500), 2),
        "payment_status": random.choice(["Paid", "Pending", "Unpaid"])
    }
    return billing

def generate_prescription(visit_id, patient_id, doctor_id):
    """Generate random prescription data."""
    prescription = {
        "prescription_id": random.randint(100000, 999999),
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "medicine_id": random.randint(1, 15),  
        "dosage": random.choice(["1 tablet", "2 tablets", "5 ml", "10 ml"]),
        "duration": random.choice(["3 days", "1 week", "2 weeks"])
    }
    return prescription

if __name__ == "__main__":
    while True:
        visit_data = generate_visit()
        producer.produce(TOPIC_VISITS, key=str(visit_data["visit_id"]), value=json.dumps(visit_data))
        producer.flush()
        
        billing_data = generate_billing(visit_data["visit_id"], visit_data["patient_id"])
        producer.produce(TOPIC_BILLING, key=str(billing_data["billing_id"]), value=json.dumps(billing_data))
        producer.flush()
        
        prescription_data = generate_prescription(visit_data["visit_id"], visit_data["patient_id"], visit_data["doctor_id"])
        producer.produce(TOPIC_PRESCRIPTIONS, key=str(prescription_data["prescription_id"]), value=json.dumps(prescription_data))
        producer.flush()
        
        print(f"Produced Visit: {visit_data}")
        print(f"Produced Billing: {billing_data}")
        print(f"Produced Prescription: {prescription_data}")
        
        time.sleep(5)  

