-- data/db/triggers.sql

SET search_path TO healthcare, public;

-- 1. Trigger to update invoice status after a payment is made or updated
CREATE OR REPLACE FUNCTION trg_func_update_invoice_status()
RETURNS TRIGGER AS $$
DECLARE
    v_total_amount NUMERIC;
    v_total_paid NUMERIC;
BEGIN
    SELECT total_amount INTO v_total_amount FROM invoices WHERE id = NEW.invoice_id;
    SELECT COALESCE(SUM(amount), 0) INTO v_total_paid FROM payments WHERE invoice_id = NEW.invoice_id;
    
    IF v_total_paid >= v_total_amount THEN
        UPDATE invoices SET status = 'Paid' WHERE id = NEW.invoice_id;
    ELSIF v_total_paid > 0 THEN
        UPDATE invoices SET status = 'Partially Paid' WHERE id = NEW.invoice_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_invoice_status
AFTER INSERT OR UPDATE ON payments
FOR EACH ROW
EXECUTE FUNCTION trg_func_update_invoice_status();


-- 2. Trigger to prevent double booking of providers
CREATE OR REPLACE FUNCTION trg_func_prevent_double_booking()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT is_provider_available(NEW.provider_id, NEW.appointment_date, NEW.start_time, NEW.end_time) THEN
        RAISE EXCEPTION 'Double booking error: Provider is already booked for this time slot.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_double_booking
BEFORE INSERT ON appointments
FOR EACH ROW
EXECUTE FUNCTION trg_func_prevent_double_booking();


-- 3. Trigger to audit patient updates
CREATE OR REPLACE FUNCTION trg_func_audit_patient_updates()
RETURNS TRIGGER AS $$
BEGIN
    IF ROW(OLD.*) IS DISTINCT FROM ROW(NEW.*) THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_data, new_data, changed_by)
        VALUES (
            'patients',
            NEW.id,
            'UPDATE',
            row_to_json(OLD)::jsonb,
            row_to_json(NEW)::jsonb,
            current_user
        );
        
        -- Also update the updated_at timestamp
        NEW.updated_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_patient_updates
BEFORE UPDATE ON patients
FOR EACH ROW
EXECUTE FUNCTION trg_func_audit_patient_updates();
