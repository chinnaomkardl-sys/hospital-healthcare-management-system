# Hospital Healthcare Management System

A comprehensive, fully functional Django-based Hospital Healthcare Management System designed for real hospital environments. This system includes role-based authentication, patient management, appointment scheduling, medical records, and more.

## 🏥 Overview

This is a production-ready hospital management system with a modern UI built using Bootstrap 5. It supports multiple roles with role-specific dashboards, features, and permissions.

## ✨ Key Features

### 🔐 Role-Based Access Control
- **Administrator**: Full hospital management
- **Doctor**: Patient care and medical records
- **Nurse**: Patient vitals and monitoring
- **Receptionist**: Patient registration and appointments
- **Patient**: Medical records access and appointment booking

### 📋 Core Features
- Custom user authentication with role-based login
- Patient registration and medical history management
- Doctor assignment and workload management
- Appointment scheduling and management
- Medical report generation and storage
- Prescription management
- Patient vitals monitoring (BP, pulse, temperature, oxygen, weight)
- Department management
- Hospital statistics and analytics
- Professional dashboard for each role

### 💾 Data Management
- Comprehensive patient profiles
- Medical history tracking
- Appointment history
- Prescription records
- Medical reports with file uploads
- Vitals recording and trending

## 🛠 Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, jQuery
- **Authentication**: Django built-in authentication with custom User model
- **File Storage**: Django FileField for medical reports

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Quick Start

1. **Clone/Extract Project**
```bash
cd hospital_management_system
```

2. **Create Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create Superuser**
```bash
python manage.py createsuperuser
```

6. **Run Development Server**
```bash
python manage.py runserver
```

7. **Access the Application**
- Home: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin
- Role Selection: http://127.0.0.1:8000/accounts/role-choice

## 📚 Project Structure

```
hospital_management_system/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── SETUP_GUIDE.md
├── README.md
│
├── hospital_management_system/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/
│   ├── models.py (Custom User, Doctor, Nurse, Patient)
│   ├── views.py (Authentication)
│   ├── forms.py
│   └── urls.py
│
├── dashboard/
│   ├── views.py (Role dashboards)
│   └── urls.py
│
├── patients/
│   ├── views.py (Patient management)
│   └── urls.py
│
├── doctors/
│   ├── views.py (Doctor operations)
│   └── urls.py
│
├── nurses/
│   ├── views.py (Nurse vitals recording)
│   └── urls.py
│
├── reception/
│   ├── views.py (Appointments, registration)
│   └── urls.py
│
├── reports/
│   ├── views.py (Medical reports)
│   └── urls.py
│
└── templates/
    ├── base.html
    ├── home.html
    ├── accounts/
    ├── dashboard/
    ├── patients/
    ├── doctors/
    ├── nurses/
    ├── reception/
    └── reports/
```

## 🔐 Default Demo Accounts

After creating superuser and demo data:
```
Admin:       admin@hospital.com / admin123
Doctor:      doctor@hospital.com / doctor123
Nurse:       nurse@hospital.com / nurse123
Reception:   reception@hospital.com / reception123
Patient:     patient@hospital.com / patient123
```

## 📊 Database Models

### Core Models
- **CustomUser**: Extended Django User with role field
- **Doctor**: Doctor profile with specialization and credentials
- **Nurse**: Nurse profile with shift and qualifications
- **Receptionist**: Reception staff profile
- **Patient**: Patient profile with medical details
- **Department**: Hospital departments
- **Appointment**: Appointment scheduling
- **MedicalReport**: Medical records and reports
- **Prescription**: Medicine prescriptions
- **Vitals**: Patient vital signs monitoring

## 🚀 Features by Role

### Administrator
- Real-time hospital statistics dashboard
- Patient management (CRUD)
- Doctor and nurse management
- Department management
- Staff assignment to patients
- Medical report access
- Analytics and reporting

### Doctor
- View assigned patients
- Add diagnoses and treatment plans
- Create prescriptions
- Upload medical reports
- View appointment schedule
- Update patient notes

### Nurse
- View assigned patients
- Record patient vitals
- Monitor patient health metrics
- View vital sign history
- Patient charts

### Receptionist
- Register new patients
- Book appointments
- View appointment schedule
- Manage appointment status
- Search patient records
- Check patient admission status

### Patient
- View upcoming appointments
- View medical history
- Access prescriptions
- Download medical reports
- View recorded vitals
- Update personal profile

## 🔗 URL Routing

| Endpoint | Purpose |
|----------|---------|
| `/` | Home page |
| `/accounts/role-choice/` | Role selection |
| `/accounts/login/<role>/` | Login pages |
| `/dashboard/<role>/` | Role dashboards |
| `/patients/` | Patient management |
| `/doctors/` | Doctor management |
| `/nurses/` | Nurse management |
| `/reception/` | Reception operations |
| `/reports/` | Medical reports |

## 🎨 UI/UX Highlights

- Responsive Bootstrap 5 design
- Role-specific navigation menus
- Clean and intuitive interface
- Smooth transitions and animations
- Organized dashboards with statistics
- Mobile-friendly layout

## 🔒 Security Features

- CSRF protection
- Password hashing
- Session-based authentication
- Role-based access control (RBAC)
- Input validation and sanitization
- Secure file uploads

## 📝 Additional Configuration

### Email Setup (Optional)
Configure email backend in settings.py for notifications:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-email-host'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### Database Configuration
Update DATABASES in settings.py for PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hospital_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🚀 Deployment

For production deployment:
1. Set `DEBUG = False`
2. Update `ALLOWED_HOSTS`
3. Use PostgreSQL or MySQL
4. Collect static files: `python manage.py collectstatic`
5. Use Gunicorn or uWSGI
6. Configure HTTPS with SSL
7. Set up proper logging

## 📖 Documentation

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 🐛 Troubleshooting

### Issue: Port already in use
```bash
python manage.py runserver 8001
```

### Issue: Database errors
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: Missing dependencies
```bash
pip install -r requirements.txt
```

## 📞 Support

For Django documentation: https://docs.djangoproject.com/
For Bootstrap: https://getbootstrap.com/

## 📄 License

This project is provided for educational purposes.

## 🎯 Future Enhancements

- Email notifications for appointments
- SMS reminders
- Advanced analytics
- Billing and payment integration
- Telemedicine features
- Mobile app
- API (REST/GraphQL)
- Multi-language support
- Advanced reporting

---

**Created**: 2024  
**Version**: 1.0  
**Status**: Production Ready
