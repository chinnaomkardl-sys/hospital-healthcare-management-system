from django import forms
from .models import Billing, Payment, InsuranceProvider, InsuranceClaim, InstallmentPlan, InstallmentPayment


class BillingForm(forms.ModelForm):
    """Form for creating/updating billing"""
    
    class Meta:
        model = Billing
        fields = ['patient', 'doctor', 'appointment_id', 'consultation_fee', 
                  'medicine_cost', 'test_cost', 'hospital_charges', 'other_charges',
                  'discount', 'payment_method', 'notes', 'due_date']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_id': forms.TextInput(attrs={'class': 'form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'medicine_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'test_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hospital_charges': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_charges': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PaymentForm(forms.ModelForm):
    """Form for recording payments"""
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class InsuranceProviderForm(forms.ModelForm):
    """Form for insurance provider"""
    
    class Meta:
        model = InsuranceProvider
        fields = ['name', 'code', 'contact_number', 'email', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InsuranceClaimForm(forms.ModelForm):
    """Form for insurance claims"""
    
    class Meta:
        model = InsuranceClaim
        fields = ['billing', 'patient', 'insurance_provider', 'policy_number', 
                  'claim_amount', 'submitted_date', 'notes']
        widgets = {
            'billing': forms.Select(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'insurance_provider': forms.Select(attrs={'class': 'form-control'}),
            'policy_number': forms.TextInput(attrs={'class': 'form-control'}),
            'claim_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'submitted_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class InsuranceClaimUpdateForm(forms.ModelForm):
    """Form for updating insurance claims"""
    
    class Meta:
        model = InsuranceClaim
        fields = ['status', 'approved_amount', 'processed_date', 'notes', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'approved_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'processed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class InstallmentPlanForm(forms.ModelForm):
    """Form for installment plans"""
    
    class Meta:
        model = InstallmentPlan
        fields = ['billing', 'patient', 'total_amount', 'installment_amount', 
                  'number_of_installments', 'start_date', 'next_due_date', 'notes']
        widgets = {
            'billing': forms.Select(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'installment_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'number_of_installments': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class InstallmentPaymentForm(forms.ModelForm):
    """Form for installment payments"""
    
    class Meta:
        model = InstallmentPayment
        fields = ['amount', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

