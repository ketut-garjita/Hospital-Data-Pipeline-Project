CREATE TABLE doctors (
    doctor_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    specialization VARCHAR(100),
    experience_years INT,
    contact_info VARCHAR(255)
);
CREATE INDEX idx_doctors_specialization ON doctors(specialization);

CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(10),
    blood_type VARCHAR(5),
    contact_info VARCHAR(255),
    insurance_id VARCHAR(50)
);

CREATE TABLE medicines (
    medicine_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    manufacturer VARCHAR(100),
    price DECIMAL(10,2)
);
CREATE INDEX idx_manufacturer ON medicines(manufacturer);

CREATE TABLE visits (
    visit_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    doctor_id INT REFERENCES doctors(doctor_id),
    visit_date DATE,
    diagnosis TEXT,
    total_cost DECIMAL(10,2)
);
CREATE INDEX idx_visits_diagnosis ON visits(diagnosis);

-- Tabel Tagihan
CREATE TABLE billing_payments (
    billing_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    visit_id INT REFERENCES visits(visit_id),
    billing_date DATE,
    total_amount DECIMAL(10,2),
    payment_status VARCHAR(20)
);
CREATE INDEX idx_billing_payments_payment_status ON billing_payments(payment_status);

CREATE TABLE prescriptions (
    prescription_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    doctor_id INT REFERENCES doctors(doctor_id),
    medicine_id INT REFERENCES medicines(medicine_id),
    dosage VARCHAR(50),
    duration VARCHAR(50)
);
CREATE INDEX idx_prescriptions_duration ON prescriptions(duration);

