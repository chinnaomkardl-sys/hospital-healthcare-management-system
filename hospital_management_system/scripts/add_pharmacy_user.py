from django.contrib.auth import get_user_model
import django

django.setup()

User = get_user_model()
username = 'pharmacy1'
email = 'pharmacy1@hospital.com'
password = 'pharmacy123'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='PHARMACIST'
    )
    print(f"Created pharmacy user '{username}' with role 'PHARMACIST'")
else:
    user = User.objects.get(username=username)
    print(f"Pharmacy user '{username}' already exists (role: {user.role})")
print("Pharmacy login credentials: username='pharmacy1', password='pharmacy123'")
print("Navigate to: http://127.0.0.1:8000/pharmacy/login/")
