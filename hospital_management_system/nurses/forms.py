from django import forms
from accounts.models import Vitals

class VitalsForm(forms.ModelForm):
    """Form for recording patient vitals"""
    
    class Meta:
        model = Vitals
        fields = ('blood_pressure', 'pulse_rate', 'temperature', 'oxygen_level', 'weight', 'notes')
        widgets = {
            'blood_pressure': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 120/80'
            }),
            'pulse_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'BPM (30-200)',
                'min': '30',
                'max': '200'
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '°F (90-115)',
                'step': '0.1',
                'min': '90',
                'max': '115'
            }),
            'oxygen_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'SpO2 % (70-100)',
                'min': '70',
                'max': '100'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'kg',
                'step': '0.1',
                'min': '10'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional observations'
            }),
        }
