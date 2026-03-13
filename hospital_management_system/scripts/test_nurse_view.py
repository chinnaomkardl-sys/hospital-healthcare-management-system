"""Test what a nurse would see"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from accounts.models import Nurse, Patient

# Get the first nurse
nurse = Nurse.objects.first()
print(f"=== Testing nurse: {nurse.user.get_full_name()} ===")
print(f"Username: {nurse.user.username}")
print(f"Nurse ID: {nurse.id}")

# Get patients for this nurse
patients = nurse.patients.all()
print(f"\nPatients assigned to this nurse: {patients.count()}")

for patient in patients:
    print(f"  - {patient.user.get_full_name()} ({patient.patient_id})")

# Now simulate what NursePatientListView does
print("\n=== Simulating NursePatientListView.get_queryset() ===")
nurse_from_view = Nurse.objects.filter(user=nurse.user).first()
print(f"Nurse from view query: {nurse_from_view}")

if nurse_from_view:
    patients_from_view = nurse_from_view.patients.select_related('user', 'assigned_doctor')
    print(f"Patients from view: {patients_from_view.count()}")
    for p in patients_from_view:
        print(f"  - {p.user.get_full_name()}")

# Check all patients and their assigned nurses
print("\n=== All patients and their assigned nurses ===")
for patient in Patient.objects.all():
    nurse_name = patient.assigned_nurse.user.get_full_name() if patient.assigned_nurse else "None"
    print(f"  {patient.user.get_full_name()} -> Nurse: {nurse_name}")

