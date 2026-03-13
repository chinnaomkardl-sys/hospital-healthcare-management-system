import os
import sys
import pathlib
import django

# Ensure the top-level project folder is on sys.path so the inner
# `hospital_management_system` package can be imported reliably.
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Nurse
from django.test import Client

User = get_user_model()

username = 'test_nurse_ci'
password = 'testpass123'

u, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': 'test_nurse_ci@example.com',
        'role': 'NURSE',
        'first_name': 'Test',
        'last_name': 'Nurse',
    }
)
if created:
    u.set_password(password)
    u.save()

nurse, ncreated = Nurse.objects.get_or_create(
    user=u,
    defaults={
        'license_number': f'LIC-{username}',
        'qualification': 'Test Qualification',
        'experience_years': 1,
    }
)

print('User created:', created)
print('Nurse profile created:', ncreated)
print('User has attribute nurse_profile:', hasattr(u, 'nurse_profile'))

client = Client()
logged_in = client.login(username=username, password=password)
print('Login successful:', logged_in)
resp = client.get('/nurses/patients/')
print('GET /nurses/patients/ ->', resp.status_code)
print('\nResponse snippet:\n')
print(resp.content.decode('utf-8', errors='ignore')[:1000])
