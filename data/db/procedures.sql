-- data/db/procedures.sql

SET search_path TO healthcare, public;

-- 1. Procedure to schedule an appointment
CREATE OR REPLACE PROCEDURE schedule_appointment(
    p_patient_id UUID,
    p_provider_id UUID,
    p_department_id UUID,
    p_appointment_date DATE,
    p_start_time TIME,
    p_end_time TIME,
    p_reason TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if end time is after start time
    IF p_end_time <= p_start_time THEN
        RAISE EXCEPTION 'End time must be after start time';
    END IF;

    -- Check provider availability
    IF NOT is_provider_available(p_provider_id, p_appointment_date, p_start_time, p_end_time) THEN
        RAISE EXCEPTION 'Provider is not available at the requested time';
    END IF;

    -- Insert the appointment
    INSERT INTO appointments (
        patient_id, provider_id, department_id, appointment_date, start_time, end_time, reason, status
    ) VALUES (
        p_patient_id, p_provider_id, p_department_id, p_appointment_date, p_start_time, p_end_time, p_reason, 'Scheduled'
    );
END;
$$;


-- 2. Procedure to process a payment and update invoice status
CREATE OR REPLACE PROCEDURE process_payment(
    p_invoice_id UUID,
    p_amount NUMERIC,
    p_payment_method VARCHAR,
    p_reference_number VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_amount NUMERIC;
    v_total_paid NUMERIC;
BEGIN
    -- Check if amount is valid
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Payment amount must be greater than zero';
    END IF;

    -- Insert the payment
    INSERT INTO payments (invoice_id, amount, payment_method, reference_number)
    VALUES (p_invoice_id, p_amount, p_payment_method, p_reference_number);

    -- Calculate total paid for this invoice (handled partially by the trigger, but we can do it here if we don't have a trigger. We WILL have a trigger to do this, so this procedure mainly acts as a unified entry point, but let's implement the logic in the trigger instead of here to prevent duplicate code. Alternatively, we can just do the insert here, and let the trigger fire.)
    
    -- Actually, a procedure can be useful to wrap business logic.
    -- The prompt asked for 3 triggers and 2 procedures.
    -- We'll rely on the trigger for status update, so this procedure just wraps the insert.
    -- Or we can make this procedure do the status update and NOT use a trigger for it. Let's do the status update here so the procedure has meat.
    
    SELECT total_amount INTO v_total_amount FROM invoices WHERE id = p_invoice_id;
    SELECT COALESCE(SUM(amount), 0) INTO v_total_paid FROM payments WHERE invoice_id = p_invoice_id;
    
    IF v_total_paid >= v_total_amount THEN
        UPDATE invoices SET status = 'Paid' WHERE id = p_invoice_id;
    ELSIF v_total_paid > 0 THEN
        UPDATE invoices SET status = 'Partially Paid' WHERE id = p_invoice_id;
    END IF;
    
END;
$$;
