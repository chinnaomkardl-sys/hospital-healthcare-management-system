"""
Script to add more patients and assign to remaining nurses
"""
import os
import sys
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Nurse, Patient, Doctor
import random

User = get_user_model()

# Get nurses
nurses = list(Nurse.objects.all())
patients = list(Patient.objects.all())

print(f"Total nurses: {len(nurses)}")
print(f"Total existing patients: {len(patients)}")

# Find nurses without patients
nurses_without_patients = [n for n in nurses if n.patients.count() == 0]
print(f"Nurses without patients: {len(nurses_without_patients)}")

# Get existing doctors
doctors = list(Doctor.objects.all())
if not doctors:
    print("No doctors found! Creating doctor profiles first...")
    from accounts.models import Department
    departments = list(Department.objects.all())
    if not departments:
        # Create a default department
        dept = Department.objects.create(name="General Medicine", code="GEN-MED")
        departments = [dept]
    
    # We need at least one doctor
    print("Please create doctors first using add_doctors.py script")
    sys.exit(1)

# Create new patients for nurses without patients
new_patients = []
for nurse in nurses_without_patients:
    # Generate unique patient data
    first_names = ['Amit', 'Priya', 'Raj', 'Sunita', 'Vijay', 'Anjali', 'Suresh', 'Meera', 'Kiran', 'Pooja']
    last_names = ['Patel', 'Sharma', 'Kumar', 'Singh', 'Joshi', 'Shah', 'Reddy', 'Nair', 'Das', 'Gupta']
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@email.com"
    
    # Create user
    user, created = User.objects.get_or_create(
        username=email,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone': f"9{random.randint(100000000, 999999999)}",
            'role': 'PATIENT'
        }
    )
    
    if created:
        user.set_password('password123')
        user.save()
    
    # Create patient
    patient, created = Patient.objects.get_or_create(
        user=user,
        defaults={
            'patient_id': f"PAT-{uuid.uuid4().hex[:6].upper()}",
            'date_of_birth': f"{random.randint(1960, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            'gender': random.choice(['M', 'F']),
            'blood_group': random.choice(['A+', 'B+', 'O+', 'AB+']),
            'emergency_contact': user.phone,
            'emergency_contact_name': f"{first_name} {last_name}",
            'assigned_doctor': random.choice(doctors),
            'assigned_nurse': nurse,
            'admission_status': 'OUTPATIENT'
        }
    )
    
    if created:
        new_patients.append(f"{first_name} {last_name}")
        print(f"Created patient: {first_name} {last_name} assigned to Nurse {nurse.user.get_full_name()}")

print(f"\nCreated {len(new_patients)} new patients")

# Now verify all nurses have patients
print("\n=== Final Patient Assignments ===")
for nurse in nurses:
    count = nurse.patients.count()
    if count > 0:
        patients_list = [p.user.get_full_name() for p in nurse.patients.all()]
        print(f"Nurse {nurse.user.get_full_name()}: {count} patients - {patients_list}")
    else:
        print(f"Nurse {nurse.user.get_full_name()}: {count} patients - NO PATIENTS!")

