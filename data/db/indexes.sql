-- data/db/indexes.sql

SET search_path TO healthcare, public;

-- Indexes for Foreign Keys to optimize joins
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_provider_id ON appointments(provider_id);
CREATE INDEX idx_encounters_patient_id ON encounters(patient_id);
CREATE INDEX idx_encounters_provider_id ON encounters(provider_id);
CREATE INDEX idx_encounters_appointment_id ON encounters(appointment_id);
CREATE INDEX idx_prescriptions_patient_id ON prescriptions(patient_id);
CREATE INDEX idx_prescriptions_provider_id ON prescriptions(provider_id);
CREATE INDEX idx_invoices_patient_id ON invoices(patient_id);
CREATE INDEX idx_payments_invoice_id ON payments(invoice_id);

-- Meaningful Indexes based on query patterns

-- 1. Provider Schedule: Frequently queried by provider and date
CREATE INDEX idx_appointments_provider_date ON appointments(provider_id, appointment_date);

-- 2. Patient Search: Searching by name and dob
CREATE INDEX idx_patients_name ON patients(last_name, first_name);
CREATE INDEX idx_patients_dob ON patients(dob);

-- 3. Invoice lookup by status for outstanding balances
CREATE INDEX idx_invoices_status ON invoices(status) WHERE status != 'Paid';

-- 4. Appointment Status lookup for reporting
CREATE INDEX idx_appointments_status ON appointments(status);

-- 5. Encounter Dates for time-based reporting
CREATE INDEX idx_encounters_date ON encounters(encounter_date);

-- 6. Medication Category lookup
CREATE INDEX idx_medications_category ON medications(category);
