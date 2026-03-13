"""Script to add appointments and medical reports for doctors"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from accounts.models import Doctor, Patient, Appointment, MedicalReport, Prescription
from datetime import datetime, timedelta
import random
import uuid

# Get all doctors and patients
doctors = list(Doctor.objects.all())
patients = list(Patient.objects.all())

print("=" * 60)
print("Creating Appointments and Medical Reports")
print("=" * 60)

print(f"\nDoctors: {len(doctors)}")
print(f"Patients: {len(patients)}")

# Create appointments for each doctor-patient pair
print("\n" + "-" * 60)
print("Creating Appointments...")
print("-" * 60)

appointment_reasons = [
    'Regular Checkup', 'Follow-up Visit', 'Chest Pain', 'Headache',
    'Fever and Cold', 'Back Pain', 'Joint Pain', 'Annual Physical',
    'Blood Pressure Check', 'Diabetes Review', 'Skin Rash', 'Allergy Issues',
    'General Consultation', 'Prescription Renewal', 'Lab Results Review'
]

time_slots = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', 
              '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']

today = datetime.now().date()
created_appointments = 0

# Create appointments for each patient with their assigned doctor
for patient in patients:
    doctor = patient.assigned_doctor
    if not doctor:
        # Assign a random doctor if not assigned
        doctor = random.choice(doctors)
    
    # Create 2-3 appointments per patient
    num_appointments = random.randint(2, 3)
    for i in range(num_appointments):
        # Vary the date (past and future appointments)
        days_offset = random.randint(-15, 15)
        appointment_date = today + timedelta(days=days_offset)
        
        # Skip future appointments beyond 30 days
        if appointment_date > today + timedelta(days=30):
            continue
            
        appointment_time = random.choice(time_slots)
        
        # Determine status based on date
        if days_offset < 0:
            status = random.choice(['COMPLETED', 'COMPLETED', 'CANCELLED'])
        elif days_offset == 0:
            status = 'SCHEDULED'
        else:
            status = 'SCHEDULED'
        
        apt, created = Appointment.objects.get_or_create(
            patient=patient,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            defaults={
                'appointment_id': f"APT-{uuid.uuid4().hex[:8].upper()}",
                'reason': random.choice(appointment_reasons),
                'status': status,
                'consultation_fee': doctor.consultation_fee
            }
        )
        
        if created:
            created_appointments += 1
            status_str = "✓" if created else "-"
            print(f"  {status_str} {patient.user.get_full_name()} -> Dr. {doctor.user.get_full_name()} on {appointment_date} ({status})")

print(f"\nTotal appointments created: {created_appointments}")
print(f"Total appointments in database: {Appointment.objects.count()}")

# Create medical reports for completed appointments
print("\n" + "-" * 60)
print("Creating Medical Reports...")
print("-" * 60)

diagnoses = [
    'Acute Bronchitis', 'Type 2 Diabetes Mellitus', 'Hypertension Stage 1',
    'Seasonal Allergic Rhinitis', 'Gastroenteritis', 'Lower Back Pain',
    'Vitamin D Deficiency', 'Anxiety Disorder', 'Asthma (Mild Persistent)',
    'Hypercholesterolemia', 'Migraine', 'Acid Reflux (GERD)', 
    'Joint Pain - Arthritis', 'Sleep Disorder', 'Thyroid Disorder'
]

treatments = [
    'Rest and hydration - 5 days', 'Continue current medications',
    'Lifestyle modifications recommended', 'Follow-up in 2 weeks',
    'Physical therapy recommended', 'Dietary changes advised',
    'Regular exercise routine', 'Stress management techniques',
    'Monitor blood pressure daily', 'Reduce salt intake',
    'Take medications as prescribed', 'Avoid trigger foods'
]

completed_appointments = Appointment.objects.filter(status='COMPLETED')
created_reports = 0

for apt in completed_appointments:
    report, created = MedicalReport.objects.get_or_create(
        patient=apt.patient,
        doctor=apt.doctor,
        defaults={
            'diagnosis': random.choice(diagnoses),
            'treatment_plan': random.choice(treatments),
            'blood_pressure': f"{random.randint(110, 140)}/{random.randint(70, 90)}",
            'heart_rate': random.randint(60, 100),
            'temperature': round(random.uniform(97.5, 99.5), 1),
            'notes': 'Patient advised to follow healthy lifestyle and regular checkups.'
        }
    )
    
    if created:
        created_reports += 1
        print(f"  ✓ {apt.patient.user.get_full_name()} - Dr. {apt.doctor.user.get_full_name()}: {report.diagnosis}")

print(f"\nTotal medical reports created: {created_reports}")
print(f"Total medical reports in database: {MedicalReport.objects.count()}")

# Create prescriptions for completed appointments
print("\n" + "-" * 60)
print("Creating Prescriptions...")
print("-" * 60)

medicines = [
    {'name': 'Amoxicillin', 'dosage': '500mg', 'frequency': '3 times a day', 'duration': '7 days'},
    {'name': 'Paracetamol', 'dosage': '650mg', 'frequency': '2 times a day', 'duration': '5 days'},
    {'name': 'Metformin', 'dosage': '500mg', 'frequency': '2 times a day', 'duration': '30 days'},
    {'name': 'Atorvastatin', 'dosage': '20mg', 'frequency': '1 time a day', 'duration': '90 days'},
    {'name': 'Omeprazole', 'dosage': '20mg', 'frequency': '1 time a day', 'duration': '14 days'},
    {'name': 'Cetirizine', 'dosage': '10mg', 'frequency': '1 time a day', 'duration': '7 days'},
    {'name': 'Azithromycin', 'dosage': '250mg', 'frequency': '1 time a day', 'duration': '5 days'},
    {'name': 'Ibuprofen', 'dosage': '400mg', 'frequency': '3 times a day', 'duration': '5 days'},
    {'name': 'Aspirin', 'dosage': '75mg', 'frequency': '1 time a day', 'duration': '90 days'},
    {'name': 'Losartan', 'dosage': '50mg', 'frequency': '1 time a day', 'duration': '30 days'},
]

created_prescriptions = 0

for apt in completed_appointments:
    # Add 1-2 prescriptions per appointment
    num_rx = random.randint(1, 2)
    for i in range(num_rx):
        med = random.choice(medicines)
        rx, created = Prescription.objects.get_or_create(
            patient=apt.patient,
            doctor=apt.doctor,
            medicine_name=med['name'],
            defaults={
                'dosage': med['dosage'],
                'frequency': med['frequency'],
                'duration': med['duration'],
                'instructions': 'Take after meals',
                'notes': f"Prescribed for {apt.reason}"
            }
        )
        if created:
            created_prescriptions += 1
            print(f"  ✓ {apt.patient.user.get_full_name()} - {med['name']} {med['dosage']}")

print(f"\nTotal prescriptions created: {created_prescriptions}")
print(f"Total prescriptions in database: {Prescription.objects.count()}")

print("\n" + "=" * 60)
print("Summary:")
print("=" * 60)
print(f"  Appointments: {Appointment.objects.count()}")
print(f"  Medical Reports: {MedicalReport.objects.count()}")
print(f"  Prescriptions: {Prescription.objects.count()}")
print("=" * 60)

