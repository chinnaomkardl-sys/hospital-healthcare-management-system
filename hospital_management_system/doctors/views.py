from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from django.forms import formset_factory
from accounts.models import Doctor, Patient, MedicalReport, Prescription, Appointment, Department
from pharmacy.models import Prescription as PharmacyPrescription, PrescriptionItem
from .forms import MedicalReportForm, PrescriptionForm, DiagnosisForm, PharmacyPrescriptionItemForm


class AdminDoctorListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin view all doctors"""
    model = Doctor
    template_name = 'doctors/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role == 'ADMIN'
    
    def get_queryset(self):
        queryset = Doctor.objects.select_related('user', 'department')
        
        # Search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(license_number__icontains=search_query)
            )
        
        # Filter by specialization
        specialization = self.request.GET.get('specialization', '')
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        
        # Filter by availability
        availability = self.request.GET.get('availability', '')
        if availability == 'available':
            queryset = queryset.filter(is_available=True)
        elif availability == 'unavailable':
            queryset = queryset.filter(is_available=False)
        
        return queryset.order_by('user__first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['specialization'] = self.request.GET.get('specialization', '')
        context['availability'] = self.request.GET.get('availability', '')
        context['specializations'] = dict(Doctor.SPECIALIZATION_CHOICES)
        context['total_doctors'] = Doctor.objects.count()
        context['available_doctors'] = Doctor.objects.filter(is_available=True).count()
        return context


class DoctorDetailView(LoginRequiredMixin, DetailView):
    """View doctor details"""
    model = Doctor
    template_name = 'doctors/doctor_detail.html'
    context_object_name = 'doctor'
    slug_field = 'user__id'
    slug_url_kwarg = 'doctor_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = self.get_object()
        context['patients'] = doctor.patients.all()
        context['appointments'] = doctor.appointments.all().order_by('-appointment_date')[:10]
        context['total_patients'] = doctor.patients.count()
        context['completed_appointments'] = doctor.appointments.filter(status='COMPLETED').count()
        return context


class DoctorAddDiagnosisView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Doctor add diagnosis for patient"""
    model = MedicalReport
    form_class = DiagnosisForm
    template_name = 'doctors/add_diagnosis.html'
    
    def test_func(self):
        if self.request.user.role != 'DOCTOR':
            return False
        try:
            return Doctor.objects.filter(user=self.request.user).exists()
        except:
            return False
    
    def form_valid(self, form):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        form.instance.doctor = doctor
        patient_id = self.kwargs['patient_id']
        form.instance.patient = get_object_or_404(Patient, patient_id=patient_id)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs['patient_id']
        context['patient'] = get_object_or_404(Patient, patient_id=patient_id)
        return context
    
    def get_success_url(self):
        patient_id = self.kwargs['patient_id']
        return reverse_lazy('patients:patient_detail', kwargs={'patient_id': patient_id})


class DoctorPharmacyPrescriptionView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Doctor add pharmacy prescription for patient (tablets from inventory)"""
    template_name = 'doctors/add_prescription.html'
    
    def test_func(self):
        if self.request.user.role != 'DOCTOR':
            return False
        try:
            return Doctor.objects.filter(user=self.request.user).exists()
        except:
            return False
    
    def get(self, request, *args, **kwargs):
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, patient_id=patient_id)
        ItemFormSet = formset_factory(PharmacyPrescriptionItemForm, extra=2, can_delete=True)
        formset = ItemFormSet()
        return render(request, self.template_name, {
            'formset': formset,
            'patient': patient,
            'is_pharmacy': True,
        })
    
    def post(self, request, *args, **kwargs):
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, patient_id=patient_id)
        doctor = get_object_or_404(Doctor, user=request.user)
        ItemFormSet = formset_factory(PharmacyPrescriptionItemForm, extra=2, can_delete=True)
        formset = ItemFormSet(request.POST)
        
        if formset.is_valid():
            prescription = PharmacyPrescription.objects.create(
                patient=patient,
                doctor=doctor,
                notes=request.POST.get('notes', ''),
            )
            for item_form in formset:
                if item_form.is_valid() and item_form.cleaned_data:
                    PrescriptionItem.objects.create(
                        prescription=prescription,
                        medicine=item_form.cleaned_data['medicine'],
                        dosage=item_form.cleaned_data['dosage'],
                        frequency=item_form.cleaned_data['frequency'],
                        duration=item_form.cleaned_data['duration'],
                        prescribed_quantity=item_form.cleaned_data['prescribed_quantity'],
                        instructions=item_form.cleaned_data['instructions'],
                    )
            return redirect('patients:patient_detail', patient_id=patient_id)
        
        return render(request, self.template_name, {
            'formset': formset,
            'patient': patient,
            'is_pharmacy': True,
        })


class DoctorUploadMedicalReportView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Doctor upload medical report"""
    model = MedicalReport
    form_class = MedicalReportForm
    template_name = 'doctors/upload_report.html'
    
    def test_func(self):
        if self.request.user.role != 'DOCTOR':
            return False
        try:
            return Doctor.objects.filter(user=self.request.user).exists()
        except:
            return False
    
    def form_valid(self, form):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        form.instance.doctor = doctor
        patient_id = self.kwargs['patient_id']
        form.instance.patient = get_object_or_404(Patient, patient_id=patient_id)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs['patient_id']
        context['patient'] = get_object_or_404(Patient, patient_id=patient_id)
        return context
    
    def get_success_url(self):
        patient_id = self.kwargs['patient_id']
        return reverse_lazy('patients:patient_detail', kwargs={'patient_id': patient_id})


class DoctorViewAppointmentsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Doctor view appointments"""
    model = Appointment
    template_name = 'doctors/view_appointments.html'
    context_object_name = 'appointments'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role == 'DOCTOR'
    
    def get_queryset(self):
        doctor = self.request.user.doctor_profile
        queryset = doctor.appointments.select_related('patient__user')
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-appointment_date', '-appointment_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Appointment.STATUS_CHOICES
        context['status'] = self.request.GET.get('status', '')
        return context


class DoctorUpdateTreatmentNotesView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Doctor update treatment notes for a patient"""
    model = MedicalReport
    form_class = DiagnosisForm
    template_name = 'doctors/update_treatment_notes.html'
    pk_url_kwarg = 'report_id'
    
    def test_func(self):
        report = self.get_object()
        return self.request.user.role == 'DOCTOR' and self.request.user == report.doctor.user
    
    def get_success_url(self):
        patient_id = self.object.patient.patient_id
        return reverse_lazy('patients:patient_detail', kwargs={'patient_id': patient_id})
