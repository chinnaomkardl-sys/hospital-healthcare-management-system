from django.conf import settings
settings.configure()  # Minimal Django config if needed
import os
import sys
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from accounts.models import CustomUser
import subprocess

# Add test pharmacist if not exists
if not CustomUser.objects.filter(role='PHARMACIST').exists():
    user = CustomUser.objects.create_user(
        username='pharmacy1',
        email='pharmacy1@hospital.com',
        password='pharmacy123',
        role='PHARMACIST'
    )
    print('Created test pharmacist: pharmacy1@hospital.com / pharmacy123')

print('All pharmacists:')
for u in CustomUser.objects.filter(role='PHARMACIST'):
    print(f'- {u.email} (role: {u.role})')

print('\\nLogin URLs:')
print('1. Role choice: http://127.0.0.1:8000/accounts/role_choice/')
print('2. Direct pharmacy: http://127.0.0.1:8000/pharmacy/login/')
print('3. Admin register pharmacist: http://127.0.0.1:8000/accounts/pharmacist-register/')
