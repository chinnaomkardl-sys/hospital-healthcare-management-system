"""Script to check current data and add 20 sample prescriptions"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from accounts.models import Doctor, Patient, Prescription, Appointment
from datetime import datetime
import random

# Check current data
doctors = list(Doctor.objects.all())
patients = list(Patient.objects.all())
prescriptions = list(Prescription.objects.all())
appointments = list(Appointment.objects.all())

print("=" * 50)
print("Current Data:")
print(f"Doctors: {len(doctors)}")
print(f"Patients: {len(patients)}")
print(f"Prescriptions: {len(prescriptions)}")
print(f"Appointments: {len(appointments)}")
print("=" * 50)

# If there are doctors and patients, create 20 prescriptions
if doctors and patients:
    # Get or create appointments if none exist
    if not appointments:
        print("\nNo appointments found. Creating appointments first...")
        from accounts.models import Department
        departments = list(Department.objects.all())
        
        for i, patient in enumerate(patients[:8]):
            for j in range(2):
                doctor = random.choice(doctors)
                apt, created = Appointment.objects.get_or_create(
                    patient=patient,
                    doctor=doctor,
                    appointment_date=datetime.now().date(),
                    appointment_time=datetime.now().time(),
                    defaults={
                        'appointment_id': f"APT-{random.randint(100000, 999999)}",
                        'reason': 'General Checkup',
                        'status': 'COMPLETED',
                        'consultation_fee': doctor.consultation_fee
                    }
                )
        appointments = list(Appointment.objects.all())
        print(f"Created {len(appointments)} appointments")

    # 20 different prescriptions to add
    prescriptions_data = [
        {'medicine_name': 'Amoxicillin', 'dosage': '500mg', 'frequency': '3 times a day', 'duration': '7 days', 'instructions': 'Take after meals', 'notes': 'Antibiotic for infection'},
        {'medicine_name': 'Paracetamol', 'dosage': '650mg', 'frequency': '2 times a day', 'duration': '5 days', 'instructions': 'Take after meals', 'notes': 'For fever and pain'},
        {'medicine_name': 'Metformin', 'dosage': '500mg', 'frequency': '2 times a day', 'duration': '30 days', 'instructions': 'Take with food', 'notes': 'For diabetes management'},
        {'medicine_name': 'Atorvastatin', 'dosage': '20mg', 'frequency': '1 time a day', 'duration': '90 days', 'instructions': 'Take at night', 'notes': 'Cholesterol medication'},
        {'medicine_name': 'Omeprazole', 'dosage': '20mg', 'frequency': '1 time a day', 'duration': '14 days', 'instructions': 'Take before breakfast', 'notes': 'For acid reflux'},
        {'medicine_name': 'Cetirizine', 'dosage': '10mg', 'frequency': '1 time a day', 'duration': '7 days', 'instructions': 'Take at night', 'notes': 'For allergies'},
        {'medicine_name': 'Azithromycin', 'dosage': '250mg', 'frequency': '1 time a day', 'duration': '5 days', 'instructions': 'Take 1 hour before meals', 'notes': 'Antibiotic'},
        {'medicine_name': 'Ibuprofen', 'dosage': '400mg', 'frequency': '3 times a day', 'duration': '5 days', 'instructions': 'Take after meals', 'notes': 'For pain and inflammation'},
        {'medicine_name': 'Aspirin', 'dosage': '75mg', 'frequency': '1 time a day', 'duration': '90 days', 'instructions': 'Take after meals', 'notes': 'Blood thinner'},
        {'medicine_name': 'Losartan', 'dosage': '50mg', 'frequency': '1 time a day', 'duration': '30 days', 'instructions': 'Take at same time daily', 'notes': 'For blood pressure'},
        {'medicine_name': 'Amlodipine', 'dosage': '5mg', 'frequency': '1 time a day', 'duration': '30 days', 'instructions': 'Take at bedtime', 'notes': 'Calcium channel blocker'},
        {'medicine_name': 'Metoprolol', 'dosage': '25mg', 'frequency': '2 times a day', 'duration': '30 days', 'instructions': 'Take with food', 'notes': 'For heart rate control'},
        {'medicine_name': 'Levothyroxine', 'dosage': '50mcg', 'frequency': '1 time a day', 'duration': '90 days', 'instructions': 'Take on empty stomach', 'notes': 'Thyroid medication'},
        {'medicine_name': 'Gliclazide', 'dosage': '80mg', 'frequency': '1 time a day', 'duration': '30 days', 'instructions': 'Take with breakfast', 'notes': 'For diabetes'},
        {'medicine_name': 'Pantoprazole', 'dosage': '40mg', 'frequency': '1 time a day', 'duration': '14 days', 'instructions': 'Take before breakfast', 'notes': 'For GERD'},
        {'medicine_name': 'Cetirizine', 'dosage': '10mg', 'frequency': '1 time a day', 'duration': '10 days', 'instructions': 'Take at night', 'notes': 'For allergic rhinitis'},
        {'medicine_name': 'Diclofenac', 'dosage': '50mg', 'frequency': '2 times a day', 'duration': '7 days', 'instructions': 'Take after meals', 'notes': 'For joint pain'},
        {'medicine_name': 'Salbutamol', 'dosage': '2mg', 'frequency': '3 times a day', 'duration': '7 days', 'instructions': 'Take as needed', 'notes': 'For asthma'},
        {'medicine_name': 'Domperidone', 'dosage': '10mg', 'frequency': '3 times a day', 'duration': '7 days', 'instructions': 'Take before meals', 'notes': 'For nausea'},
        {'medicine_name': 'ORS Solution', 'dosage': '1 packet', 'frequency': 'As needed', 'duration': '3 days', 'instructions': 'Dissolve in water', 'notes': 'For dehydration'},
    ]

    created_count = 0
    apt_list = list(Appointment.objects.all())
    
    print(f"\nCreating 20 prescriptions...")
    for i, rx_data in enumerate(prescriptions_data):
        patient = patients[i % len(patients)]
        doctor = doctors[i % len(doctors)]
        
        rx, created = Prescription.objects.get_or_create(
            patient=patient,
            doctor=doctor,
            medicine_name=rx_data['medicine_name'],
            defaults={
                'dosage': rx_data['dosage'],
                'frequency': rx_data['frequency'],
                'duration': rx_data['duration'],
                'instructions': rx_data['instructions'],
                'notes': rx_data['notes']
            }
        )
        if created:
            created_count += 1
            print(f"  Created: {rx_data['medicine_name']} for {patient.user.get_full_name()}")
    
    print(f"\nTotal prescriptions created: {created_count}")
    print(f"Total prescriptions in database: {Prescription.objects.count()}")
else:
    print("\nCannot create prescriptions without doctors and patients!")
    print("Please ensure you have doctors and patients in the database first.")

