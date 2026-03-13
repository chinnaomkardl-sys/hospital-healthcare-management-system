"""Debug script to check nurse user accounts"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from accounts.models import Nurse, CustomUser

# Get all nurses and their user accounts
print('=== Nurse Profiles and User Accounts ===')
for nurse in Nurse.objects.all()[:5]:
    print(f'Nurse: {nurse.user.get_full_name()}')
    print(f'  Username: {nurse.user.username}')
    print(f'  Email: {nurse.user.email}')
    print(f'  Role: {nurse.user.role}')
    print()

# Get users with role NURSE
print('=== Users with NURSE role ===')
nurse_users = CustomUser.objects.filter(role='NURSE')
print(f'Total users with NURSE role: {nurse_users.count()}')
for user in nurse_users[:5]:
    has_profile = hasattr(user, 'nurse_profile')
    print(f'  Username: {user.username}, Name: {user.get_full_name()}, Has Nurse profile: {has_profile}')

# Check if there's a mismatch
print()
print('=== Checking for mismatches ===')
mismatch_count = 0
for user in CustomUser.objects.filter(role='NURSE'):
    if not hasattr(user, 'nurse_profile'):
        print(f'User {user.username} has role NURSE but NO Nurse profile!')
        mismatch_count += 1

if mismatch_count == 0:
    print('No mismatches found. All NURSE users have Nurse profiles.')

# Now check NurseProfile to User mapping
print()
print('=== Nurse Profiles to User mapping ===')
nurse_count = Nurse.objects.count()
print(f'Total Nurse profiles: {nurse_count}')

# Check if the login user is a nurse
print()
print('=== Sample nurse users for login ===')
for nurse in Nurse.objects.all()[:3]:
    print(f'Username: {nurse.user.username}, Password: password123, Name: {nurse.user.get_full_name()}')

