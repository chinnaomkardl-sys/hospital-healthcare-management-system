from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import datetime, timedelta
from accounts.models import Patient, Doctor, Appointment, Department, CustomUser
from .forms import AppointmentForm, AppointmentSearchForm
import uuid


def get_next_available_doctor(specialization=None, exclude_doctor=None):
    """
    Find the next available doctor for automatic assignment.
    Returns an available doctor or None if no doctor is available.
    """
    # Get all available doctors
    doctors = Doctor.objects.filter(is_available=True)
    
    # Filter by specialization if provided
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    
    # Exclude the current doctor if provided
    if exclude_doctor:
        doctors = doctors.exclude(id=exclude_doctor.id)
    
    # Order by least number of appointments today
    today = datetime.now().date()
    doctors = sorted(doctors, key=lambda d: d.appointments.filter(
        appointment_date=today, 
        status__in=['SCHEDULED', 'COMPLETED']
    ).count())
    
    return doctors[0] if doctors else None


class ReceptionRegisterPatientView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Reception register new patient"""
    model = Patient
    template_name = 'reception/register_patient.html'
    fields = ('date_of_birth', 'gender', 'blood_group', 'emergency_contact', 
              'emergency_contact_name', 'allergies', 'medical_history')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'RECEPTIONIST']
    
    def post(self, request, *args, **kwargs):
        # Get user data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        # Create user
        # Basic validation
        if not email:
            messages.error(request, 'Email is required')
            return self.get(request)

        if password != request.POST.get('password_confirm'):
            messages.error(request, 'Passwords do not match')
            return self.get(request)

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'A user with that email already exists')
            return self.get(request)

        try:
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                first_name=first_name or '',
                last_name=last_name or '',
                phone=phone or '',
                password=password,
                role='PATIENT'
            )

            # Create patient
            patient = Patient()
            patient.user = user
            patient.patient_id = f"PAT-{uuid.uuid4().hex[:8].upper()}"
            patient.date_of_birth = request.POST.get('date_of_birth')
            patient.gender = request.POST.get('gender')
            patient.blood_group = request.POST.get('blood_group')
            patient.emergency_contact = request.POST.get('emergency_contact')
            patient.emergency_contact_name = request.POST.get('emergency_contact_name')
            patient.allergies = request.POST.get('allergies')
            patient.medical_history = request.POST.get('medical_history')
            patient.save()

            return redirect('reception:patient_registered', patient_id=patient.patient_id)
        except Exception as e:
            messages.error(request, f'Registration error: {e}')
            return self.get(request)
    
    def get_success_url(self):
        return reverse_lazy('reception:appointment_list')


class PatientRegisteredView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Show patient registered confirmation"""
    model = Patient
    template_name = 'reception/patient_registered.html'
    context_object_name = 'patient'
    slug_field = 'patient_id'
    slug_url_kwarg = 'patient_id'
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'RECEPTIONIST']


class ReceptionBookAppointmentView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Reception book appointment"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'reception/book_appointment.html'
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'RECEPTIONIST']
    
    def form_valid(self, form):
        selected_doctor = form.cleaned_data['doctor']
        appointment_date = form.cleaned_data['appointment_date']
        appointment_time = form.cleaned_data['appointment_time']
        
        # Check if auto_assign is enabled
        auto_assign = form.cleaned_data.get('auto_assign', True)
        
        # Check if selected doctor has appointments at the same time
        if auto_assign and selected_doctor:
            existing_appointment = Appointment.objects.filter(
                doctor=selected_doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['SCHEDULED', 'COMPLETED']
            ).exists()
            
            if existing_appointment:
                # Find next available doctor
                new_doctor = get_next_available_doctor(
                    specialization=selected_doctor.specialization,
                    exclude_doctor=selected_doctor
                )
                
                if new_doctor:
                    form.instance.doctor = new_doctor
                    messages.info(
                        self.request, 
                        f'Dr. {selected_doctor.user.get_full_name()} is busy at this time. '
                        f'Appointment has been assigned to Dr. {new_doctor.user.get_full_name()}.'
                    )
                else:
                    messages.warning(
                        self.request,
                        f'No available doctor found for the same specialization. '
                        f'Keeping the appointment with Dr. {selected_doctor.user.get_full_name()}.'
                    )
        
        form.instance.appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
        form.instance.created_by = self.request.user
        form.instance.consultation_fee = form.cleaned_data['doctor'].consultation_fee
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Book Appointment'
        return context
    
    def get_success_url(self):
        return reverse_lazy('reception:appointment_confirmed', 
                          kwargs={'appointment_id': self.object.appointment_id})


class AppointmentConfirmedView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Show appointment confirmed"""
    model = Appointment
    template_name = 'reception/appointment_confirmed.html'
    context_object_name = 'appointment'
    slug_field = 'appointment_id'
    slug_url_kwarg = 'appointment_id'
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'RECEPTIONIST']


class ReceptionViewAppointmentScheduleView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Reception view appointment schedule"""
    model = Appointment
    template_name = 'reception/appointment_schedule.html'
    context_object_name = 'appointments'
    paginate_by = 30
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'RECEPTIONIST']
    
    def get_queryset(self):
        queryset = Appointment.objects.select_related('patient__user', 'doctor__user')
        
        # Filter by date
        date_filter = self.request.GET.get('date', '')
        if date_filter:
            queryset = queryset.filter(appointment_date=date_filter)
        else:
            # Default to today
            queryset = queryset.filter(appointment_date=datetime.now().date())
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by doctor
        doctor = self.request.GET.get('doctor', '')
        if doctor:
            queryset = queryset.filter(doctor__id=doctor)
        
        return queryset.order_by('appointment_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_filter'] = self.request.GET.get('date', datetime.now().date())
        context['status'] = self.request.GET.get('status', '')
        context['doctor'] = self.request.GET.get('doctor', '')
        context['doctors'] = Doctor.objects.all()
        context['statuses'] = Appointment.STATUS_CHOICES
        return context


class ReceptionSearchPatientView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Reception search patient admission"""
    model = Patient
    template_name = 'reception/search_patient.html'
    context_object_name = 'patients'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'RECEPTIONIST']
    
    def get_queryset(self):
        queryset = Patient.objects.select_related('user', 'assigned_doctor')
        
        search_query = self.request.GET.get('q', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(patient_id__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ReceptionUpdateAppointmentStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Reception update appointment status"""
    model = Appointment
    fields = ['status', 'notes']
    template_name = 'reception/update_appointment.html'
    slug_field = 'appointment_id'
    slug_url_kwarg = 'appointment_id'
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'RECEPTIONIST']
    
    def get_success_url(self):
        return reverse_lazy('reception:appointment_list')


class ReceptionAppointmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Reception view all appointments"""
    model = Appointment
    template_name = 'reception/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 30
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'RECEPTIONIST']
    
    def get_queryset(self):
        queryset = Appointment.objects.select_related('patient__user', 'doctor__user')
        
        # Filter by date range
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        
        if start_date:
            queryset = queryset.filter(appointment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(appointment_date__lte=end_date)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-appointment_date', '-appointment_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['status'] = self.request.GET.get('status', '')
        context['statuses'] = Appointment.STATUS_CHOICES
        return context
