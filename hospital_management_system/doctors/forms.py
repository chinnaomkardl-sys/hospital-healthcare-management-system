from django import forms
from accounts.models import MedicalReport, Prescription
from pharmacy.models import Medicine

class DiagnosisForm(forms.ModelForm):
    """Form for adding diagnosis and treatment notes"""
    
    class Meta:
        model = MedicalReport
        fields = ('diagnosis', 'treatment_plan', 'blood_pressure', 'heart_rate', 
                 'temperature', 'lab_results', 'notes')
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'blood_pressure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 120/80'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'BPM'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'lab_results': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PrescriptionForm(forms.ModelForm):
    """Form for adding prescriptions"""
    
    class Meta:
        model = Prescription
        fields = ('medicine_name', 'dosage', 'frequency', 'duration', 'instructions', 'notes')
        widgets = {
            'medicine_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500mg'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3 times a day'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 10 days'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class MedicalReportForm(forms.ModelForm):
    """Form for uploading medical reports"""
    
    class Meta:
        model = MedicalReport
        fields = ('diagnosis', 'treatment_plan', 'blood_pressure', 'heart_rate', 
                 'temperature', 'lab_results', 'notes', 'report_file')
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'blood_pressure': forms.TextInput(attrs={'class': 'form-control'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'lab_results': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'report_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PharmacyPrescriptionItemForm(forms.Form):
    """Form for pharmacy prescription items (doctor use)"""
    medicine = forms.ModelChoiceField(
        queryset=Medicine.objects.filter(status='ACTIVE', unit='TABLET'),
        empty_label="Search tablets...",
        widget=forms.Select(attrs={
            'class': 'form-select medicine-select',
            'data-pharmacy-search': 'true'
        })
    )
    dosage = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1 tablet'}))
    frequency = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '3 times daily'}))
    duration = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '7 days'}))
    prescribed_quantity = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}))
    instructions = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}), required=False)
