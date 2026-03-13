from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from accounts.models import Nurse, Patient, Vitals, Department
from .forms import VitalsForm
from django.core.exceptions import PermissionDenied

def nurse_patients(request):
    """Allow only users who actually have a Nurse profile."""
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        raise PermissionDenied
    if not hasattr(user, 'nurse_profile'):
        raise PermissionDenied


class AdminNurseListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin view all nurses"""
    model = Nurse
    template_name = 'nurses/nurse_list.html'
    context_object_name = 'nurses'
    paginate_by = 20
    
    def test_func(self):
        return getattr(self.request.user, 'role', None) == 'ADMIN'
    
    def get_queryset(self):
        queryset = Nurse.objects.select_related('user', 'department')
        
        # Search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(license_number__icontains=search_query)
            )
        
        # Filter by department
        department = self.request.GET.get('department', '')
        if department:
            queryset = queryset.filter(department__id=department)
        
        # Filter by shift
        shift = self.request.GET.get('shift', '')
        if shift:
            queryset = queryset.filter(shift=shift)
        
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
        context['department'] = self.request.GET.get('department', '')
        context['shift'] = self.request.GET.get('shift', '')
        context['availability'] = self.request.GET.get('availability', '')
        context['departments'] = Department.objects.all()
        context['shifts'] = Nurse.SHIFT_CHOICES
        context['total_nurses'] = Nurse.objects.count()
        context['available_nurses'] = Nurse.objects.filter(is_available=True).count()
        return context


class NurseDetailView(LoginRequiredMixin, DetailView):
    """View nurse details"""
    model = Nurse
    template_name = 'nurses/nurse_detail.html'
    context_object_name = 'nurse'
    slug_field = 'user__id'
    slug_url_kwarg = 'nurse_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nurse = self.get_object()
        context['patients'] = nurse.patients.all()
        context['vitals_recorded'] = nurse.vitals_recorded.all().order_by('-recorded_at')[:10]
        context['total_patients'] = nurse.patients.count()
        return context


class NursePatientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Patient
    template_name = 'nurses/patient_list.html'
    
    def test_func(self):
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        # Allow either an attached Nurse profile or a user whose role is NURSE
        return getattr(user, 'role', None) == 'NURSE' or hasattr(user, 'nurse_profile')
    
    def get_queryset(self):
        nurse = Nurse.objects.filter(user=self.request.user).first()
        if not nurse:
            # If there's no Nurse profile for this user, don't raise 404 —
            # return an empty queryset so the template can render a friendly message.
            return Patient.objects.none()

        queryset = nurse.patients.select_related('user', 'assigned_doctor')
        
        # Search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(patient_id__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class NurseRecordVitalsView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Nurse record patient vitals"""
    model = Vitals
    form_class = VitalsForm
    template_name = 'nurses/record_vitals.html'
    
    def test_func(self):
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return getattr(user, 'role', None) == 'NURSE' or hasattr(user, 'nurse_profile')
    
    def form_valid(self, form):
        nurse = get_object_or_404(Nurse, user=self.request.user)
        form.instance.nurse = nurse
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


class NurseViewVitalsHistoryView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Nurse view patient vitals history"""
    model = Vitals
    template_name = 'nurses/vitals_history.html'
    context_object_name = 'vitals'
    paginate_by = 20
    
    def test_func(self):
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return getattr(user, 'role', None) == 'NURSE' or hasattr(user, 'nurse_profile')
    
    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        patient = get_object_or_404(Patient, patient_id=patient_id)
        return patient.vitals.all().order_by('-recorded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs['patient_id']
        context['patient'] = get_object_or_404(Patient, patient_id=patient_id)
        return context
