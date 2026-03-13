from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import FormView, View, TemplateView, ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import CustomUser, Doctor, Nurse, Receptionist, Patient, Department
from .forms import (
    CustomUserCreationForm, LoginForm, DoctorForm, NurseForm, 
    ReceptionistForm, PatientForm, CustomUserChangeForm
)
import uuid
from datetime import datetime


def admin_required():
    """Decorator-like function for class-based views"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'
    return test_func


class RoleChoiceView(TemplateView):
    """View to choose login role"""
    template_name = 'accounts/role_choice.html'


class RoleLoginView(FormView):
    """Base login view for all roles"""
    template_name = 'accounts/login.html'
    form_class = LoginForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = self.kwargs.get('role', 'PATIENT')
        context['role'] = role
        context['role_display'] = dict(CustomUser.ROLE_CHOICES).get(role, 'User')
        return context
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            form.add_error('email', 'Invalid email or password.')
            return self.form_invalid(form)
        
        # Check role
        role = self.kwargs.get('role', 'PATIENT')
        if user.role != role:
            form.add_error('email', f'This email is registered as {user.get_role_display()}, not {dict(CustomUser.ROLE_CHOICES).get(role, role)}.')
            return self.form_invalid(form)
        
        # Authenticate
        user = authenticate(request=self.request, username=user.username, password=password)
        
        if user is not None:
            login(self.request, user)
            
            # Redirect to appropriate dashboard
            if user.role == 'ADMIN':
                return redirect('dashboard:admin_dashboard')
            elif user.role == 'DOCTOR':
                return redirect('dashboard:doctor_dashboard')
            elif user.role == 'NURSE':
                return redirect('dashboard:nurse_dashboard')
            elif user.role == 'RECEPTIONIST':
                return redirect('dashboard:receptionist_dashboard')
            elif user.role == 'PHARMACIST':
                return redirect('pharmacy:dashboard')
            else:  # PATIENT
                return redirect('dashboard:patient_dashboard')
        else:
            form.add_error('password', 'Invalid email or password.')
            return self.form_invalid(form)


class LogoutView(View):
    """Logout view"""
    
    def get(self, request):
        logout(request)
        return redirect('home')


class AdminRegisterView(CreateView):
    """Admin registration view (for first admin setup)"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/admin_register.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Admin Registration'
        context['form'] = kwargs.get('form') or self.get_form()
        return context
    
    def form_valid(self, form):
        form.instance.role = 'ADMIN'
        form.instance.is_staff = True
        form.instance.is_superuser = True
        response = super().form_valid(form)
        # Auto-login after registration
        user = authenticate(
            username=form.instance.username,
            password=form.cleaned_data['password1']
        )
        if user:
            login(self.request, user)
            return redirect('dashboard:admin_dashboard')
        return response
    
    def get_success_url(self):
        return reverse_lazy('dashboard:admin_dashboard')


class DoctorRegisterView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Doctor registration view - Admin only"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/doctor_register.html'
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Doctor Registration'
        context['form'] = kwargs.get('form') or self.get_form()
        context['doctor_form'] = kwargs.get('doctor_form') or DoctorForm()
        return context
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        license_number = request.POST.get('license_number')
        specialization = request.POST.get('specialization')
        qualification = request.POST.get('qualification')
        experience_years = request.POST.get('experience_years')
        consultation_fee = request.POST.get('consultation_fee', 500)
        
        # Validate passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return self.get(request)
        
        # Check if user exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return self.get(request)
        
        try:
            # Create user
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='DOCTOR'
            )
            
            # Create doctor profile
            Doctor.objects.create(
                user=user,
                license_number=license_number,
                specialization=specialization,
                qualification=qualification,
                experience_years=int(experience_years),
                consultation_fee=float(consultation_fee)
            )
            
            # Auto-login
            user = authenticate(username=email, password=password1)
            if user:
                login(self.request, user)
                messages.success(request, 'Doctor registered successfully!')
                return redirect('dashboard:doctor_dashboard')
        except Exception as e:
            messages.error(request, f'Registration error: {str(e)}')
            return self.get(request)
        
        return redirect('accounts:role_choice')
    
    def get_success_url(self):
        return reverse_lazy('dashboard:doctor_dashboard')


class NurseRegisterView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Nurse registration view - Admin only"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/nurse_register.html'
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Nurse Registration'
        context['form'] = kwargs.get('form') or self.get_form()
        context['nurse_form'] = kwargs.get('nurse_form') or NurseForm()
        return context
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        license_number = request.POST.get('license_number')
        shift = request.POST.get('shift', 'MORNING')
        qualification = request.POST.get('qualification')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return self.get(request)
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return self.get(request)
        
        try:
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='NURSE'
            )
            
            Nurse.objects.create(
                user=user,
                license_number=license_number,
                shift=shift,
                qualification=qualification
            )
            
            user = authenticate(username=email, password=password1)
            if user:
                login(self.request, user)
                messages.success(request, 'Nurse registered successfully!')
                return redirect('dashboard:nurse_dashboard')
        except Exception as e:
            messages.error(request, f'Registration error: {str(e)}')
            return self.get(request)
        
        return redirect('accounts:role_choice')
    
    def get_success_url(self):
        return reverse_lazy('dashboard:nurse_dashboard')


class PatientRegisterView(CreateView):
    """Patient registration view"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/patient_register.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Patient Registration'
        context['form'] = kwargs.get('form') or self.get_form()
        context['patient_form'] = kwargs.get('patient_form') or PatientForm()
        return context
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender', 'OTHER')
        blood_group = request.POST.get('blood_group', 'O+')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return self.get(request)
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return self.get(request)
        
        try:
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='PATIENT'
            )
            
            Patient.objects.create(
                user=user,
                patient_id=f"PAT-{uuid.uuid4().hex[:8].upper()}",
                date_of_birth=date_of_birth,
                gender=gender,
                blood_group=blood_group
            )
            
            user = authenticate(username=email, password=password1)
            if user:
                login(self.request, user)
                messages.success(request, 'Patient registered successfully!')
                return redirect('dashboard:patient_dashboard')
        except Exception as e:
            messages.error(request, f'Registration error: {str(e)}')
            return self.get(request)
        
        return redirect('accounts:role_choice')
    
    def get_success_url(self):
        return reverse_lazy('dashboard:patient_dashboard')




class ReceptionistRegisterView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Receptionist registration view - Admin only"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/receptionist_register.html'
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'
    
    def get_context_data(self, **kwargs):
        context = {}
        context['title'] = 'Receptionist Registration'
        context['form'] = kwargs.get('form') or self.get_form()
        context['receptionist_form'] = kwargs.get('receptionist_form') or ReceptionistForm()
        return context
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        employee_id = request.POST.get('employee_id')
        shift = request.POST.get('shift', 'MORNING')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return self.get(request)
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return self.get(request)
        
        try:
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='RECEPTIONIST'
            )
            
            Receptionist.objects.create(
                user=user,
                employee_id=employee_id,
                shift=shift
            )
            
            user = authenticate(username=email, password=password1)
            if user:
                login(self.request, user)
                messages.success(request, 'Receptionist registered successfully!')
                return redirect('dashboard:receptionist_dashboard')
        except Exception as e:
            messages.error(request, f'Registration error: {str(e)}')
            return self.get(request)
        
        return redirect('accounts:role_choice')
    
    def get_success_url(self):
        return reverse_lazy('dashboard:receptionist_dashboard')


class PharmacistRegisterView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Pharmacist registration view - Admin only"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/pharmacist_register.html'
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        pharmacist_license = request.POST.get('pharmacist_license')
        qualification = request.POST.get('qualification')
        shift = request.POST.get('shift', 'MORNING')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return self.get(request)
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return self.get(request)
        
        try:
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='PHARMACIST'
            )
            
            # Log pharmacist_license etc. as user notes or custom field if needed
            messages.success(request, f'Pharmacist {user.get_full_name()} registered successfully with license {pharmacist_license}!')
            
            user = authenticate(username=email, password=password1)
            if user:
                login(self.request, user)
                return redirect('pharmacy:dashboard')
        except Exception as e:
            messages.error(request, f'Registration error: {str(e)}')
            return self.get(request)
        
        return redirect('accounts:role_choice')
    
    def get_success_url(self):
        return reverse_lazy('pharmacy:dashboard')




class UserProfileView(LoginRequiredMixin, DetailView):
    """View user profile"""
    model = CustomUser
    template_name = 'accounts/profile.html'
    context_object_name = 'user_profile'
    
    def get_object(self):
        return self.request.user


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Edit user profile"""
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/edit_profile.html'
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('accounts:profile')
