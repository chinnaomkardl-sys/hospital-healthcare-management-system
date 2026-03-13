"""Script to add sample nurses and assign patients to nurses"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Patient, Nurse, Department
import uuid
import random

User = get_user_model()

def create_nurses():
    """Create sample nurses"""
    nurses_data = [
        {'first_name': 'Priya', 'last_name': 'Sharma', 'email': 'priya.sharma@hospital.com', 'phone': '9876543201', 'shift': 'MORNING', 'qualification': 'B.Sc Nursing', 'experience': 5},
        {'first_name': 'Anita', 'last_name': 'Desai', 'email': 'anita.desai@hospital.com', 'phone': '9876543202', 'shift': 'AFTERNOON', 'qualification': 'GNM', 'experience': 3},
        {'first_name': 'Sunita', 'last_name': 'Patel', 'email': 'sunita.patel@hospital.com', 'phone': '9876543203', 'shift': 'NIGHT', 'qualification': 'B.Sc Nursing', 'experience': 7},
        {'first_name': 'Meera', 'last_name': 'Iyer', 'email': 'meera.iyer@hospital.com', 'phone': '9876543204', 'shift': 'MORNING', 'qualification': 'ANM', 'experience': 2},
        {'first_name': 'Kavita', 'last_name': 'Reddy', 'email': 'kavita.reddy@hospital.com', 'phone': '9876543205', 'shift': 'AFTERNOON', 'qualification': 'B.Sc Nursing', 'experience': 4},
    ]
    
    # Get or create department
    dept, _ = Department.objects.get_or_create(
        name='General Nursing',
        defaults={'code': 'GEN-NUR', 'description': 'General Nursing Department'}
    )
    
    created = []
    for ndata in nurses_data:
        email = ndata['email']
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=ndata['first_name'],
                last_name=ndata['last_name'],
                phone=ndata['phone'],
                password='nurse123',
                role='NURSE'
            )
            
            nurse = Nurse.objects.create(
                user=user,
                license_number=f"NUR-{uuid.uuid4().hex[:6].upper()}",
                department=dept,
                shift=ndata['shift'],
                qualification=ndata['qualification'],
                experience_years=ndata['experience'],
                is_available=True
            )
            created.append(f"Nurse {ndata['first_name']} {ndata['last_name']}")
            print(f"Created: {user.get_full_name()}")
        else:
            print(f"Nurse already exists: {email}")
    
    return list(Nurse.objects.all())

def assign_patients_to_nurses(nurses):
    """Assign patients to nurses"""
    patients = list(Patient.objects.filter(assigned_nurse__isnull=True))
    
    if not patients:
        print("No unassigned patients found!")
        return
    
    print(f"\nAssigning {len(patients)} patients to nurses...")
    
    for i, patient in enumerate(patients):
        nurse = nurses[i % len(nurses)]
        patient.assigned_nurse = nurse
        patient.save()
        print(f"  Assigned {patient.user.get_full_name()} to Nurse {nurse.user.get_full_name()}")

def main():
    print("=" * 50)
    print("Adding Sample Nurses")
    print("=" * 50)
    
    # Create nurses
    nurses = create_nurses()
    print(f"\nTotal nurses: {len(nurses)}")
    
    # Assign patients to nurses
    assign_patients_to_nurses(nurses)
    
    # Print summary
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Total Nurses: {Nurse.objects.count()}")
    print(f"  Patients with assigned nurse: {Patient.objects.filter(assigned_nurse__isnull=False).count()}")
    print("=" * 50)

if __name__ == '__main__':
    main()

