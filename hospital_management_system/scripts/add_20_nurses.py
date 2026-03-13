"""Script to add 20 sample nurses and assign patients to nurses"""
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

def create_20_nurses():
    """Create 20 sample nurses"""
    nurses_data = [
        {'first_name': 'Priya', 'last_name': 'Sharma', 'email': 'priya.sharma@hospital.com', 'phone': '9876543201', 'shift': 'MORNING', 'qualification': 'B.Sc Nursing', 'experience': 8},
        {'first_name': 'Anita', 'last_name': 'Desai', 'email': 'anita.desai@hospital.com', 'phone': '9876543202', 'shift': 'AFTERNOON', 'qualification': 'GNM', 'experience': 5},
        {'first_name': 'Sunita', 'last_name': 'Patel', 'email': 'sunita.patel@hospital.com', 'phone': '9876543203', 'shift': 'NIGHT', 'qualification': 'B.Sc Nursing', 'experience': 10},
        {'first_name': 'Meera', 'last_name': 'Iyer', 'email': 'meera.iyer@hospital.com', 'phone': '9876543204', 'shift': 'MORNING', 'qualification': 'ANM', 'experience': 3},
        {'first_name': 'Kavita', 'last_name': 'Reddy', 'email': 'kavita.reddy@hospital.com', 'phone': '9876543205', 'shift': 'AFTERNOON', 'qualification': 'B.Sc Nursing', 'experience': 6},
        {'first_name': 'Lakshmi', 'last_name': 'Narayanan', 'email': 'lakshmi.n@hospital.com', 'phone': '9876543206', 'shift': 'NIGHT', 'qualification': 'GNM', 'experience': 4},
        {'first_name': 'Radha', 'last_name': 'Krishnan', 'email': 'radha.k@hospital.com', 'phone': '9876543207', 'shift': 'MORNING', 'qualification': 'B.Sc Nursing', 'experience': 7},
        {'first_name': 'Sarala', 'last_name': 'Devi', 'email': 'sarala.d@hospital.com', 'phone': '9876543208', 'shift': 'AFTERNOON', 'qualification': 'ANM', 'experience': 2},
        {'first_name': 'Vijaya', 'last_name': 'Kumar', 'email': 'vijaya.k@hospital.com', 'phone': '9876543209', 'shift': 'NIGHT', 'qualification': 'B.Sc Nursing', 'experience': 9},
        {'first_name': 'Kamala', 'last_name': 'Haasan', 'email': 'kamala.h@hospital.com', 'phone': '9876543210', 'shift': 'MORNING', 'qualification': 'GNM', 'experience': 5},
        {'first_name': 'Malini', 'last_name': 'Swamy', 'email': 'malini.s@hospital.com', 'phone': '9876543211', 'shift': 'AFTERNOON', 'qualification': 'B.Sc Nursing', 'experience': 11},
        {'first_name': 'Devi', 'last_name': 'Prasad', 'email': 'devi.p@hospital.com', 'phone': '9876543212', 'shift': 'NIGHT', 'qualification': 'ANM', 'experience': 4},
        {'first_name': 'Uma', 'last_name': 'Shankar', 'email': 'uma.s@hospital.com', 'phone': '9876543213', 'shift': 'MORNING', 'qualification': 'B.Sc Nursing', 'experience': 6},
        {'first_name': 'Janaki', 'last_name': 'Ram', 'email': 'janaki.r@hospital.com', 'phone': '9876543214', 'shift': 'AFTERNOON', 'qualification': 'GNM', 'experience': 3},
        {'first_name': 'Parvati', 'last_name': 'Menon', 'email': 'parvati.m@hospital.com', 'phone': '9876543215', 'shift': 'NIGHT', 'qualification': 'B.Sc Nursing', 'experience': 8},
        {'first_name': 'Shanti', 'last_name': 'Dorai', 'email': 'shanti.d@hospital.com', 'phone': '9876543216', 'shift': 'MORNING', 'qualification': 'ANM', 'experience': 2},
        {'first_name': 'Bharti', 'last_name': 'Agarwal', 'email': 'bharti.a@hospital.com', 'phone': '9876543217', 'shift': 'AFTERNOON', 'qualification': 'B.Sc Nursing', 'experience': 7},
        {'first_name': 'Chitra', 'last_name': 'Gupta', 'email': 'chitra.g@hospital.com', 'phone': '9876543218', 'shift': 'NIGHT', 'qualification': 'GNM', 'experience': 5},
        {'first_name': 'Asha', 'last_name': 'Bhatia', 'email': 'asha.b@hospital.com', 'phone': '9876543219', 'shift': 'MORNING', 'qualification': 'B.Sc Nursing', 'experience': 9},
        {'first_name': 'Geeta', 'last_name': 'Kapoor', 'email': 'geeta.k@hospital.com', 'phone': '9876543220', 'shift': 'AFTERNOON', 'qualification': 'ANM', 'experience': 4},
    ]
    
    # Get or create department
    dept, _ = Department.objects.get_or_create(
        name='General Nursing',
        defaults={'code': 'GEN-NUR', 'description': 'General Nursing Department'}
    )
    
    created = []
    for ndata in nurses_data:
        email = ndata['email']
        # Delete existing nurse with same email if exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if hasattr(user, 'nurse_profile'):
                user.nurse_profile.delete()
            user.delete()
        
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
        print(f"Created: {user.get_full_name()} - {ndata['shift']} shift")
    
    return list(Nurse.objects.all())

def assign_patients_to_nurses(nurses):
    """Assign patients to nurses"""
    patients = list(Patient.objects.all())
    
    if not patients:
        print("No patients found!")
        return
    
    print(f"\nAssigning {len(patients)} patients to {len(nurses)} nurses...")
    
    # Distribute patients evenly among nurses
    for i, patient in enumerate(patients):
        nurse = nurses[i % len(nurses)]
        patient.assigned_nurse = nurse
        patient.save()
        print(f"  {i+1}. {patient.user.get_full_name()} → {nurse.user.get_full_name()}")

def main():
    print("=" * 60)
    print("Creating 20 Sample Nurses with Patient Assignments")
    print("=" * 60)
    
    # Create nurses
    nurses = create_20_nurses()
    print(f"\nTotal nurses: {len(nurses)}")
    
    # Assign patients to nurses
    assign_patients_to_nurses(nurses)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total Nurses: {Nurse.objects.count()}")
    print(f"  Total Patients: {Patient.objects.count()}")
    print(f"  Patients with assigned nurse: {Patient.objects.filter(assigned_nurse__isnull=False).count()}")
    
    print("\nAll Nurse Credentials (Password: nurse123):")
    for n in Nurse.objects.all():
        print(f"  - {n.user.email}")
    print("=" * 60)

if __name__ == '__main__':
    main()

