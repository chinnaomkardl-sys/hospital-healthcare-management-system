from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Doctor, Nurse, Receptionist, Patient, Department

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form"""
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'address', 'city', 'state', 'role')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form"""
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'address', 'city', 'state', 'profile_picture')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DoctorForm(forms.ModelForm):
    """Doctor registration form"""
    
    class Meta:
        model = Doctor
        fields = ('license_number', 'specialization', 'department', 'qualification', 
                 'experience_years', 'consultation_fee', 'bio')
        widgets = {
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class NurseForm(forms.ModelForm):
    """Nurse registration form"""
    
    class Meta:
        model = Nurse
        fields = ('license_number', 'department', 'shift', 'qualification', 'experience_years')
        widgets = {
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'shift': forms.Select(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ReceptionistForm(forms.ModelForm):
    """Receptionist registration form"""
    
    class Meta:
        model = Receptionist
        fields = ('employee_id', 'department', 'shift')
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'shift': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PatientForm(forms.ModelForm):
    """Patient registration form"""
    
    class Meta:
        model = Patient
        fields = ('date_of_birth', 'gender', 'blood_group', 'emergency_contact', 
                 'emergency_contact_name', 'allergies', 'medical_history')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LoginForm(forms.Form):
    """Login form for all roles"""
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your email',
        'autocomplete': 'off'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your password'
    }))
