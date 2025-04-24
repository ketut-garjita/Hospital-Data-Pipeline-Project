import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

# Connect to PostgreSQL
conn = psycopg2.connect("host=localhost port=5433 dbname=hospital user=postgres password=postgres")
cur = conn.cursor()
faker = Faker()

# Insert doctors
for i in range(1, 11):
    cur.execute(
        "INSERT INTO doctors (name, specialization, experience_years, contact_info) VALUES (%s, %s, %s, %s) RETURNING doctor_id",
        (faker.name(), random.choice(["Cardiology", "Neurology", "Orthopedics", "Pediatrics"]),
         random.randint(5, 30), faker.phone_number())
    )

# Insert patients
for i in range(1, 101):
    cur.execute(
        "INSERT INTO patients (patient_id, full_name, date_of_birth, gender, blood_type, contact_info, insurance_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (i, faker.name(), faker.date_of_birth(minimum_age=1, maximum_age=90), random.choice(["Male", "Female"]),
         random.choice(["A", "B", "AB", "O"]), faker.phone_number(), faker.bothify(text='INS####'))
    )

# Insert visits and store their IDs
visit_ids = []
for i in range(1, 51):
    cur.execute(
        "INSERT INTO visits (patient_id, doctor_id, visit_date, diagnosis, total_cost) VALUES (%s, %s, %s, %s, %s) RETURNING visit_id",
        (random.randint(1, 100), random.randint(1, 10), faker.date_between(start_date="-1y", end_date="today"),
         faker.sentence(), round(random.uniform(50, 500), 2))
    )
    visit_id = cur.fetchone()[0]  # Retrieve the inserted visit_id
    visit_ids.append(visit_id)

# Insert medicines and store their IDs
medicine_ids = []
for i in range(1, 16):
    cur.execute(
        "INSERT INTO medicines (name, category, manufacturer, price) VALUES (%s, %s, %s, %s) RETURNING medicine_id",
        (faker.word(), random.choice(["Antibiotic", "Painkiller", "Antidepressant", "Antiviral"]),
         faker.company(), round(random.uniform(5, 100), 2))
    )
    medicine_id = cur.fetchone()[0]  # Retrieve the inserted medicine_id
    medicine_ids.append(medicine_id)

# Insert prescriptions using only existing medicine IDs
for i in range(1, 31):
    cur.execute(
        "INSERT INTO prescriptions (patient_id, doctor_id, medicine_id, dosage, duration) VALUES (%s, %s, %s, %s, %s)",
        (random.randint(1, 100), random.randint(1, 10), random.choice(medicine_ids), f"{random.randint(1, 3)} pills",
         f"{random.randint(3, 14)} days")
    )

# Insert billing payments using only existing visit IDs
for i in range(1, 41):
    if visit_ids:  # Ensure visit_ids list is not empty
        cur.execute(
            "INSERT INTO billing_payments (patient_id, visit_id, billing_date, total_amount, payment_status) VALUES (%s, %s, %s, %s, %s)",
            (random.randint(1, 100), random.choice(visit_ids), faker.date_between(start_date="-1y", end_date="today"),
             round(random.uniform(50, 500), 2), random.choice(["Paid", "Unpaid", "Pending"]))
        )

# Commit and close connection
conn.commit()
cur.close()
conn.close()
print("Data inserted successfully!")

