from django import forms
from .models import (
    Medicine, MedicineCategory, Supplier, Prescription, 
    PrescriptionItem, MedicineRequest, MedicineRequestItem,
    PurchaseOrder, PurchaseOrderItem, MedicineAlert
)


class MedicineCategoryForm(forms.ModelForm):
    """Form for medicine categories"""
    class Meta:
        model = MedicineCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SupplierForm(forms.ModelForm):
    """Form for suppliers"""
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MedicineForm(forms.ModelForm):
    """Form for medicines"""
    class Meta:
        model = Medicine
        fields = [
            'name', 'category', 'supplier', 'generic_name', 'composition',
            'dosage', 'unit', 'strength', 'cost_price', 'selling_price',
            'current_stock', 'minimum_stock_level', 'reorder_level',
            'expiry_date', 'batch_number', 'status', 'requires_prescription'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'generic_name': forms.TextInput(attrs={'class': 'form-control'}),
            'composition': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'strength': forms.TextInput(attrs={'class': 'form-control'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'requires_prescription': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PrescriptionForm(forms.ModelForm):
    """Form for prescriptions"""
    class Meta:
        model = Prescription
        fields = ['patient', 'doctor', 'appointment_id', 'diagnosis', 'notes', 'valid_until']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'appointment_id': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PrescriptionItemForm(forms.ModelForm):
    """Form for prescription items"""
    class Meta:
        model = PrescriptionItem
        fields = ['medicine', 'dosage', 'frequency', 'duration', 'instructions', 'prescribed_quantity']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-select'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1 tablet'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3 times a day'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 7 days'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'prescribed_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class MedicineRequestForm(forms.ModelForm):
    """Form for medicine requests"""
    class Meta:
        model = MedicineRequest
        fields = ['patient', 'doctor', 'prescription', 'request_type', 'urgency', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'prescription': forms.Select(attrs={'class': 'form-select'}),
            'request_type': forms.Select(attrs={'class': 'form-select'}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PurchaseOrderForm(forms.ModelForm):
    """Form for purchase orders"""
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'expected_delivery_date', 'notes', 'discount']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    """Form for purchase order items"""
    class Meta:
        model = PurchaseOrderItem
        fields = ['medicine', 'ordered_quantity', 'unit_cost', 'expiry_date', 'batch_number']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-select'}),
            'ordered_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

