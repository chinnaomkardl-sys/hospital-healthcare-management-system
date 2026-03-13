"""Test what the nurse dashboard would see"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from accounts.models import Nurse, Patient, Appointment
from datetime import datetime

# Get the first nurse user
nurse_user_email = "anita.desai@hospital.com"
from django.contrib.auth import get_user_model
User = get_user_model()
nurse_user = User.objects.get(email=nurse_user_email)

print(f"=== Testing Nurse Dashboard for {nurse_user.get_full_name()} ===")
print(f"User role: {nurse_user.role}")
print(f"Has nurse_profile: {hasattr(nurse_user, 'nurse_profile')}")

# Get nurse profile
nurse = nurse_user.nurse_profile
print(f"Nurse ID: {nurse.id}")
print(f"Nurse department: {nurse.department}")

# Get assigned patients
assigned_patients = nurse.patients.all()
print(f"\nAssigned patients: {assigned_patients.count()}")
for p in assigned_patients:
    print(f"  - {p.user.get_full_name()} ({p.patient_id})")

# Get total patients
total_patients = nurse.patients.count()
print(f"\nTotal patients: {total_patients}")

# Get today's appointments for assigned patients
today = datetime.now().date()
patient_ids = nurse.patients.values_list('id', flat=True)

todays_appointments = Appointment.objects.filter(
    patient_id__in=patient_ids,
    appointment_date=today,
    status='SCHEDULED'
).select_related('patient__user', 'doctor__user')

print(f"\nToday's appointments: {todays_appointments.count()}")
for apt in todays_appointments:
    print(f"  - {apt.patient.user.get_full_name()} with Dr. {apt.doctor.user.get_full_name()} at {apt.appointment_time}")

# All upcoming appointments
upcoming_appointments = Appointment.objects.filter(
    patient_id__in=patient_ids,
    appointment_date__gte=today,
    status='SCHEDULED'
).select_related('patient__user', 'doctor__user').order_by('appointment_date', 'appointment_time')[:10]

print(f"\nUpcoming appointments: {upcoming_appointments.count()}")
for apt in upcoming_appointments:
    print(f"  - {apt.appointment_date} {apt.appointment_time}: {apt.patient.user.get_full_name()} with Dr. {apt.doctor.user.get_full_name()}")

