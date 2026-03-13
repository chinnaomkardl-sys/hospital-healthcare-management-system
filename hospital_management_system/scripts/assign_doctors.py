"""Script to assign doctors to all patients automatically"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from accounts.models import Doctor, Patient
import random

# Get all doctors
doctors = list(Doctor.objects.all())
patients = list(Patient.objects.all())

print("=" * 60)
print("Assigning Doctors to Patients")
print("=" * 60)

# Group doctors by specialization
doctors_by_spec = {}
for doc in doctors:
    if doc.specialization not in doctors_by_spec:
        doctors_by_spec[doc.specialization] = []
    doctors_by_spec[doc.specialization].append(doc)

print(f"\nTotal Doctors: {len(doctors)}")
print(f"Total Patients: {len(patients)}")

# Assign doctors to patients based on specialization needs
# Common specializations get more patients
spec_weights = {
    'GENERAL': 3,
    'CARDIOLOGY': 2,
    'NEUROLOGY': 2,
    'ORTHOPEDICS': 2,
    'PEDIATRICS': 2,
    'DERMATOLOGY': 1,
    'SURGERY': 1,
    'PSYCHIATRY': 1,
    'RADIOLOGY': 1,
    'PATHOLOGY': 1,
}

# Create a weighted list of doctors
weighted_doctors = []
for doc in doctors:
    weight = spec_weights.get(doc.specialization, 1)
    weighted_doctors.extend([doc] * weight)

print(f"\nAssigning doctors to {len(patients)} patients...\n")

assigned_count = 0
for i, patient in enumerate(patients):
    if patient.assigned_doctor is None:
        # Assign based on specialization needs
        patient.assigned_doctor = random.choice(weighted_doctors)
        patient.save()
        print(f"  ✓ {patient.user.get_full_name()} -> Dr. {patient.assigned_doctor.user.get_full_name()} ({patient.assigned_doctor.specialization})")
        assigned_count += 1
    else:
        print(f"  - {patient.user.get_full_name()} (already has Dr. {patient.assigned_doctor.user.get_full_name()})")

print(f"\n{'=' * 60}")
print(f"Summary:")
print(f"  Total Patients: {len(patients)}")
print(f"  Newly Assigned: {assigned_count}")
print(f"  Already Had Doctor: {len(patients) - assigned_count}")
print(f"{'=' * 60}")

# Print current assignments
print("\nCurrent Patient-Doctor Assignments:")
print("-" * 60)
for patient in patients:
    if patient.assigned_doctor:
        print(f"  {patient.user.get_full_name()} -> Dr. {patient.assigned_doctor.user.get_full_name()} ({patient.assigned_doctor.specialization})")
    else:
        print(f"  {patient.user.get_full_name()} -> No doctor assigned")

