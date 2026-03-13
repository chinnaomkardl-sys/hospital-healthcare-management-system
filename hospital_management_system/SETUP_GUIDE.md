# Hospital Healthcare Management System - Setup Guide

## Project Overview
This is a fully functional Hospital Healthcare Management System built with Django. It includes role-based authentication, appointment management, patient records, medical reports, and more.

## System Requirements
- Python 3.8+
- pip (Python package installer)
- virtualenv (recommended)

## Installation Steps

### Step 1: Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

### Step 5: Create Demo Data (Optional)
```bash
python manage.py shell

# Execute the following in the Django shell:
from accounts.models import CustomUser, Department, Doctor, Nurse, Receptionist, Patient
from datetime import date
import uuid

# Create departments
dept1 = Department.objects.create(name="Cardiology", code="CARD")
dept2 = Department.objects.create(name="General Medicine", code="GEN")

# Create demo admin (if not created via createsuperuser)
admin_user = CustomUser.objects.create_superuser(
    username='admin@hospital.com',
    email='admin@hospital.com',
    password='admin123',
    role='ADMIN',
    first_name='Admin',
    last_name='Hospital'
)

# Create demo doctor
doctor_user = CustomUser.objects.create_user(
    username='doctor@hospital.com',
    email='doctor@hospital.com',
    password='doctor123',
    role='DOCTOR',
    first_name='John',
    last_name='Doe'
)
doctor = Doctor.objects.create(
    user=doctor_user,
    license_number='DOC123456',
    specialization='CARDIOLOGY',
    department=dept1,
    qualification='MD, Cardiology',
    experience_years=5
)

# Create demo nurse
nurse_user = CustomUser.objects.create_user(
    username='nurse@hospital.com',
    email='nurse@hospital.com',
    password='nurse123',
    role='NURSE',
    first_name='Jane',
    last_name='Smith'
)
Nurse.objects.create(
    user=nurse_user,
    license_number='NURSE123456',
    department=dept1,
    shift='MORNING',
    qualification='BSc Nursing',
    experience_years=3
)

# Create demo receptionist
receptionist_user = CustomUser.objects.create_user(
    username='reception@hospital.com',
    email='reception@hospital.com',
    password='reception123',
    role='RECEPTIONIST',
    first_name='Mike',
    last_name='Johnson'
)
Receptionist.objects.create(
    user=receptionist_user,
    employee_id='REC001',
    department=dept1
)

# Create demo patient
patient_user = CustomUser.objects.create_user(
    username='patient@hospital.com',
    email='patient@hospital.com',
    password='patient123',
    role='PATIENT',
    first_name='Robert',
    last_name='Wilson'
)
Patient.objects.create(
    user=patient_user,
    patient_id=f"PAT-{uuid.uuid4().hex[:8].upper()}",
    date_of_birth=date(1985, 5, 15),
    gender='M',
    blood_group='O+',
    emergency_contact='1234567890',
    emergency_contact_name='Sarah Wilson',
    assigned_doctor=doctor
)

exit()
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000**

## Access the System

### Role-Based Login Pages
- **Home:** http://127.0.0.1:8000
- **Role Selection:** http://127.0.0.1:8000/accounts/role-choice/
- **Admin Login:** http://127.0.0.1:8000/accounts/login/ADMIN/
- **Doctor Login:** http://127.0.0.1:8000/accounts/login/DOCTOR/
- **Nurse Login:** http://127.0.0.1:8000/accounts/login/NURSE/
- **Receptionist Login:** http://127.0.0.1:8000/accounts/login/RECEPTIONIST/
- **Patient Login:** http://127.0.0.1:8000/accounts/login/PATIENT/

### Admin Panel
- **Django Admin:** http://127.0.0.1:8000/admin/ (use superuser credentials)

### Demo Accounts
After running demo data creation:
- **Admin:** admin@hospital.com / admin123
- **Doctor:** doctor@hospital.com / doctor123
- **Nurse:** nurse@hospital.com / nurse123
- **Receptionist:** reception@hospital.com / reception123
- **Patient:** patient@hospital.com / patient123

## Key Features

### Administrator Features
- Dashboard with hospital statistics
- Manage patients, doctors, nurses, receptionists
- Assign doctors and nurses to patients
- View and manage departments
- View medical reports
- Hospital statistics and analytics

### Doctor Features
- View assigned patients
- Add diagnoses and medical reports
- Create prescriptions
- View appointments
- Update patient treatment notes
- Upload medical reports

### Nurse Features
- View assigned patients
- Record patient vitals (BP, pulse, temperature, oxygen level, weight)
- View vitals history
- Patient monitoring

### Receptionist Features
- Register new patients
- Book appointments
- View appointment schedule
- Search and check patient admission
- Update appointment status

### Patient Features
- View appointments
- View prescriptions
- Download medical reports
- View treatment history
- Update personal profile
- View vitals and medical information

## Project Structure

```
hospital_management_system/
├── manage.py
├── requirements.txt
├── db.sqlite3
│
├── hospital_management_system/
│   ├── __init__.py
│   ├── settings.py (Django configuration)
│   ├── urls.py (Main URL routing)
│   └── wsgi.py
│
├── accounts/
│   ├── models.py (Custom User, Doctor, Nurse, Patient models)
│   ├── views.py (Authentication, registration views)
│   ├── forms.py (User registration forms)
│   ├── urls.py
│   └── admin.py
│
├── dashboard/
│   ├── views.py (Dashboard views for each role)
│   ├── urls.py
│   └── ...
│
├── patients/
│   ├── views.py (Patient management)
│   ├── forms.py
│   ├── urls.py
│   └── ...
│
├── doctors/
│   ├── views.py (Doctor operations)
│   ├── forms.py (Diagnosis, prescription forms)
│   ├── urls.py
│   └── ...
│
├── nurses/
│   ├── views.py (Nurse vitals recording)
│   ├── forms.py (Vitals form)
│   ├── urls.py
│   └── ...
│
├── reception/
│   ├── views.py (Appointment and patient registration)
│   ├── forms.py
│   ├── urls.py
│   └── ...
│
├── reports/
│   ├── views.py (Medical reports and prescriptions)
│   ├── urls.py
│   └── ...
│
├── templates/
│   ├── base.html (Base template with navigation)
│   ├── home.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── role_choice.html
│   │   └── registration templates
│   ├── dashboard/
│   │   ├── admin_dashboard.html
│   │   ├── doctor_dashboard.html
│   │   ├── nurse_dashboard.html
│   │   ├── receptionist_dashboard.html
│   │   └── patient_dashboard.html
│   ├── patients/
│   ├── doctors/
│   ├── nurses/
│   ├── reception/
│   └── reports/
│
├── static/
│   ├── css/
│   └── js/
│
└── media/
    ├── profile_pictures/
    └── medical_reports/
```

## Models Overview

### CustomUser
- Extends Django's User model
- Includes role field (ADMIN, DOCTOR, NURSE, RECEPTIONIST, PATIENT)
- Profile information: phone, address, city, state, profile_picture

### Doctor
- License number, specialization, department
- Qualification, experience years
- Consultation fee, availability status

### Nurse
- License number, department, shift
- Qualification, experience years

### Receptionist
- Employee ID, department, shift

### Patient
- Patient ID, date of birth, gender, blood group
- Emergency contact information
- Medical history, allergies
- Assignment to doctor and nurse
- Admission status and dates

### Appointment
- Patient, doctor, appointment date/time
- Reason, status, consultation fee
- Created by (receptionist)

### MedicalReport
- Patient, doctor, diagnosis, treatment plan
- Vital signs, lab results, notes
- Report file attachment

### Vitals
- Patient, nurse recording
- Blood pressure, pulse rate, temperature
- Oxygen level, weight

### Prescription
- Patient, doctor, medicine details
- Dosage, frequency, duration

### Department
- Department name and code
- Head doctor assignment

## API Routes

### Accounts
- `/accounts/role-choice/` - Role selection
- `/accounts/login/<role>/` - Role-based login
- `/accounts/logout/` - Logout
- `/accounts/admin-register/` - Admin registration
- `/accounts/doctor-register/` - Doctor registration
- `/accounts/nurse-register/` - Nurse registration
- `/accounts/receptionist-register/` - Receptionist registration
- `/accounts/patient-register/` - Patient registration
- `/accounts/profile/` - View profile
- `/accounts/profile/edit/` - Edit profile

### Dashboard
- `/dashboard/admin/` - Admin dashboard
- `/dashboard/doctor/` - Doctor dashboard
- `/dashboard/nurse/` - Nurse dashboard
- `/dashboard/receptionist/` - Receptionist dashboard
- `/dashboard/patient/` - Patient dashboard

### Patients
- `/patients/list/` - All patients
- `/patients/<patient_id>/` - Patient details
- `/patients/<patient_id>/assign-doctor/` - Assign doctor/nurse
- `/patients/search/` - Search patients

### Doctors
- `/doctors/list/` - All doctors
- `/doctors/<doctor_id>/` - Doctor details
- `/doctors/appointments/` - Doctor's appointments
- `/doctors/patient/<patient_id>/diagnosis/` - Add diagnosis
- `/doctors/patient/<patient_id>/prescription/` - Add prescription
- `/doctors/patient/<patient_id>/report/` - Upload report

### Nurses
- `/nurses/list/` - All nurses
- `/nurses/<nurse_id>/` - Nurse details
- `/nurses/patients/` - Nurse's patients
- `/nurses/patient/<patient_id>/vitals/` - Record vitals
- `/nurses/patient/<patient_id>/vitals-history/` - Vitals history

### Reception
- `/reception/register-patient/` - Register patient
- `/reception/book-appointment/` - Book appointment
- `/reception/appointments/` - Appointments list
- `/reception/appointments/schedule/` - Appointment schedule
- `/reception/search-patient/` - Search patient

### Reports
- `/reports/medical-reports/` - All medical reports
- `/reports/patient/<patient_id>/reports/` - Patient's reports
- `/reports/prescriptions/` - Prescriptions
- `/reports/patient/<patient_id>/prescriptions/` - Patient's prescriptions

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Ensure all dependencies are installed: `pip install -r requirements.txt`

### Issue: Database errors
**Solution:** Run migrations: 
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: Static files not loading
**Solution:** Collect static files:
```bash
python manage.py collectstatic
```

### Issue: Port 8000 already in use
**Solution:** Use a different port:
```bash
python manage.py runserver 8001
```

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Update `ALLOWED_HOSTS` with your domain
3. Use a production database (PostgreSQL recommended)
4. Set up proper SECRET_KEY
5. Enable HTTPS
6. Use a production WSGI server (Gunicorn, uWSGI)
7. Set up email backend for notifications
8. Configure static files and media serving

## Notes

- The system uses SQLite by default. For production, use PostgreSQL or MySQL
- All passwords are hashed using Django's default password hasher
- File uploads (medical reports, profiles) are stored in `/media` directory
- Bootstrap 5 is used for responsive UI design
- Role-based access control is implemented using Django's authentication system

## Support & Documentation

For more information about Django, visit: https://docs.djangoproject.com/
For Bootstrap documentation: https://getbootstrap.com/docs/

## License

This project is provided as-is for educational purposes.
