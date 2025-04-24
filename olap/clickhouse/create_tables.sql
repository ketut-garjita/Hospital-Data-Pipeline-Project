CREATE TABLE doctors
(
    doctor_id UInt64,
    name String,
    specialization String,
    experience_years UInt8,
    contact_info String
)
ENGINE = MergeTree
ORDER BY doctor_id;


CREATE TABLE patients
(
    patient_id UInt64,
    full_name String,
    date_of_birth Date,
    gender String,
    blood_type String,
    contact_info String,
    insurance_id String
)
ENGINE = MergeTree
ORDER BY patient_id;


CREATE TABLE medicines
(
    medicine_id UInt64,
    name String,
    category String,
    manufacturer String,
    price Decimal(10, 2)
)
ENGINE = MergeTree
ORDER BY medicine_id;


CREATE TABLE visits
(
    visit_id UInt64,
    patient_id UInt64,
    doctor_id UInt64,
    visit_date Date,
    diagnosis String,
    total_cost Decimal(10,2)
)
ENGINE = MergeTree
ORDER BY (visit_date, patient_id);


CREATE TABLE billing_payments
(
    billing_id UInt64,
    patient_id UInt64,
    visit_id UInt64,
    billing_date Date,
    total_amount Decimal(10,2),
    payment_status String
)
ENGINE = MergeTree
ORDER BY (billing_date, billing_id);


CREATE TABLE prescriptions
(
    prescription_id UInt64,
    patient_id UInt64,
    doctor_id UInt64,
    medicine_id UInt64,
    dosage String,
    duration String
)
ENGINE = MergeTree
ORDER BY prescription_id;


