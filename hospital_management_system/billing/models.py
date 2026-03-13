from decimal import Decimal
from django.db import models
from accounts.models import Patient, Doctor
import uuid
from django.utils import timezone
from datetime import timedelta


# Payment method choices - defined at module level
PAYMENT_METHOD_CHOICES = (
    ('CASH', 'Cash'),
    ('CARD', 'Credit/Debit Card'),
    ('UPI', 'UPI'),
    ('INSURANCE', 'Insurance'),
    ('BANK_TRANSFER', 'Bank Transfer'),
)


class InsuranceProvider(models.Model):
    """Insurance provider/company model"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    contact_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class InsuranceClaim(models.Model):
    """Insurance claim management"""
    
    CLAIM_STATUS_CHOICES = (
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('PROCESSING', 'Processing'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PARTIAL_APPROVED', 'Partially Approved'),
    )
    
    claim_id = models.CharField(max_length=50, unique=True)
    billing = models.ForeignKey('Billing', on_delete=models.CASCADE, related_name='insurance_claims')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_claims')
    insurance_provider = models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE, related_name='claims')
    
    # Claim details
    policy_number = models.CharField(max_length=100)
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=CLAIM_STATUS_CHOICES, default='SUBMITTED')
    submitted_date = models.DateField()
    processed_date = models.DateField(blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"CLAIM-{self.claim_id} - {self.patient.user.get_full_name()} - ${self.claim_amount}"
    
    def save(self, *args, **kwargs):
        if not self.claim_id:
            self.claim_id = f"CLM-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class InstallmentPlan(models.Model):
    """Installment/EMI plan for payments"""
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DEFAULTED', 'Defaulted'),
        ('CANCELLED', 'Cancelled'),
    )
    
    plan_id = models.CharField(max_length=50, unique=True)
    billing = models.ForeignKey('Billing', on_delete=models.CASCADE, related_name='installment_plans')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='installment_plans')
    
    # Plan details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_installments = models.IntegerField()
    installments_paid = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    start_date = models.DateField()
    next_due_date = models.DateField()
    completed_date = models.DateField(blank=True, null=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"INST-{self.plan_id} - {self.patient.user.get_full_name()}"
    
    @property
    def get_remaining_amount(self):
        return self.total_amount - self.amount_paid
    
    @property
    def get_remaining_installments(self):
        return self.number_of_installments - self.installments_paid
    
    def save(self, *args, **kwargs):
        if not self.plan_id:
            self.plan_id = f"INST-{uuid.uuid4().hex[:6].upper()}"
        
        # Update status based on payments
        if self.amount_paid >= self.total_amount:
            self.status = 'COMPLETED'
            self.completed_date = timezone.now().date()
        elif self.next_due_date < timezone.now().date() and self.status == 'ACTIVE':
            self.status = 'DEFAULTED'
        
        super().save(*args, **kwargs)


class InstallmentPayment(models.Model):
    """Individual installment payments"""
    payment_id = models.CharField(max_length=50, unique=True)
    installment_plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"INST-PAY-{self.payment_id} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"IPAY-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class Billing(models.Model):
    """Billing Model for patient invoices"""
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial Payment'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('UPI', 'UPI'),
        ('INSURANCE', 'Insurance'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    )
    
    billing_id = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='billings')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='billings')
    appointment_id = models.CharField(max_length=50, blank=True, null=True)
    
    # Billing details
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medicine_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    test_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hospital_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment details
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    
    # Status and notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"BILL-{self.billing_id} - {self.patient.user.get_full_name()} - ${self.total_amount}"
    
    @property
    def get_balance(self):
        """Calculate remaining balance"""
        return self.total_amount - self.amount_paid
    
    def save(self, *args, **kwargs):
        if not self.billing_id:
            self.billing_id = f"BILL-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate totals
        self.subtotal = self.consultation_fee + self.medicine_cost + self.test_cost + self.hospital_charges + self.other_charges
        self.tax = self.subtotal * Decimal('0.10')  # 10% tax
        self.total_amount = self.subtotal + self.tax - self.discount
        
        # Update status based on payment
        if self.amount_paid >= self.total_amount and self.total_amount > 0:
            self.status = 'PAID'
        elif self.amount_paid > 0:
            self.status = 'PARTIAL'
        
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment history for billing"""
    
    payment_id = models.CharField(max_length=50, unique=True)
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PAY-{self.payment_id} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"PAY-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

