from django.contrib.auth import get_user_model
import django

django.setup()

User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'Admin@123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print('Created superuser', username)
else:
    print('Superuser', username, 'already exists')
