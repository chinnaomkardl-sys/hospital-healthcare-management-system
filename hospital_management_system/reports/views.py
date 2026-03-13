from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.http import FileResponse
from accounts.models import MedicalReport, Patient, Prescription


class AdminMedicalReportListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin view all medical reports"""
    model = MedicalReport
    template_name = 'reports/medical_report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role == 'ADMIN'
    
    def get_queryset(self):
        queryset = MedicalReport.objects.select_related('patient__user', 'doctor__user')
        
        # Search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(patient__user__first_name__icontains=search_query) |
                Q(patient__user__last_name__icontains=search_query) |
                Q(patient__patient_id__icontains=search_query) |
                Q(doctor__user__first_name__icontains=search_query)
            )
        
        # Filter by date range
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        
        if start_date:
            queryset = queryset.filter(report_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(report_date__lte=end_date)
        
        return queryset.order_by('-report_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        return context


class PatientMedicalReportListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Patient view their medical reports"""
    model = MedicalReport
    template_name = 'reports/patient_reports.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def test_func(self):
        patient = get_object_or_404(Patient, patient_id=self.kwargs['patient_id'])
        return (
            self.request.user.role == 'PATIENT' and self.request.user == patient.user
        ) or self.request.user.role == 'ADMIN'
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, patient_id=patient_id)
        return patient.medical_reports.select_related('doctor__user').order_by('-report_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs['patient_id']
        context['patient'] = get_object_or_404(Patient, patient_id=patient_id)
        return context


class MedicalReportDetailView(LoginRequiredMixin, DetailView):
    """View medical report details"""
    model = MedicalReport
    template_name = 'reports/medical_report_detail.html'
    context_object_name = 'report'
    pk_url_kwarg = 'report_id'
    
    def test_func(self):
        report = self.get_object()
        return (
            self.request.user.role == 'ADMIN' or
            self.request.user == report.patient.user or
            self.request.user == report.doctor.user
        )
    
    def get(self, request, *args, **kwargs):
        # If patient_id is in kwargs, verify authorization
        if 'patient_id' in kwargs:
            patient_id = kwargs['patient_id']
            patient = get_object_or_404(Patient, patient_id=patient_id)
            report = self.get_object()
            
            if report.patient != patient:
                return redirect('home')
        
        return super().get(request, *args, **kwargs)


class DoctorPrescriptionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Doctor view prescriptions given"""
    model = Prescription
    template_name = 'reports/prescription_list.html'
    context_object_name = 'prescriptions'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role in ['DOCTOR', 'ADMIN']
    
    def get_queryset(self):
        if self.request.user.role == 'DOCTOR':
            doctor = self.request.user.doctor_profile
            queryset = doctor.prescriptions.select_related('patient__user')
        else:  # ADMIN
            queryset = Prescription.objects.select_related('patient__user', 'doctor__user')
        
        # Search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(patient__user__first_name__icontains=search_query) |
                Q(patient__user__last_name__icontains=search_query) |
                Q(medicine_name__icontains=search_query)
            )
        
        return queryset.order_by('-prescribed_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class PatientPrescriptionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Patient view their prescriptions"""
    model = Prescription
    template_name = 'reports/patient_prescriptions.html'
    context_object_name = 'prescriptions'
    paginate_by = 20
    
    def test_func(self):
        patient = get_object_or_404(Patient, patient_id=self.kwargs['patient_id'])
        return (
            self.request.user.role == 'PATIENT' and self.request.user == patient.user
        ) or self.request.user.role == 'ADMIN'
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, patient_id=patient_id)
        return patient.prescriptions.select_related('doctor__user').order_by('-prescribed_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs['patient_id']
        context['patient'] = get_object_or_404(Patient, patient_id=patient_id)
        return context


class DownloadMedicalReportView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Download medical report file"""
    model = MedicalReport
    pk_url_kwarg = 'report_id'
    
    def test_func(self):
        report = self.get_object()
        return (
            self.request.user.role == 'ADMIN' or
            self.request.user == report.patient.user or
            self.request.user == report.doctor.user
        )
    
    def get(self, request, *args, **kwargs):
        report = self.get_object()
        
        if not report.report_file:
            return redirect('reports:medical_report_detail', report_id=report.id)
        
        return FileResponse(report.report_file.open('rb'), as_attachment=True)
