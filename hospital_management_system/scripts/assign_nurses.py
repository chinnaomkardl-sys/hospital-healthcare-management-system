"""
Script to assign nurses to all patients automatically
Run with: python scripts/assign_nurses.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from accounts.models import Nurse, Patient
import random

# Get all nurses and patients
nurses = list(Nurse.objects.all())
patients = list(Patient.objects.all())

print("=" * 60)
print("Assigning Nurses to Patients")
print("=" * 60)

print(f"\nTotal Nurses: {len(nurses)}")
print(f"Total Patients: {len(patients)}")

if not nurses:
    print("\nNo nurses found! Please create nurses first.")
    sys.exit(1)

if not patients:
    print("\nNo patients found! Please create patients first.")
    sys.exit(1)

# Show current assignments before making changes
print("\n--- Current Nurse-Patient Assignments ---")
for patient in patients:
    if patient.assigned_nurse:
        print(f"  {patient.user.get_full_name()} -> Nurse {patient.assigned_nurse.user.get_full_name()}")
    else:
        print(f"  {patient.user.get_full_name()} -> No nurse assigned")

# Assign nurses to patients
print(f"\nAssigning nurses to {len(patients)} patients...\n")

# Group nurses by department
nurses_by_dept = {}
for nurse in nurses:
    dept_name = nurse.department.name if nurse.department else "General"
    if dept_name not in nurses_by_dept:
        nurses_by_dept[dept_name] = []
    nurses_by_dept[dept_name].append(nurse)

# Get all nurses for random assignment
all_nurses = nurses

assigned_count = 0
for i, patient in enumerate(patients):
    if patient.assigned_nurse is None:
        # Assign a random nurse
        nurse = random.choice(all_nurses)
        patient.assigned_nurse = nurse
        patient.save()
        print(f"  ✓ {patient.user.get_full_name()} -> Nurse {nurse.user.get_full_name()} ({nurse.department.name if nurse.department else 'General'})")
        assigned_count += 1
    else:
        print(f"  - {patient.user.get_full_name()} (already has Nurse {patient.assigned_nurse.user.get_full_name()})")

print(f"\n{'=' * 60}")
print(f"Summary:")
print(f"  Total Patients: {len(patients)}")
print(f"  Newly Assigned: {assigned_count}")
print(f"  Already Had Nurse: {len(patients) - assigned_count}")
print(f"{'=' * 60}")

# Print final assignments
print("\nFinal Patient-Nurse Assignments:")
print("-" * 60)
for patient in patients:
    if patient.assigned_nurse:
        print(f"  {patient.user.get_full_name()} -> Nurse {patient.assigned_nurse.user.get_full_name()} ({patient.assigned_nurse.department.name if patient.assigned_nurse.department else 'General'})")
    else:
        print(f"  {patient.user.get_full_name()} -> No nurse assigned")

# Verify by showing what each nurse sees
print("\n--- Verification: What each nurse will see ---")
for nurse in nurses:
    patient_count = nurse.patients.count()
    print(f"  Nurse {nurse.user.get_full_name()}: {patient_count} patients")

