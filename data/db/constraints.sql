-- data/db/constraints.sql

SET search_path TO healthcare, public;

-- Foreign Keys

ALTER TABLE providers
    ADD CONSTRAINT fk_providers_department
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL;

ALTER TABLE appointments
    ADD CONSTRAINT fk_appointments_patient
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_appointments_provider
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_appointments_department
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL;

ALTER TABLE encounters
    ADD CONSTRAINT fk_encounters_appointment
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_encounters_patient
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_encounters_provider
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE;

ALTER TABLE encounter_diagnoses
    ADD CONSTRAINT fk_ed_encounter
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_ed_diagnosis
    FOREIGN KEY (diagnosis_code) REFERENCES diagnoses(code) ON DELETE CASCADE;

ALTER TABLE prescriptions
    ADD CONSTRAINT fk_prescriptions_encounter
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_prescriptions_patient
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_prescriptions_provider
    FOREIGN KEY (provider_id) REFERENCES providers(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_prescriptions_medication
    FOREIGN KEY (medication_id) REFERENCES medications(id) ON DELETE RESTRICT;

ALTER TABLE invoices
    ADD CONSTRAINT fk_invoices_patient
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    ADD CONSTRAINT fk_invoices_encounter
    FOREIGN KEY (encounter_id) REFERENCES encounters(id) ON DELETE SET NULL;

ALTER TABLE payments
    ADD CONSTRAINT fk_payments_invoice
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE;


-- Check Constraints

ALTER TABLE appointments
    ADD CONSTRAINT chk_appointments_time
    CHECK (end_time > start_time),
    ADD CONSTRAINT chk_appointments_status
    CHECK (status IN ('Scheduled', 'Completed', 'Cancelled', 'No-Show'));

ALTER TABLE invoices
    ADD CONSTRAINT chk_invoices_amount
    CHECK (total_amount >= 0),
    ADD CONSTRAINT chk_invoices_dates
    CHECK (due_date >= issue_date),
    ADD CONSTRAINT chk_invoices_status
    CHECK (status IN ('Unpaid', 'Partially Paid', 'Paid', 'Cancelled'));

ALTER TABLE payments
    ADD CONSTRAINT chk_payments_amount
    CHECK (amount > 0);

ALTER TABLE prescriptions
    ADD CONSTRAINT chk_prescriptions_dates
    CHECK (end_date IS NULL OR end_date >= start_date),
    ADD CONSTRAINT chk_prescriptions_refills
    CHECK (refills >= 0);
