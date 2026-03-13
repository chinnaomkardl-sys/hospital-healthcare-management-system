from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from accounts.models import Patient, Doctor, Department, CustomUser, Appointment, PrescriptionRefill, Teleconsultation
from .forms import PatientFiltersForm, AssignDoctorForm
from datetime import date
import uuid


class AdminPatientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin view all patients"""
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role == 'ADMIN'
    
    def get_queryset(self):
        queryset = Patient.objects.select_related('user', 'assigned_doctor', 'assigned_nurse')
        
        # Search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(patient_id__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(admission_status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['statuses'] = Patient.STATUS_CHOICES
        return context


class PatientDetailView(LoginRequiredMixin, DetailView):
    """View patient details"""
    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'
    slug_field = 'patient_id'
    slug_url_kwarg = 'patient_id'
    
    def get_queryset(self):
        return Patient.objects.select_related('user', 'assigned_doctor__user', 'assigned_nurse__user')
    
    def test_func(self):
        patient = self.get_object()
        return (
            self.request.user.role == 'ADMIN' or
            self.request.user.role == 'RECEPTIONIST' or
            self.request.user == patient.user or
            (self.request.user.role == 'DOCTOR' and patient.assigned_doctor and self.request.user == patient.assigned_doctor.user) or
            (self.request.user.role == 'NURSE' and patient.assigned_nurse and self.request.user == patient.assigned_nurse.user)
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        context['appointments'] = patient.appointments.all().order_by('-appointment_date')
        context['medical_reports'] = patient.medical_reports.all().order_by('-report_date')
        context['prescriptions'] = patient.prescriptions.all().order_by('-prescribed_at')
        context['vitals'] = patient.vitals.all().order_by('-recorded_at')
        return context


class AdminAssignDoctorView(LoginRequiredMixin, UpdateView):
    """Assign doctor to patient"""
    model = Patient
    template_name = 'patients/assign_doctor.html'
    form_class = AssignDoctorForm
    
    # Allow any authenticated user to access this page
    # The form will show appropriate options based on context
    
    def get_object(self):
        return get_object_or_404(Patient, patient_id=self.kwargs['patient_id'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        context['patient'] = patient
        return context
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        patient = self.get_object()
        return reverse_lazy('patients:patient_detail', kwargs={'patient_id': patient.patient_id})


class AdminSearchPatientView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Search patients"""
    model = Patient
    template_name = 'patients/search_patients.html'
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


class PatientBookAppointmentView(LoginRequiredMixin, CreateView):
    """Patient can book their own appointment"""
    model = Appointment
    template_name = 'patients/book_appointment.html'
    fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']
    
    def test_func(self):
        return self.request.user.role == 'PATIENT'
    
    def get(self, request, *args, **kwargs):
        # Check if patient profile exists
        try:
            patient = request.user.patient_profile
        except Patient.DoesNotExist:
            from django.contrib import messages
            messages.error(request, 'Please complete your patient registration first.')
            return redirect('dashboard:patient_dashboard')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get available doctors
        available_doctors = Doctor.objects.filter(is_available=True).select_related('user', 'department')
        context['available_doctors'] = available_doctors
        
        # Get today's available doctors
        today = date.today()
        today_appointments = Appointment.objects.filter(
            appointment_date=today,
            status='SCHEDULED'
        ).values_list('doctor_id', 'appointment_time')
        
        available_doctors_today = []
        for doctor in available_doctors:
            # Check if doctor has any appointments today
            has_appointment_today = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=today,
                status='SCHEDULED'
            ).exists()
            if not has_appointment_today:
                available_doctors_today.append(doctor)
        
        context['available_doctors_today'] = available_doctors_today[:5]
        
        return context
    
    def form_valid(self, form):
        # Get the patient profile
        patient = self.request.user.patient_profile
        form.instance.patient = patient
        form.instance.appointment_id = uuid.uuid4().hex[:8].upper()
        form.instance.status = 'SCHEDULED'
        form.instance.created_by = self.request.user
        
        # Set consultation fee from doctor
        doctor = form.cleaned_data['doctor']
        form.instance.consultation_fee = doctor.consultation_fee
        
        # Save the appointment
        response = super().form_valid(form)
        
        from django.contrib import messages
        messages.success(self.request, 'Appointment booked successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('patients:appointment_confirmed', kwargs={'appointment_id': self.object.appointment_id})


class PatientAppointmentConfirmedView(LoginRequiredMixin, DetailView):
    """Show appointment confirmation to patient"""
    model = Appointment
    template_name = 'patients/appointment_confirmed.html'
    context_object_name = 'appointment'
    
    def test_func(self):
        appointment = self.get_object()
        return self.request.user == appointment.patient.user
    
    def get_object(self):
        return get_object_or_404(Appointment, appointment_id=self.kwargs['appointment_id'])


class PatientPrescriptionRefillView(LoginRequiredMixin, CreateView):
    """Patient can request prescription refill"""
    model = PrescriptionRefill
    template_name = 'patients/prescription_refill.html'
    fields = ['prescription', 'notes']
    
    def test_func(self):
        return self.request.user.role == 'PATIENT'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.request.user.patient_profile
        # Get patient's prescriptions
        context['prescriptions'] = patient.prescriptions.all()
        return context
    
    def form_valid(self, form):
        patient = self.request.user.patient_profile
        form.instance.patient = patient
        response = super().form_valid(form)
        from django.contrib import messages
        messages.success(self.request, 'Prescription refill request submitted successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('dashboard:patient_dashboard')


class PatientBillingListView(LoginRequiredMixin, ListView):
    """Patient can view their bills"""
    model = None
    template_name = 'patients/patient_bills.html'
    context_object_name = 'bills'
    
    def test_func(self):
        return self.request.user.role == 'PATIENT'
    
    def get_queryset(self):
        from billing.models import Billing
        patient = self.request.user.patient_profile
        return Billing.objects.filter(patient=patient).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.request.user.patient_profile
        from billing.models import Billing
        context['pending_bills'] = Billing.objects.filter(patient=patient, status='PENDING')
        context['paid_bills'] = Billing.objects.filter(patient=patient, status='PAID')
        return context


class PatientMakePaymentView(LoginRequiredMixin, CreateView):
    """Patient can make payment for bills"""
    from billing.models import Payment
    model = Payment
    template_name = 'patients/make_payment.html'
    fields = ['amount', 'payment_method', 'notes']
    
    def test_func(self):
        return self.request.user.role == 'PATIENT'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from billing.models import Billing
        billing_id = self.kwargs.get('billing_id')
        context['billing'] = get_object_or_404(Billing, billing_id=billing_id)
        return context
    
    def form_valid(self, form):
        from billing.models import Billing
        billing_id = self.kwargs.get('billing_id')
        billing = get_object_or_404(Billing, billing_id=billing_id)
        form.instance.billing = billing
        response = super().form_valid(form)
        
        # Update billing amount paid
        billing.amount_paid += form.cleaned_data['amount']
        billing.save()
        
        from django.contrib import messages
        messages.success(self.request, 'Payment successful!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('patients:patient_bills')


class PatientTeleconsultationView(LoginRequiredMixin, CreateView):
    """Patient can request teleconsultation"""
    model = Teleconsultation
    template_name = 'patients/request_teleconsultation.html'
    fields = ['doctor', 'scheduled_date', 'scheduled_time', 'notes']
    
    def test_func(self):
        return self.request.user.role == 'PATIENT'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctors'] = Doctor.objects.filter(is_available=True)
        return context
    
    def form_valid(self, form):
        patient = self.request.user.patient_profile
        form.instance.patient = patient
        # Generate meeting link (in real app, integrate with video service)
        form.instance.meeting_link = f"https://meet.hospital.com/{uuid.uuid4().hex[:12]}"
        response = super().form_valid(form)
        
        from django.contrib import messages
        messages.success(self.request, 'Teleconsultation request submitted! You will receive a meeting link.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('dashboard:patient_dashboard')


class PatientTeleconsultationListView(LoginRequiredMixin, ListView):
    """Patient can view their teleconsultations"""
    model = Teleconsultation
    template_name = 'patients/teleconsultation_list.html'
    context_object_name = 'teleconsultations'
    
    def test_func(self):
        return self.request.user.role == 'PATIENT'
    
    def get_queryset(self):
        patient = self.request.user.patient_profile
        return Teleconsultation.objects.filter(patient=patient).order_by('-scheduled_date', '-scheduled_time')
