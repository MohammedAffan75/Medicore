-- data/db/tables.sql

SET search_path TO healthcare, public;

CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    contact_phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    department_id UUID, -- FK to departments
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    hire_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(20),
    blood_type VARCHAR(5),
    phone VARCHAR(20),
    email VARCHAR(255) UNIQUE,
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL, -- FK to patients
    provider_id UUID NOT NULL, -- FK to providers
    department_id UUID, -- FK to departments
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Scheduled', -- Scheduled, Completed, Cancelled, No-Show
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE encounters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID, -- FK to appointments
    patient_id UUID NOT NULL, -- FK to patients
    provider_id UUID NOT NULL, -- FK to providers
    encounter_date TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE diagnoses (
    code VARCHAR(20) PRIMARY KEY, -- e.g., ICD-10 code
    description TEXT NOT NULL,
    category VARCHAR(100)
);

CREATE TABLE encounter_diagnoses (
    encounter_id UUID NOT NULL, -- FK to encounters
    diagnosis_code VARCHAR(20) NOT NULL, -- FK to diagnoses
    is_primary BOOLEAN DEFAULT false,
    PRIMARY KEY (encounter_id, diagnosis_code)
);

CREATE TABLE medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    brand_name VARCHAR(200),
    category VARCHAR(100),
    dosage_form VARCHAR(50) -- Tablet, Liquid, Injection, etc.
);

CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encounter_id UUID NOT NULL, -- FK to encounters
    patient_id UUID NOT NULL, -- FK to patients
    provider_id UUID NOT NULL, -- FK to providers
    medication_id UUID NOT NULL, -- FK to medications
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    refills INT DEFAULT 0,
    instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL, -- FK to patients
    encounter_id UUID, -- FK to encounters
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Unpaid', -- Unpaid, Partially Paid, Paid, Cancelled
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL, -- FK to invoices
    payment_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount NUMERIC(10, 2) NOT NULL,
    payment_method VARCHAR(50), -- Credit Card, Cash, Insurance, Bank Transfer
    reference_number VARCHAR(100)
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL, -- UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100) DEFAULT 'system'
);
