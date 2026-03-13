"""Script to add 20 sample doctors to the Hospital Management System"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Doctor, Department
import uuid
import random

User = get_user_model()

# Get or create a department
dept, _ = Department.objects.get_or_create(
    name='General Medicine',
    defaults={'code': 'GEN', 'description': 'General Medicine Department'}
)

# List of 20 doctors with their details
doctors_data = [
    {'first_name': 'Rajesh', 'last_name': 'Kumar', 'specialization': 'CARDIOLOGY', 'qualification': 'MD, DM Cardiology', 'experience': 15},
    {'first_name': 'Priya', 'last_name': 'Sharma', 'specialization': 'NEUROLOGY', 'qualification': 'MD, DM Neurology', 'experience': 12},
    {'first_name': 'Amit', 'last_name': 'Patel', 'specialization': 'ORTHOPEDICS', 'qualification': 'MS Orthopedics', 'experience': 10},
    {'first_name': 'Sunita', 'last_name': 'Reddy', 'specialization': 'PEDIATRICS', 'qualification': 'MD Pediatrics', 'experience': 8},
    {'first_name': 'Vijay', 'last_name': 'Singh', 'specialization': 'GENERAL', 'qualification': 'MD General Medicine', 'experience': 20},
    {'first_name': 'Anjali', 'last_name': 'Mehta', 'specialization': 'DERMATOLOGY', 'qualification': 'MD Dermatology', 'experience': 7},
    {'first_name': 'Suresh', 'last_name': 'Gupta', 'specialization': 'SURGERY', 'qualification': 'MS Surgery', 'experience': 18},
    {'first_name': 'Kavita', 'last_name': 'Joshi', 'specialization': 'PSYCHIATRY', 'qualification': 'MD Psychiatry', 'experience': 9},
    {'first_name': 'Raj', 'last_name': 'Malhotra', 'specialization': 'RADIOLOGY', 'qualification': 'MD Radiology', 'experience': 11},
    {'first_name': 'Neha', 'last_name': 'Agarwal', 'specialization': 'PATHOLOGY', 'qualification': 'MD Pathology', 'experience': 6},
    {'first_name': 'Deepak', 'last_name': 'Shah', 'specialization': 'CARDIOLOGY', 'qualification': 'MD, DM Cardiology', 'experience': 14},
    {'first_name': 'Pooja', 'last_name': 'Nair', 'specialization': 'PEDIATRICS', 'qualification': 'MD Pediatrics', 'experience': 5},
    {'first_name': 'Arun', 'last_name': 'Menon', 'specialization': 'NEUROLOGY', 'qualification': 'MD, DM Neurology', 'experience': 16},
    {'first_name': 'Divya', 'last_name': 'Iyer', 'specialization': 'DERMATOLOGY', 'qualification': 'MD Dermatology', 'experience': 8},
    {'first_name': 'Manoj', 'last_name': 'Bhatia', 'specialization': 'ORTHOPEDICS', 'qualification': 'MS Orthopedics', 'experience': 13},
    {'first_name': 'Lakshmi', 'last_name': 'Raman', 'specialization': 'GENERAL', 'qualification': 'MD General Medicine', 'experience': 22},
    {'first_name': 'Harish', 'last_name': 'Chandra', 'specialization': 'SURGERY', 'qualification': 'MS Surgery', 'experience': 15},
    {'first_name': 'Uma', 'last_name': 'Mahesh', 'specialization': 'PSYCHIATRY', 'qualification': 'MD Psychiatry', 'experience': 10},
    {'first_name': 'Sanjay', 'last_name': 'Kapoor', 'specialization': 'RADIOLOGY', 'qualification': 'MD Radiology', 'experience': 12},
    {'first_name': 'Radha', 'last_name': 'Krishnan', 'specialization': 'PATHOLOGY', 'qualification': 'MD Pathology', 'experience': 7},
]

created_count = 0

print("=" * 50)
print("Adding 20 Fake Doctors")
print("=" * 50)

for doc_data in doctors_data:
    email = f"{doc_data['first_name'].lower()}.{doc_data['last_name'].lower()}@hospital.com"
    username = email
    
    # Check if user already exists
    if not User.objects.filter(email=email).exists():
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=doc_data['first_name'],
            last_name=doc_data['last_name'],
            password='doctor123',
            role='DOCTOR',
            phone=f"+91{random.randint(9000000000, 9999999999)}"
        )
        
        # Create doctor profile
        doctor = Doctor.objects.create(
            user=user,
            license_number=f"DR-{uuid.uuid4().hex[:8].upper()}",
            specialization=doc_data['specialization'],
            department=dept,
            qualification=doc_data['qualification'],
            experience_years=doc_data['experience'],
            consultation_fee=random.randint(300, 1500),
            is_available=True,
            bio=f"Experienced {doc_data['specialization'].lower()} specialist with {doc_data['experience']} years of practice."
        )
        
        created_count += 1
        print(f"Created: Dr. {doc_data['first_name']} {doc_data['last_name']} ({doc_data['specialization']})")
    else:
        print(f"Already exists: Dr. {doc_data['first_name']} {doc_data['last_name']}")

print(f"\nTotal doctors created: {created_count}")
print(f"Total doctors in database: {Doctor.objects.count()}")

# Print all available doctors
print("\n" + "=" * 50)
print("Available Doctors for Patient Assignment:")
print("=" * 50)
for doc in Doctor.objects.all()[:25]:
    status = "Available" if doc.is_available else "Busy"
    print(f"- Dr. {doc.user.get_full_name()} ({doc.specialization}) - {status}")

