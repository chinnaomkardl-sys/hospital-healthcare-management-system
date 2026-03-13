from django.db import models
from accounts.models import Patient, Doctor
from django.utils import timezone
import uuid
from decimal import Decimal


class MedicineCategory(models.Model):
    """Medicine category model"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Medicine Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Medicine supplier/vendor model"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"SUP-{uuid.uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)


class Medicine(models.Model):
    """Medicine inventory model"""
    
    UNIT_CHOICES = (
        ('TABLET', 'Tablet'),
        ('CAPSULE', 'Capsule'),
        ('SYRUP', 'Syrup'),
        ('INJECTION', 'Injection'),
        ('CREAM', 'Cream'),
        ('OINTMENT', 'Ointment'),
        ('DROPS', 'Drops'),
        ('INHALER', 'Inhaler'),
        ('PATCH', 'Patch'),
        ('OTHER', 'Other'),
    )

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('DISCONTINUED', 'Discontinued'),
    )

    name = models.CharField(max_length=200)
    medicine_code = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(MedicineCategory, on_delete=models.SET_NULL, null=True, related_name='medicines')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='medicines')
    
    # Medicine details
    generic_name = models.CharField(max_length=200, blank=True)
    composition = models.TextField(blank=True)
    dosage = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='TABLET')
    strength = models.CharField(max_length=50, blank=True)
    
    # Pricing
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Stock management
    current_stock = models.IntegerField(default=0)
    minimum_stock_level = models.IntegerField(default=10)
    reorder_level = models.IntegerField(default=20)
    
    # Expiry tracking
    expiry_date = models.DateField(blank=True, null=True)
    batch_number = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    requires_prescription = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.strength})"

    @property
    def is_low_stock(self):
        """Check if medicine is below minimum stock level"""
        return self.current_stock <= self.minimum_stock_level

    @property
    def is_expiring_soon(self):
        """Check if medicine is expiring within 30 days"""
        if not self.expiry_date:
            return False
        days_until_expiry = (self.expiry_date - timezone.now().date()).days
        return 0 <= days_until_expiry <= 30

    @property
    def is_expired(self):
        """Check if medicine is expired"""
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()

    @property
    def days_until_expiry(self):
        """Get days until expiry"""
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.now().date()).days

    def save(self, *args, **kwargs):
        if not self.medicine_code:
            self.medicine_code = f"MED-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class MedicineStockHistory(models.Model):
    """Track medicine stock changes"""
    
    ACTION_CHOICES = (
        ('PURCHASE', 'Purchase/Restock'),
        ('SALE', 'Sale/Dispense'),
        ('RETURN', 'Return to Supplier'),
        ('DAMAGE', 'Damaged/Expired'),
        ('ADJUSTMENT', 'Stock Adjustment'),
    )

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stock_history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.medicine.name} - {self.action} - {self.quantity}"


class Prescription(models.Model):
    """E-prescription model for doctor prescriptions"""
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('DISPENSED', 'Dispensed'),
        ('PARTIALLY_DISPENSED', 'Partially Dispensed'),
        ('CANCELLED', 'Cancelled'),
    )

    prescription_id = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='pharmacy_prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='pharmacy_prescriptions')
    appointment_id = models.CharField(max_length=50, blank=True, null=True)
    
    # Prescription details
    diagnosis = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Dates
    prescription_date = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateField(blank=True, null=True)
    dispensed_date = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"RX-{self.prescription_id} - {self.patient.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.prescription_id:
            self.prescription_id = f"RX-{uuid.uuid4().hex[:6].upper()}"
        if not self.valid_until:
            self.valid_until = timezone.now().date() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)


class PrescriptionItem(models.Model):
    """Individual items in a prescription"""
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    
    # Dosage instructions
    dosage = models.CharField(max_length=100)  # e.g., "1 tablet", "5ml"
    frequency = models.CharField(max_length=100)  # e.g., "3 times a day", "twice daily"
    duration = models.CharField(max_length=100, blank=True)  # e.g., "7 days"
    instructions = models.TextField(blank=True)
    
    # Quantity
    prescribed_quantity = models.IntegerField(default=0)
    dispensed_quantity = models.IntegerField(default=0)
    
    # Status
    is_dispensed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.medicine.name} - {self.prescribed_quantity} {self.medicine.unit}"


class MedicineRequest(models.Model):
    """Medicine request from wards/patients"""
    
    REQUEST_TYPE_CHOICES = (
        ('PATIENT', 'Patient Request'),
        ('WARD', 'Ward Request'),
        ('EMERGENCY', 'Emergency'),
        ('ROUTINE', 'Routine'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DISPENSED', 'Dispensed'),
        ('REJECTED', 'Rejected'),
        ('PARTIALLY_DISPENSED', 'Partially Dispensed'),
    )

    request_id = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medicine_requests', null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='medicine_requests')
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True, related_name='medicine_requests')
    
    # Request details
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='PATIENT')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    urgency = models.CharField(max_length=20, choices=[('NORMAL', 'Normal'), ('URGENT', 'Urgent'), ('EMERGENCY', 'Emergency')], default='NORMAL')
    notes = models.TextField(blank=True)
    
    # Dates
    requested_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    dispensed_date = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"REQ-{self.request_id} - {self.get_request_type_display()}"

    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = f"REQ-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class MedicineRequestItem(models.Model):
    """Individual items in a medicine request"""
    
    request = models.ForeignKey(MedicineRequest, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    requested_quantity = models.IntegerField(default=0)
    dispensed_quantity = models.IntegerField(default=0)
    is_dispensed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.medicine.name} - {self.requested_quantity}"


class PurchaseOrder(models.Model):
    """Purchase order for medicine suppliers"""
    
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent to Supplier'),
        ('PARTIALLY_RECEIVED', 'Partially Received'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    )

    order_id = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateField(blank=True, null=True)
    received_date = models.DateField(blank=True, null=True)
    
    # Totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    received_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"PO-{self.order_id} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"PO-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate totals
        self.subtotal = sum(item.total_cost for item in self.items.all())
        self.tax = self.subtotal * Decimal('0.10')  # 10% tax
        self.total_amount = self.subtotal + self.tax - self.discount
        
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    """Items in a purchase order"""
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    
    # Quantity
    ordered_quantity = models.IntegerField(default=0)
    received_quantity = models.IntegerField(default=0)
    
    # Pricing
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Expiry
    expiry_date = models.DateField(blank=True, null=True)
    batch_number = models.CharField(max_length=100, blank=True)
    
    # Status
    is_received = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.medicine.name} - {self.ordered_quantity}"

    def save(self, *args, **kwargs):
        self.total_cost = self.ordered_quantity * self.unit_cost
        super().save(*args, **kwargs)


class MedicineAlert(models.Model):
    """Alerts for medicine inventory and expiry"""
    
    ALERT_TYPE_CHOICES = (
        ('LOW_STOCK', 'Low Stock'),
        ('EXPIRY_WARNING', 'Expiry Warning'),
        ('EXPIRED', 'Expired'),
        ('OUT_OF_STOCK', 'Out of Stock'),
    )

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.medicine.name}"

