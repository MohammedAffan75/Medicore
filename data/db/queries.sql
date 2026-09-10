-- data/db/queries.sql

SET search_path TO healthcare, public;

-- Query 1: Top 5 prescribed medications per department using Window Functions
WITH DeptMedications AS (
    SELECT 
        d.name AS department_name,
        m.name AS medication_name,
        COUNT(rx.id) AS prescription_count,
        ROW_NUMBER() OVER(PARTITION BY d.name ORDER BY COUNT(rx.id) DESC) as rank
    FROM prescriptions rx
    JOIN appointments a ON rx.encounter_id = (SELECT id FROM encounters WHERE appointment_id = a.id LIMIT 1)
    JOIN departments d ON a.department_id = d.id
    JOIN medications m ON rx.medication_id = m.id
    GROUP BY d.name, m.name
)
SELECT department_name, medication_name, prescription_count
FROM DeptMedications
WHERE rank <= 5;


-- Query 2: Providers with higher than average No-Show rates
WITH ProviderStats AS (
    SELECT 
        provider_id,
        COUNT(id) AS total_appointments,
        SUM(CASE WHEN status = 'No-Show' THEN 1 ELSE 0 END) AS noshows
    FROM appointments
    GROUP BY provider_id
),
ProviderRates AS (
    SELECT 
        p.first_name || ' ' || p.last_name AS provider_name,
        ps.total_appointments,
        ps.noshows,
        (ps.noshows * 100.0 / NULLIF(ps.total_appointments, 0)) AS noshow_rate
    FROM ProviderStats ps
    JOIN providers p ON ps.provider_id = p.id
)
SELECT * 
FROM ProviderRates
WHERE noshow_rate > (SELECT AVG(noshow_rate) FROM ProviderRates);


-- Query 3: Cumulative revenue by month using Window Functions
WITH MonthlyRevenue AS (
    SELECT 
        DATE_TRUNC('month', payment_date) AS month,
        SUM(amount) AS revenue
    FROM payments
    GROUP BY DATE_TRUNC('month', payment_date)
)
SELECT 
    month,
    revenue,
    SUM(revenue) OVER(ORDER BY month) AS cumulative_revenue
FROM MonthlyRevenue
ORDER BY month;


-- Query 4: Patients with 3 or more consecutive missed appointments
WITH OrderedAppointments AS (
    SELECT 
        patient_id,
        appointment_date,
        status,
        LAG(status, 1) OVER(PARTITION BY patient_id ORDER BY appointment_date) as prev1_status,
        LAG(status, 2) OVER(PARTITION BY patient_id ORDER BY appointment_date) as prev2_status
    FROM appointments
)
SELECT DISTINCT p.first_name, p.last_name, p.phone
FROM OrderedAppointments oa
JOIN patients p ON oa.patient_id = p.id
WHERE oa.status = 'No-Show' 
  AND oa.prev1_status = 'No-Show' 
  AND oa.prev2_status = 'No-Show';


-- Query 5: Average wait time between scheduling and appointment date per department
-- (Assuming created_at is when it was scheduled)
SELECT 
    d.name AS department_name,
    AVG(a.appointment_date - DATE(a.created_at)) AS avg_days_to_appointment
FROM appointments a
JOIN departments d ON a.department_id = d.id
GROUP BY d.name
ORDER BY avg_days_to_appointment DESC;


-- Query 6: Finding the most common comorbidities (Primary Diagnosis paired with Secondary)
WITH EncounterDiagnosesRanked AS (
    SELECT 
        encounter_id,
        diagnosis_code,
        is_primary
    FROM encounter_diagnoses
)
SELECT 
    d1.description AS primary_diagnosis,
    d2.description AS secondary_diagnosis,
    COUNT(*) as co_occurrence_count
FROM EncounterDiagnosesRanked e1
JOIN EncounterDiagnosesRanked e2 ON e1.encounter_id = e2.encounter_id AND e1.is_primary = true AND e2.is_primary = false
JOIN diagnoses d1 ON e1.diagnosis_code = d1.code
JOIN diagnoses d2 ON e2.diagnosis_code = d2.code
GROUP BY d1.description, d2.description
ORDER BY co_occurrence_count DESC
LIMIT 10;


-- Query 7: Patients who have seen providers in more than 3 different departments
SELECT 
    p.first_name, 
    p.last_name, 
    COUNT(DISTINCT a.department_id) AS departments_visited
FROM patients p
JOIN appointments a ON p.id = a.patient_id
GROUP BY p.id, p.first_name, p.last_name
HAVING COUNT(DISTINCT a.department_id) > 3;


-- Query 8: Revenue generated per diagnosis category
SELECT 
    d.category,
    SUM(i.total_amount) AS total_billed,
    SUM(p.amount) AS total_paid
FROM diagnoses d
JOIN encounter_diagnoses ed ON d.code = ed.diagnosis_code
JOIN encounters e ON ed.encounter_id = e.id
JOIN invoices i ON e.id = i.encounter_id
LEFT JOIN payments p ON i.id = p.invoice_id
WHERE ed.is_primary = true
GROUP BY d.category
ORDER BY total_billed DESC;


-- Query 9: Identifying potential medication conflicts (e.g., patient on two meds of same category from different providers)
WITH PatientMeds AS (
    SELECT 
        rx.patient_id,
        rx.provider_id,
        m.category AS med_category,
        m.name AS med_name
    FROM prescriptions rx
    JOIN medications m ON rx.medication_id = m.id
    WHERE rx.end_date >= CURRENT_DATE OR rx.end_date IS NULL
)
SELECT 
    p.first_name || ' ' || p.last_name AS patient_name,
    pm1.med_category,
    pm1.med_name AS med1,
    pm2.med_name AS med2,
    prov1.last_name AS provider1,
    prov2.last_name AS provider2
FROM PatientMeds pm1
JOIN PatientMeds pm2 ON pm1.patient_id = pm2.patient_id 
    AND pm1.med_category = pm2.med_category 
    AND pm1.med_name != pm2.med_name
    AND pm1.provider_id != pm2.provider_id
JOIN patients p ON pm1.patient_id = p.id
JOIN providers prov1 ON pm1.provider_id = prov1.id
JOIN providers prov2 ON pm2.provider_id = prov2.id
GROUP BY patient_name, pm1.med_category, med1, med2, provider1, provider2;


-- Query 10: Provider utilization rate (percentage of available hours booked)
-- Assuming 8 hours availability per day for 20 working days a month = 160 hours
WITH ProviderHoursBooked AS (
    SELECT 
        provider_id,
        DATE_TRUNC('month', appointment_date) AS month,
        SUM(EXTRACT(EPOCH FROM (end_time - start_time))/3600.0) AS hours_booked
    FROM appointments
    WHERE status NOT IN ('Cancelled')
    GROUP BY provider_id, DATE_TRUNC('month', appointment_date)
)
SELECT 
    p.first_name || ' ' || p.last_name AS provider_name,
    phb.month,
    phb.hours_booked,
    (phb.hours_booked / 160.0) * 100 AS utilization_percentage
FROM ProviderHoursBooked phb
JOIN providers p ON phb.provider_id = p.id
ORDER BY utilization_percentage DESC;
