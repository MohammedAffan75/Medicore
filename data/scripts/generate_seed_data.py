import random
from faker import Faker
import uuid
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
random.seed(42)

# Configuration
NUM_PATIENTS = 5500
NUM_PROVIDERS = 25
NUM_APPOINTMENTS = 12000

# Constants
DEPARTMENTS = [
    ("Cardiology", "Building A, 1st Floor", "555-0101"),
    ("Neurology", "Building A, 2nd Floor", "555-0102"),
    ("Pediatrics", "Building B, 1st Floor", "555-0103"),
    ("Oncology", "Building B, 2nd Floor", "555-0104"),
    ("Orthopedics", "Building C, 1st Floor", "555-0105"),
    ("General Practice", "Main Clinic", "555-0106"),
    ("Dermatology", "Main Clinic", "555-0107"),
    ("Psychiatry", "Building C, 2nd Floor", "555-0108"),
    ("Emergency", "ER Building", "555-9111"),
    ("Radiology", "Basement", "555-0110")
]

DIAGNOSES = [
    ("I10", "Essential (primary) hypertension", "Cardiology"),
    ("E11.9", "Type 2 diabetes mellitus without complications", "Endocrinology"),
    ("J45.909", "Unspecified asthma, uncomplicated", "Pulmonology"),
    ("M54.5", "Low back pain", "Orthopedics"),
    ("J01.90", "Acute sinusitis, unspecified", "ENT"),
    ("F41.1", "Generalized anxiety disorder", "Psychiatry"),
    ("F32.9", "Major depressive disorder, single episode, unspecified", "Psychiatry"),
    ("K21.9", "Gastro-esophageal reflux disease without esophagitis", "Gastroenterology"),
    ("L70.0", "Acne vulgaris", "Dermatology"),
    ("N39.0", "Urinary tract infection, site not specified", "Urology"),
    ("G43.909", "Migraine, unspecified, not intractable, without status migrainosus", "Neurology"),
    ("H10.9", "Unspecified conjunctivitis", "Ophthalmology"),
    ("J02.9", "Acute pharyngitis, unspecified", "ENT"),
    ("B35.3", "Tinea pedis", "Dermatology"),
    ("A09", "Infectious gastroenteritis and colitis, unspecified", "Gastroenterology"),
    ("R51", "Headache", "General"),
    ("R53.83", "Other fatigue", "General"),
    ("E78.5", "Hyperlipidemia, unspecified", "Cardiology"),
    ("M25.50", "Pain in unspecified joint", "Orthopedics"),
    ("D50.9", "Iron deficiency anemia, unspecified", "Hematology")
]

MEDICATIONS = [
    ("Lisinopril", "Prinivil", "Antihypertensive", "Tablet"),
    ("Atorvastatin", "Lipitor", "Statin", "Tablet"),
    ("Levothyroxine", "Synthroid", "Thyroid Hormone", "Tablet"),
    ("Metformin", "Glucophage", "Antidiabetic", "Tablet"),
    ("Amlodipine", "Norvasc", "Calcium Channel Blocker", "Tablet"),
    ("Metoprolol", "Lopressor", "Beta Blocker", "Tablet"),
    ("Omeprazole", "Prilosec", "Proton Pump Inhibitor", "Capsule"),
    ("Losartan", "Cozaar", "Antihypertensive", "Tablet"),
    ("Albuterol", "ProAir", "Bronchodilator", "Inhaler"),
    ("Gabapentin", "Neurontin", "Anticonvulsant", "Capsule"),
    ("Hydrochlorothiazide", "Microzide", "Diuretic", "Tablet"),
    ("Sertraline", "Zoloft", "Antidepressant", "Tablet"),
    ("Simvastatin", "Zocor", "Statin", "Tablet"),
    ("Montelukast", "Singulair", "Leukotriene Receptor Antagonist", "Tablet"),
    ("Escitalopram", "Lexapro", "Antidepressant", "Tablet"),
    ("Acetaminophen", "Tylenol", "Analgesic", "Tablet"),
    ("Ibuprofen", "Advil", "NSAID", "Tablet"),
    ("Amoxicillin", "Amoxil", "Antibiotic", "Capsule"),
    ("Azithromycin", "Zithromax", "Antibiotic", "Tablet"),
    ("Citalopram", "Celexa", "Antidepressant", "Tablet"),
    ("Fluoxetine", "Prozac", "Antidepressant", "Capsule"),
    ("Pantoprazole", "Protonix", "Proton Pump Inhibitor", "Tablet"),
    ("Prednisone", "Deltasone", "Corticosteroid", "Tablet"),
    ("Trazodone", "Desyrel", "Antidepressant", "Tablet"),
    ("Duloxetine", "Cymbalta", "Antidepressant", "Capsule"),
    ("Fluticasone", "Flonase", "Corticosteroid", "Nasal Spray"),
    ("Venlafaxine", "Effexor", "Antidepressant", "Capsule"),
    ("Warfarin", "Coumadin", "Anticoagulant", "Tablet"),
    ("Meloxicam", "Mobic", "NSAID", "Tablet"),
    ("Clonazepam", "Klonopin", "Benzodiazepine", "Tablet"),
    ("Lorazepam", "Ativan", "Benzodiazepine", "Tablet"),
    ("Glipizide", "Glucotrol", "Antidiabetic", "Tablet"),
    ("Cyclobenzaprine", "Flexeril", "Muscle Relaxant", "Tablet"),
    ("Tamsulosin", "Flomax", "Alpha Blocker", "Capsule"),
    ("Rosuvastatin", "Crestor", "Statin", "Tablet"),
    ("Oxycodone", "OxyContin", "Opioid Analgesic", "Tablet"),
    ("Clopidogrel", "Plavix", "Antiplatelet", "Tablet"),
    ("Propranolol", "Inderal", "Beta Blocker", "Tablet"),
    ("Aspirin", "Bayer", "NSAID", "Tablet"),
    ("Ranitidine", "Zantac", "H2 Blocker", "Tablet"),
    ("Diltiazem", "Cardizem", "Calcium Channel Blocker", "Tablet"),
    ("Carvedilol", "Coreg", "Beta Blocker", "Tablet"),
    ("Paroxetine", "Paxil", "Antidepressant", "Tablet"),
    ("Lorazepam", "Ativan", "Benzodiazepine", "Tablet"),
    ("Allopurinol", "Zyloprim", "Xanthine Oxidase Inhibitor", "Tablet"),
    ("Pravastatin", "Pravachol", "Statin", "Tablet"),
    ("Spironolactone", "Aldactone", "Diuretic", "Tablet"),
    ("Ondansetron", "Zofran", "Antiemetic", "Tablet"),
    ("Diazepam", "Valium", "Benzodiazepine", "Tablet"),
    ("Naproxen", "Aleve", "NSAID", "Tablet")
]

def escape_sql(value):
    if value is None:
        return "NULL"
    if isinstance(value, str):
        return f"'{value.replace(chr(39), chr(39)+chr(39))}'"
    return str(value)

def generate():
    with open('data/db/seed.sql', 'w', encoding='utf-8') as f:
        f.write("SET search_path TO healthcare, public;\n\n")

        print("Generating Departments...")
        department_ids = []
        for name, loc, phone in DEPARTMENTS:
            dep_id = str(uuid.uuid4())
            department_ids.append(dep_id)
            f.write(f"INSERT INTO departments (id, name, location, contact_phone) VALUES ({escape_sql(dep_id)}, {escape_sql(name)}, {escape_sql(loc)}, {escape_sql(phone)});\n")

        print("Generating Providers...")
        provider_ids = []
        for _ in range(NUM_PROVIDERS):
            prov_id = str(uuid.uuid4())
            provider_ids.append(prov_id)
            dep_id = random.choice(department_ids)
            f.write(f"INSERT INTO providers (id, first_name, last_name, specialty, department_id, email, phone, hire_date) VALUES ({escape_sql(prov_id)}, {escape_sql(fake.first_name())}, {escape_sql(fake.last_name())}, {escape_sql(fake.job())}, {escape_sql(dep_id)}, {escape_sql(fake.unique.company_email())}, {escape_sql(fake.phone_number()[:20])}, {escape_sql(fake.date_between(start_date='-10y', end_date='today'))});\n")

        print("Generating Patients...")
        patient_ids = []
        f.write("INSERT INTO patients (id, first_name, last_name, dob, gender, blood_type, phone, email, address) VALUES \n")
        patient_values = []
        for i in range(NUM_PATIENTS):
            pat_id = str(uuid.uuid4())
            patient_ids.append(pat_id)
            blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            gender = random.choice(["Male", "Female", "Other"])
            val = f"({escape_sql(pat_id)}, {escape_sql(fake.first_name())}, {escape_sql(fake.last_name())}, {escape_sql(fake.date_of_birth(minimum_age=0, maximum_age=100))}, {escape_sql(gender)}, {escape_sql(random.choice(blood_types))}, {escape_sql(fake.phone_number()[:20])}, {escape_sql(fake.unique.email())}, {escape_sql(fake.address().replace(chr(10), ', '))})"
            patient_values.append(val)
            if len(patient_values) == 1000:
                f.write(",\n".join(patient_values) + ";\nINSERT INTO patients (id, first_name, last_name, dob, gender, blood_type, phone, email, address) VALUES \n")
                patient_values = []
        
        if patient_values:
            f.write(",\n".join(patient_values) + ";\n")
        else:
            # truncate the last INSERT INTO if empty
            f.seek(f.tell() - 110)
            f.truncate()

        print("Generating Diagnoses...")
        for code, desc, cat in DIAGNOSES:
            f.write(f"INSERT INTO diagnoses (code, description, category) VALUES ({escape_sql(code)}, {escape_sql(desc)}, {escape_sql(cat)});\n")

        print("Generating Medications...")
        medication_ids = []
        for name, brand, cat, form in MEDICATIONS:
            med_id = str(uuid.uuid4())
            medication_ids.append(med_id)
            f.write(f"INSERT INTO medications (id, name, brand_name, category, dosage_form) VALUES ({escape_sql(med_id)}, {escape_sql(name)}, {escape_sql(brand)}, {escape_sql(cat)}, {escape_sql(form)});\n")

        print("Generating Appointments, Encounters, Prescriptions, Invoices, Payments...")
        start_date = datetime.today() - timedelta(days=365)
        
        f.write("INSERT INTO appointments (id, patient_id, provider_id, department_id, appointment_date, start_time, end_time, status, reason) VALUES \n")
        appointment_vals = []
        encounter_vals = []
        encounter_diag_vals = []
        prescription_vals = []
        invoice_vals = []
        payment_vals = []
        
        for i in range(NUM_APPOINTMENTS):
            appt_id = str(uuid.uuid4())
            pat_id = random.choice(patient_ids)
            prov_id = random.choice(provider_ids)
            dep_id = random.choice(department_ids) # Simple assignment
            
            appt_date = fake.date_between(start_date='-2y', end_date='+2m')
            st_hour = random.randint(8, 16)
            st_min = random.choice([0, 15, 30, 45])
            start_time = f"{st_hour:02d}:{st_min:02d}:00"
            end_time = f"{(st_hour + 1):02d}:{st_min:02d}:00"
            
            statuses = ["Scheduled", "Completed", "Completed", "Completed", "Cancelled", "No-Show"]
            status = random.choice(statuses)
            
            appointment_vals.append(f"({escape_sql(appt_id)}, {escape_sql(pat_id)}, {escape_sql(prov_id)}, {escape_sql(dep_id)}, {escape_sql(appt_date)}, {escape_sql(start_time)}, {escape_sql(end_time)}, {escape_sql(status)}, {escape_sql(fake.sentence())})")
            
            if len(appointment_vals) == 1000:
                f.write(",\n".join(appointment_vals) + ";\nINSERT INTO appointments (id, patient_id, provider_id, department_id, appointment_date, start_time, end_time, status, reason) VALUES \n")
                appointment_vals = []

            # Generate Encounter for Completed
            if status == "Completed":
                enc_id = str(uuid.uuid4())
                enc_datetime = datetime.combine(appt_date, datetime.strptime(start_time, "%H:%M:%S").time())
                encounter_vals.append(f"({escape_sql(enc_id)}, {escape_sql(appt_id)}, {escape_sql(pat_id)}, {escape_sql(prov_id)}, {escape_sql(enc_datetime)}, {escape_sql(fake.paragraph())})")
                
                # Diagnoses
                num_diag = random.randint(1, 3)
                diags = random.sample(DIAGNOSES, num_diag)
                for j, d in enumerate(diags):
                    is_prim = (j == 0)
                    encounter_diag_vals.append(f"({escape_sql(enc_id)}, {escape_sql(d[0])}, {escape_sql(is_prim)})")

                # Prescriptions
                if random.random() > 0.5:
                    num_rx = random.randint(1, 3)
                    rxs = random.sample(medication_ids, num_rx)
                    for rx in rxs:
                        rx_id = str(uuid.uuid4())
                        end_d = appt_date + timedelta(days=30)
                        prescription_vals.append(f"({escape_sql(rx_id)}, {escape_sql(enc_id)}, {escape_sql(pat_id)}, {escape_sql(prov_id)}, {escape_sql(rx)}, {escape_sql('1 pill')}, {escape_sql('Once a day')}, {escape_sql(appt_date)}, {escape_sql(end_d)}, {random.randint(0, 3)}, {escape_sql('Take with food')})")

                # Invoices
                inv_id = str(uuid.uuid4())
                total = round(random.uniform(50, 500), 2)
                due_d = appt_date + timedelta(days=30)
                inv_status = random.choice(["Paid", "Paid", "Unpaid", "Partially Paid"])
                invoice_vals.append(f"({escape_sql(inv_id)}, {escape_sql(pat_id)}, {escape_sql(enc_id)}, {escape_sql(appt_date)}, {escape_sql(due_d)}, {total}, {escape_sql(inv_status)})")

                # Payments
                if inv_status == "Paid":
                    pay_id = str(uuid.uuid4())
                    payment_vals.append(f"({escape_sql(pay_id)}, {escape_sql(inv_id)}, {escape_sql(enc_datetime + timedelta(days=random.randint(0, 10)))}, {total}, {escape_sql(random.choice(['Credit Card', 'Insurance', 'Cash']))}, {escape_sql(fake.bothify(text='REF-####-####'))})")
                elif inv_status == "Partially Paid":
                    pay_id = str(uuid.uuid4())
                    partial_total = round(total / 2, 2)
                    payment_vals.append(f"({escape_sql(pay_id)}, {escape_sql(inv_id)}, {escape_sql(enc_datetime + timedelta(days=random.randint(0, 10)))}, {partial_total}, {escape_sql(random.choice(['Credit Card', 'Insurance', 'Cash']))}, {escape_sql(fake.bothify(text='REF-####-####'))})")

        if appointment_vals:
            f.write(",\n".join(appointment_vals) + ";\n")
            
        def write_batches(table, cols, vals, chunk_size=1000):
            if not vals: return
            f.write(f"INSERT INTO {table} ({cols}) VALUES \n")
            for i in range(0, len(vals), chunk_size):
                chunk = vals[i:i+chunk_size]
                f.write(",\n".join(chunk))
                if i + chunk_size < len(vals):
                    f.write(f";\nINSERT INTO {table} ({cols}) VALUES \n")
                else:
                    f.write(";\n")

        print("Writing encounters...")
        write_batches("encounters", "id, appointment_id, patient_id, provider_id, encounter_date, notes", encounter_vals)
        print("Writing encounter_diagnoses...")
        write_batches("encounter_diagnoses", "encounter_id, diagnosis_code, is_primary", encounter_diag_vals)
        print("Writing prescriptions...")
        write_batches("prescriptions", "id, encounter_id, patient_id, provider_id, medication_id, dosage, frequency, start_date, end_date, refills, instructions", prescription_vals)
        print("Writing invoices...")
        write_batches("invoices", "id, patient_id, encounter_id, issue_date, due_date, total_amount, status", invoice_vals)
        print("Writing payments...")
        write_batches("payments", "id, invoice_id, payment_date, amount, payment_method, reference_number", payment_vals)

    print("Data generation complete.")

if __name__ == "__main__":
    generate()
