from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    """Custom user model with role-based authentication"""
    
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('DOCTOR', 'Doctor'),
        ('NURSE', 'Nurse'),
        ('PHARMACIST', 'Pharmacist'),
        ('RECEPTIONIST', 'Receptionist'),
        ('PATIENT', 'Patient'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PATIENT')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active_user = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_role_display_lower(self):
        """Return role in lowercase"""
        return self.role.lower()


class Department(models.Model):
    """Hospital Departments"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    head_doctor = models.OneToOneField('accounts.Doctor', on_delete=models.SET_NULL, 
                                       null=True, blank=True, related_name='department_head')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Departments"
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Doctor(models.Model):
    """Doctor Model"""
    
    SPECIALIZATION_CHOICES = (
        ('CARDIOLOGY', 'Cardiology'),
        ('NEUROLOGY', 'Neurology'),
        ('ORTHOPEDICS', 'Orthopedics'),
        ('PEDIATRICS', 'Pediatrics'),
        ('GENERAL', 'General Medicine'),
        ('SURGERY', 'Surgery'),
        ('PSYCHIATRY', 'Psychiatry'),
        ('DERMATOLOGY', 'Dermatology'),
        ('PATHOLOGY', 'Pathology'),
        ('RADIOLOGY', 'Radiology'),
        ('OTHER', 'Other'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='doctors')
    qualification = models.CharField(max_length=100)
    experience_years = models.IntegerField(validators=[MinValueValidator(0)])
    availability_start = models.TimeField(default='09:00')
    availability_end = models.TimeField(default='17:00')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    is_available = models.BooleanField(default=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name']
        indexes = [
            models.Index(fields=['specialization']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class Nurse(models.Model):
    """Nurse Model"""
    
    SHIFT_CHOICES = (
        ('MORNING', 'Morning (6 AM - 2 PM)'),
        ('AFTERNOON', 'Afternoon (2 PM - 10 PM)'),
        ('NIGHT', 'Night (10 PM - 6 AM)'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='nurse_profile')
    license_number = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='nurses')
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='MORNING')
    qualification = models.CharField(max_length=100)
    experience_years = models.IntegerField(validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name']
    
    def __str__(self):
        return f"Nurse {self.user.get_full_name()}"


class Receptionist(models.Model):
    """Receptionist Model"""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='receptionist_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='receptionists')
    shift = models.CharField(max_length=20, default='MORNING')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name']
    
    def __str__(self):
        return f"Receptionist {self.user.get_full_name()}"

class Pharmacist(models.Model):
    """Pharmacist Model"""
    
    SHIFT_CHOICES = (
        ('MORNING', 'Morning (6 AM - 2 PM)'),
        ('AFTERNOON', 'Afternoon (2 PM - 10 PM)'),
        ('NIGHT', 'Night (10 PM - 6 AM)'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='pharmacist_profile')
    license_number = models.CharField(max_length=50, unique=True)
    qualification = models.CharField(max_length=100)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='MORNING')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name']
    
    def __str__(self):
        return f"Pharmacist {self.user.get_full_name()}"


class Patient(models.Model):
    """Patient Model"""
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('ADMITTED', 'Admitted'),
        ('DISCHARGED', 'Discharged'),
        ('OUTPATIENT', 'Outpatient'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    patient_id = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20)
    emergency_contact_name = models.CharField(max_length=100)
    allergies = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, 
                                        related_name='patients')
    assigned_nurse = models.ForeignKey(Nurse, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='patients')
    admission_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OUTPATIENT')
    admission_date = models.DateTimeField(null=True, blank=True)
    discharge_date = models.DateTimeField(null=True, blank=True)
    discharge_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['admission_status']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.patient_id})"
    
    @property
    def age(self):
        """Calculate patient age"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class Appointment(models.Model):
    """Appointment Model"""
    
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    )
    
    appointment_id = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, 
                                   related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['appointment_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"APT-{self.appointment_id} | {self.patient.user.get_full_name()} - Dr. {self.doctor.user.get_full_name()}"


class Vitals(models.Model):
    """Patient Vitals Model"""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals')
    nurse = models.ForeignKey(Nurse, on_delete=models.SET_NULL, null=True, related_name='vitals_recorded')
    blood_pressure = models.CharField(max_length=10)  # e.g., "120/80"
    pulse_rate = models.IntegerField(validators=[MinValueValidator(30), MaxValueValidator(200)])  # BPM
    temperature = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(90), MaxValueValidator(115)])  # Fahrenheit
    oxygen_level = models.IntegerField(validators=[MinValueValidator(70), MaxValueValidator(100)])  # SpO2 percentage
    weight = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(10)])  # kg
    notes = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        verbose_name_plural = "Vitals"
        indexes = [
            models.Index(fields=['-recorded_at']),
        ]
    
    def __str__(self):
        return f"Vitals - {self.patient.user.get_full_name()} ({self.recorded_at.strftime('%Y-%m-%d %H:%M')})"


class Prescription(models.Model):
    """Prescription Model"""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)  # e.g., "500mg"
    frequency = models.CharField(max_length=50)  # e.g., "3 times a day"
    duration = models.CharField(max_length=50)  # e.g., "10 days"
    instructions = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    prescribed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-prescribed_at']
    
    def __str__(self):
        return f"{self.medicine_name} - {self.patient.user.get_full_name()}"


class MedicalReport(models.Model):
    """Medical Report Model"""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_reports')
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    blood_pressure = models.CharField(max_length=10, blank=True, null=True)
    heart_rate = models.IntegerField(blank=True, null=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    lab_results = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    report_file = models.FileField(upload_to='medical_reports/', blank=True, null=True)
    report_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-report_date']
        indexes = [
            models.Index(fields=['-report_date']),
        ]
    
    def __str__(self):
        return f"Report - {self.patient.user.get_full_name()} ({self.report_date.strftime('%Y-%m-%d')})"


class PrescriptionRefill(models.Model):
    """Prescription Refill Request Model"""
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    )
    
    refill_id = models.CharField(max_length=50, unique=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='refill_requests')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescription_refills')
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='refill_reviews')
    reviewed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"REFILL-{self.refill_id} - {self.prescription.medicine_name}"
    
    def save(self, *args, **kwargs):
        if not self.refill_id:
            import uuid
            self.refill_id = f"REF-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class Teleconsultation(models.Model):
    """Teleconsultation/Video Call Model"""
    
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    )
    
    consultation_id = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='teleconsultations')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='teleconsultations')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='teleconsultations')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    meeting_link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']
    
    def __str__(self):
        return f"TELE-{self.consultation_id} - {self.patient.user.get_full_name()} with Dr. {self.doctor.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.consultation_id:
            import uuid
            self.consultation_id = f"TELE-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
