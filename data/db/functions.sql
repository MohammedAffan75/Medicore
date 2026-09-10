-- data/db/functions.sql

SET search_path TO healthcare, public;

-- 1. Function to calculate patient age
CREATE OR REPLACE FUNCTION calculate_patient_age(dob DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN EXTRACT(YEAR FROM age(CURRENT_DATE, dob))::INTEGER;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 2. Function to get outstanding balance for a patient
CREATE OR REPLACE FUNCTION get_outstanding_balance(p_patient_id UUID)
RETURNS NUMERIC AS $$
DECLARE
    total_balance NUMERIC := 0;
BEGIN
    SELECT COALESCE(SUM(total_amount), 0) INTO total_balance
    FROM invoices
    WHERE patient_id = p_patient_id
      AND status IN ('Unpaid', 'Partially Paid');
      
    -- Subtract partial payments if 'Partially Paid' means payments exist
    -- Actually, a better way is to sum total_amount and subtract sum(payment_amount)
    
    RETURN (
        SELECT COALESCE(SUM(i.total_amount), 0) - COALESCE(SUM(p.amount), 0)
        FROM invoices i
        LEFT JOIN payments p ON i.id = p.invoice_id
        WHERE i.patient_id = p_patient_id
    );
END;
$$ LANGUAGE plpgsql;


-- 3. Function to check if a provider is available for a given time slot
CREATE OR REPLACE FUNCTION is_provider_available(
    p_provider_id UUID, 
    p_appt_date DATE, 
    p_start_time TIME, 
    p_end_time TIME
)
RETURNS BOOLEAN AS $$
DECLARE
    conflict_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO conflict_count
    FROM appointments
    WHERE provider_id = p_provider_id
      AND appointment_date = p_appt_date
      AND status NOT IN ('Cancelled', 'No-Show')
      AND (
          (p_start_time >= start_time AND p_start_time < end_time) OR
          (p_end_time > start_time AND p_end_time <= end_time) OR
          (p_start_time <= start_time AND p_end_time >= end_time)
      );
      
    RETURN conflict_count = 0;
END;
$$ LANGUAGE plpgsql;
