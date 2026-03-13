from django import forms
from accounts.models import Patient, Doctor, Nurse

class PatientFiltersForm(forms.Form):
    """Patient filtering form"""
    
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search by name or patient ID'
    }))
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(Patient.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assigned_doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Filter by Doctor'
    )


class AssignDoctorForm(forms.ModelForm):
    """Form to assign doctor and nurse to a patient"""
    
    class Meta:
        model = Patient
        fields = ['assigned_doctor', 'assigned_nurse']
        widgets = {
            'assigned_doctor': forms.Select(attrs={'class': 'form-control'}),
            'assigned_nurse': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_doctor'].queryset = Doctor.objects.select_related('user').all()
        self.fields['assigned_nurse'].queryset = Nurse.objects.select_related('user').all()
        self.fields['assigned_doctor'].empty_label = "Select a Doctor (Optional)"
        self.fields['assigned_nurse'].empty_label = "Select a Nurse (Optional)"
