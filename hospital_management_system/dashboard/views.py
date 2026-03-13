from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from accounts.models import Patient, Doctor, Nurse, Appointment, Department
from datetime import datetime, timedelta


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to check if user has required role"""
    required_role = None
    
    def test_func(self):
        return self.request.user.role == self.required_role
    
    def handle_no_permission(self):
        return redirect('home')


class AdminDashboardView(RoleRequiredMixin, TemplateView):
    """Admin Dashboard"""
    template_name = 'dashboard/admin_dashboard.html'
    required_role = 'ADMIN'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_patients'] = Patient.objects.count()
        context['total_doctors'] = Doctor.objects.count()
        context['total_nurses'] = Nurse.objects.count()
        context['total_appointments'] = Appointment.objects.count()
        context['total_departments'] = Department.objects.count()
        
        # Recent admissions
        context['recent_admissions'] = Patient.objects.filter(
            admission_status='ADMITTED'
        ).order_by('-admission_date')[:5]
        
        # Recent appointments
        context['recent_appointments'] = Appointment.objects.filter(
            status='SCHEDULED',
            appointment_date__gte=datetime.now().date()
        ).order_by('appointment_date', 'appointment_time')[:5]
        
        # Upcoming appointments (next 7 days)
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        context['upcoming_appointments'] = Appointment.objects.filter(
            status='SCHEDULED',
            appointment_date__range=[today, next_week]
        ).count()
        
        return context


class DoctorDashboardView(RoleRequiredMixin, TemplateView):
    """Doctor Dashboard"""
    template_name = 'dashboard/doctor_dashboard.html'
    required_role = 'DOCTOR'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Safely get doctor profile; don't rely on attribute access which can raise
        doctor = None
        try:
            doctor = getattr(self.request.user, 'doctor_profile', None)
        except Exception:
            doctor = None

        if not doctor:
            # Try fallback lookup
            doctor = Doctor.objects.filter(user=self.request.user).first()

        if doctor:
            context['doctor'] = doctor
            context['assigned_patients'] = doctor.patients.all()
            context['total_patients'] = doctor.patients.count()

            # Today's appointments
            today = datetime.now().date()
            context['todays_appointments'] = doctor.appointments.filter(
                appointment_date=today,
                status__in=['SCHEDULED', 'COMPLETED']
            ).order_by('appointment_time')

            # Upcoming appointments (next 7 days)
            next_week = today + timedelta(days=7)
            context['upcoming_appointments'] = doctor.appointments.filter(
                appointment_date__range=[today, next_week],
                status='SCHEDULED'
            ).order_by('appointment_date', 'appointment_time')[:5]
        else:
            # Ensure keys exist for template rendering
            context['doctor'] = None
            context['assigned_patients'] = []
            context['total_patients'] = 0
            context['todays_appointments'] = []
            context['upcoming_appointments'] = []
        
        return context


class NurseDashboardView(RoleRequiredMixin, TemplateView):
    """Nurse Dashboard"""
    template_name = 'dashboard/nurse_dashboard.html'
    required_role = 'NURSE'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        nurse = None
        try:
            nurse = self.request.user.nurse_profile
            context['nurse'] = nurse
            context['assigned_patients'] = nurse.patients.all()
            context['total_patients'] = nurse.patients.count()
            
            # Get appointments for assigned patients
            from datetime import datetime
            today = datetime.now().date()
            patient_ids = nurse.patients.values_list('id', flat=True)
            
            # Today's appointments for assigned patients
            context['todays_appointments'] = Appointment.objects.filter(
                patient_id__in=patient_ids,
                appointment_date=today,
                status='SCHEDULED'
            ).select_related('patient__user', 'doctor__user')
            
            # All upcoming appointments
            context['upcoming_appointments'] = Appointment.objects.filter(
                patient_id__in=patient_ids,
                appointment_date__gte=today,
                status='SCHEDULED'
            ).select_related('patient__user', 'doctor__user').order_by('appointment_date', 'appointment_time')[:10]
            
        except:
            pass
        
        # Get list of unavailable nurses (not working)
        context['unavailable_nurses'] = Nurse.objects.filter(
            is_available=False
        ).select_related('user', 'department')
        
        return context


class ReceptionistDashboardView(RoleRequiredMixin, TemplateView):
    """Receptionist Dashboard"""
    template_name = 'dashboard/receptionist_dashboard.html'
    required_role = 'RECEPTIONIST'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Today's appointments
        today = datetime.now().date()
        context['todays_appointments'] = Appointment.objects.filter(
            appointment_date=today
        ).order_by('appointment_time')
        
        # Recent patients
        context['recent_patients'] = Patient.objects.order_by('-created_at')[:10]
        
        # Available doctors
        context['available_doctors'] = Doctor.objects.filter(is_available=True)
        
        return context


class PatientDashboardView(RoleRequiredMixin, TemplateView):
    """Patient Dashboard"""
    template_name = 'dashboard/patient_dashboard.html'
    required_role = 'PATIENT'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            patient = self.request.user.patient_profile
            context['patient'] = patient
            
            # Patient appointments
            context['upcoming_appointments'] = patient.appointments.filter(
                status__in=['SCHEDULED'],
                appointment_date__gte=datetime.now().date()
            ).order_by('appointment_date', 'appointment_time')
            
            context['past_appointments'] = patient.appointments.filter(
                status__in=['COMPLETED', 'NO_SHOW']
            ).order_by('-appointment_date')[:5]
            
            # Medical reports
            context['recent_reports'] = patient.medical_reports.all().order_by('-report_date')[:5]
            
            # Prescriptions
            context['recent_prescriptions'] = patient.prescriptions.all().order_by('-prescribed_at')[:5]
            
            # Vitals
            context['recent_vitals'] = patient.vitals.all().order_by('-recorded_at')[:5]
            
        except:
            pass
        
        return context
