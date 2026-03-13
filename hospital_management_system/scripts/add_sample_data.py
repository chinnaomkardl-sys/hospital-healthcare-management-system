"""
Script to add sample data to the Hospital Management System
Run with: python manage.py shell < scripts/add_sample_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import (
    Patient, Doctor, Nurse, Department, 
    Appointment, Prescription, MedicalReport, Vitals
)
import uuid

User = get_user_model()

def create_departments():
    """Get existing departments"""
    departments = Department.objects.all()
    print(f"Found {departments.count()} departments")
    return departments

def create_patients():
    """Create sample patients"""
    patients_data = [
        {'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@email.com', 'phone': '9876543210', 'dob': '1985-03-15', 'gender': 'M', 'blood': 'A+'},
        {'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah.j@email.com', 'phone': '9876543211', 'dob': '1990-07-22', 'gender': 'F', 'blood': 'B+'},
        {'first_name': 'Michael', 'last_name': 'Brown', 'email': 'm.brown@email.com', 'phone': '9876543212', 'dob': '1978-11-08', 'gender': 'M', 'blood': 'O+'},
        {'first_name': 'Emily', 'last_name': 'Davis', 'email': 'emily.d@email.com', 'phone': '9876543213', 'dob': '1995-02-14', 'gender': 'F', 'blood': 'AB+'},
        {'first_name': 'Robert', 'last_name': 'Wilson', 'email': 'r.wilson@email.com', 'phone': '9876543214', 'dob': '1982-09-30', 'gender': 'M', 'blood': 'A-'},
        {'first_name': 'Jennifer', 'last_name': 'Martinez', 'email': 'j.martinez@email.com', 'phone': '9876543215', 'dob': '1988-12-25', 'gender': 'F', 'blood': 'O-'},
        {'first_name': 'David', 'last_name': 'Anderson', 'email': 'd.anderson@email.com', 'phone': '9876543216', 'dob': '1975-06-18', 'gender': 'M', 'blood': 'B-'},
        {'first_name': 'Lisa', 'last_name': 'Taylor', 'email': 'lisa.t@email.com', 'phone': '9876543217', 'dob': '1992-04-05', 'gender': 'F', 'blood': 'A+'},
    ]
    
    created = []
    for pdata in patients_data:
        email = pdata['email']
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=pdata['first_name'],
                last_name=pdata['last_name'],
                phone=pdata['phone'],
                password='password123',
                role='PATIENT'
            )
            
            patient = Patient.objects.create(
                user=user,
                patient_id=f"PAT-{uuid.uuid4().hex[:6].upper()}",
                date_of_birth=pdata['dob'],
                gender=pdata['gender'],
                blood_group=pdata['blood'],
                emergency_contact=pdata['phone'],
                emergency_contact_name=f"{pdata['first_name']} {pdata['last_name']}",
                admission_status='OUTPATIENT'
            )
            created.append(f"{pdata['first_name']} {pdata['last_name']}")
            print(f"Created patient: {patient.patient_id} - {user.get_full_name()}")
    
    return Patient.objects.all()

def create_appointments(doctors, patients):
    """Create sample appointments"""
    statuses = ['SCHEDULED', 'COMPLETED', 'CANCELLED', 'NO_SHOW']
    reasons = [
        'Regular Checkup', 'Follow-up Visit', 'Chest Pain', 'Headache',
        'Fever and Cold', 'Back Pain', 'Joint Pain', 'Annual Physical',
        'Blood Pressure Check', 'Diabetes Review', 'Skin Rash', 'Allergy Issues'
    ]
    
    created = 0
    today = datetime.now().date()
    
    for patient in patients[:6]:  # Create appointments for first 6 patients
        for i in range(3):  # 3 appointments per patient
            doctor = random.choice(doctors)
            days_offset = random.randint(-10, 20)
            appointment_date = today + timedelta(days=days_offset)
            
            # Don't create future appointments beyond 30 days
            if appointment_date > today + timedelta(days=30):
                continue
                
            appointment_time = f"{random.randint(9, 16)}:{random.choice(['00', '30'])}"
            
            if days_offset < 0:
                status = random.choice(['COMPLETED', 'CANCELLED', 'NO_SHOW'])
            elif days_offset == 0:
                status = 'SCHEDULED'
            else:
                status = 'SCHEDULED'
            
            apt, created_flag = Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                defaults={
                    'appointment_id': f"APT-{uuid.uuid4().hex[:6].upper()}",
                    'reason': random.choice(reasons),
                    'status': status,
                    'consultation_fee': doctor.consultation_fee,
                    'created_by': doctor.user
                }
            )
            if created_flag:
                created += 1
    
    print(f"Created {created} appointments")
    return Appointment.objects.all()

def create_prescriptions(doctors, patients):
    """Create sample prescriptions"""
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
    
    created = 0
    appointments = Appointment.objects.filter(status='COMPLETED')[:10]
    
    for apt in appointments:
        # Add 1-3 prescriptions per completed appointment
        num_prescriptions = random.randint(1, 3)
        for i in range(num_prescriptions):
            med = random.choice(medicines)
            rx, created_flag = Prescription.objects.get_or_create(
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
            if created_flag:
                created += 1
    
    print(f"Created {created} prescriptions")
    return Prescription.objects.all()

def create_medical_reports(doctors, patients):
    """Create sample medical reports"""
    diagnoses = [
        'Acute Bronchitis',
        'Type 2 Diabetes Mellitus',
        'Hypertension Stage 1',
        'Seasonal Allergic Rhinitis',
        'Gastroenteritis',
        'Lower Back Pain',
        'Vitamin D Deficiency',
        'Anxiety Disorder',
        'Asthma (Mild Persistent)',
        'Hypercholesterolemia'
    ]
    
    treatments = [
        'Rest and hydration - 5 days',
        'Continue current medications',
        'Lifestyle modifications recommended',
        'Follow-up in 2 weeks',
        'Physical therapy recommended',
        'Dietary changes advised',
        'Regular exercise routine',
        'Stress management techniques',
        'Monitor blood pressure daily',
        'Reduce salt intake'
    ]
    
    created = 0
    appointments = Appointment.objects.filter(status='COMPLETED')[:8]
    
    for apt in appointments:
        report, created_flag = MedicalReport.objects.get_or_create(
            patient=apt.patient,
            doctor=apt.doctor,
            diagnosis=random.choice(diagnoses),
            defaults={
                'treatment_plan': random.choice(treatments),
                'blood_pressure': f"{random.randint(110, 140)}/{random.randint(70, 90)}",
                'heart_rate': random.randint(60, 100),
                'temperature': round(random.uniform(97.5, 99.5), 1),
                'notes': 'Regular checkup completed. Patient advised to follow healthy lifestyle.'
            }
        )
        if created_flag:
            created += 1
    
    print(f"Created {created} medical reports")
    return MedicalReport.objects.all()

def create_vitals(nurses, patients):
    """Create sample vital records"""
    created = 0
    
    for patient in patients[:5]:
        for i in range(3):  # 3 vital records per patient
            nurse = random.choice(nurses) if nurses else None
            days_ago = i * 2
            recorded_at = datetime.now() - timedelta(days=days_ago)
            
            vitals, created_flag = Vitals.objects.get_or_create(
                patient=patient,
                nurse=nurse,
                recorded_at=recorded_at,
                defaults={
                    'blood_pressure': f"{random.randint(110, 140)}/{random.randint(70, 90)}",
                    'pulse_rate': random.randint(60, 100),
                    'temperature': round(random.uniform(97.5, 99.5), 1),
                    'oxygen_level': random.randint(95, 100),
                    'weight': round(random.uniform(50, 90), 1),
                    'notes': 'Vital signs within normal range'
                }
            )
            if created_flag:
                created += 1
    
    print(f"Created {created} vital records")
    return Vitals.objects.all()

def main():
    print("=" * 50)
    print("Adding Sample Data to Hospital Management System")
    print("=" * 50)
    
    # Create departments
    print("\n1. Creating Departments...")
    departments = create_departments()
    
    # Get or create doctors
    print("\n2. Checking Doctors...")
    doctors = list(Doctor.objects.all())
    if not doctors:
        print("No doctors found! Please create doctors first.")
        return
    
    print(f"Found {len(doctors)} doctors")
    
    # Get or create nurses
    print("\n3. Checking Nurses...")
    nurses = list(Nurse.objects.all())
    print(f"Found {len(nurses)} nurses")
    
    # Create patients
    print("\n4. Creating Patients...")
    patients = create_patients()
    print(f"Total patients: {patients.count()}")
    
    # Create appointments
    print("\n5. Creating Appointments...")
    appointments = create_appointments(doctors, patients)
    print(f"Total appointments: {appointments.count()}")
    
    # Create prescriptions
    print("\n6. Creating Prescriptions...")
    prescriptions = create_prescriptions(doctors, patients)
    print(f"Total prescriptions: {prescriptions.count()}")
    
    # Create medical reports
    print("\n7. Creating Medical Reports...")
    reports = create_medical_reports(doctors, patients)
    print(f"Total medical reports: {reports.count()}")
    
    # Create vital records
    print("\n8. Creating Vital Records...")
    vitals = create_vitals(nurses, patients)
    print(f"Total vital records: {vitals.count()}")
    
    print("\n" + "=" * 50)
    print("Sample data creation completed!")
    print("=" * 50)
    
    # Print summary
    print(f"""
Summary:
- Departments: {departments.count()}
- Doctors: {len(doctors)}
- Nurses: {len(nurses)}
- Patients: {patients.count()}
- Appointments: {appointments.count()}
- Prescriptions: {prescriptions.count()}
- Medical Reports: {reports.count()}
- Vital Records: {vitals.count()}
    """)

if __name__ == '__main__':
    main()

