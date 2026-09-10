-- data/db/views.sql

SET search_path TO healthcare, public;

-- 1. Patient Summary View
CREATE OR REPLACE VIEW v_patient_summary AS
SELECT 
    p.id AS patient_id,
    p.first_name,
    p.last_name,
    p.dob,
    calculate_patient_age(p.dob) AS age,
    p.gender,
    get_outstanding_balance(p.id) AS outstanding_balance,
    (SELECT encounter_date FROM encounters e WHERE e.patient_id = p.id ORDER BY encounter_date DESC LIMIT 1) AS last_encounter_date
FROM patients p;


-- 2. Provider Schedule View
CREATE OR REPLACE VIEW v_provider_schedule AS
SELECT 
    a.appointment_date,
    a.start_time,
    a.end_time,
    p.first_name || ' ' || p.last_name AS provider_name,
    d.name AS department_name,
    pat.first_name || ' ' || pat.last_name AS patient_name,
    a.status,
    a.reason
FROM appointments a
JOIN providers p ON a.provider_id = p.id
JOIN departments d ON a.department_id = d.id
JOIN patients pat ON a.patient_id = pat.id
ORDER BY a.appointment_date, a.start_time;


-- 3. Monthly Revenue View
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT 
    DATE_TRUNC('month', payment_date) AS month,
    SUM(amount) AS total_revenue,
    COUNT(id) AS payment_count
FROM payments
GROUP BY DATE_TRUNC('month', payment_date)
ORDER BY month DESC;


-- 4. Appointment Statistics View
CREATE OR REPLACE VIEW v_appointment_statistics AS
SELECT 
    d.name AS department_name,
    DATE_TRUNC('month', a.appointment_date) AS month,
    COUNT(a.id) AS total_appointments,
    SUM(CASE WHEN a.status = 'Completed' THEN 1 ELSE 0 END) AS completed_count,
    SUM(CASE WHEN a.status = 'No-Show' THEN 1 ELSE 0 END) AS noshow_count,
    SUM(CASE WHEN a.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
    ROUND(SUM(CASE WHEN a.status = 'No-Show' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id), 2) AS noshow_rate_pct
FROM appointments a
JOIN departments d ON a.department_id = d.id
GROUP BY d.name, DATE_TRUNC('month', a.appointment_date)
ORDER BY d.name, month DESC;


-- 5. Prescription History View
CREATE OR REPLACE VIEW v_prescription_history AS
SELECT 
    rx.id AS prescription_id,
    pat.first_name || ' ' || pat.last_name AS patient_name,
    prov.first_name || ' ' || prov.last_name AS prescribed_by,
    m.name AS medication_name,
    m.category AS medication_category,
    rx.dosage,
    rx.frequency,
    rx.start_date,
    rx.end_date,
    rx.refills
FROM prescriptions rx
JOIN patients pat ON rx.patient_id = pat.id
JOIN providers prov ON rx.provider_id = prov.id
JOIN medications m ON rx.medication_id = m.id
ORDER BY rx.start_date DESC;
