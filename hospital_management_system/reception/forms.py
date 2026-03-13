from django import forms
from accounts.models import Appointment, Patient, Doctor

class AppointmentForm(forms.ModelForm):
    """Form for booking appointments"""
    
    auto_assign = forms.BooleanField(
        required=False,
        initial=True,
        label='Auto-assign if doctor is busy',
        help_text='Automatically assign to another available doctor if selected doctor has appointments',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Appointment
        fields = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'reason', 'notes', 'auto_assign')
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason for appointment'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Reorder fields so auto_assign appears at the end
        self.order_fields(['patient', 'doctor', 'appointment_date', 'appointment_time', 'reason', 'notes', 'auto_assign'])


class AppointmentSearchForm(forms.Form):
    """Search appointments form"""
    
    search_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))
    
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(Appointment.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
