from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from datetime import timedelta


def pharmacy_login(request):
    """Custom pharmacy login view"""
    # If already logged in and has permission, go to dashboard
    if request.user.is_authenticated:
        if hasattr(request.user, 'role') and request.user.role in ['PHARMACIST', 'ADMIN', 'RECEPTIONIST', 'DOCTOR', 'NURSE']:
            return redirect('pharmacy:dashboard')
        else:
            messages.warning(request, 'You do not have permission to access the pharmacy portal.')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'role') and user.role in ['PHARMACIST', 'ADMIN', 'RECEPTIONIST', 'DOCTOR', 'NURSE']:
                login(request, user)
                return redirect('pharmacy:dashboard')
            else:
                messages.error(request, 'You do not have permission to access the pharmacy portal.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'pharmacy/login.html')


def pharmacy_home(request):
    """Pharmacy home - redirects to login or dashboard"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'role') and request.user.role in ['PHARMACIST', 'ADMIN', 'RECEPTIONIST', 'DOCTOR', 'NURSE']:
            return redirect('pharmacy:dashboard')
    return redirect('pharmacy:login')


from .models import (
    Medicine, MedicineCategory, Supplier, Prescription, PrescriptionItem,
    MedicineRequest, MedicineRequestItem, PurchaseOrder, PurchaseOrderItem, 
    MedicineAlert, MedicineStockHistory
)
from .forms import (
    MedicineForm, MedicineCategoryForm, SupplierForm, PrescriptionForm,
    PrescriptionItemForm, MedicineRequestForm, PurchaseOrderForm, PurchaseOrderItemForm
)


class PharmacyAccessMixin(UserPassesTestMixin):
    """Mixin to check pharmacy access roles"""
    
    def test_func(self):
        return hasattr(self.request.user, 'role') and self.request.user.role in ['PHARMACIST', 'ADMIN', 'RECEPTIONIST', 'DOCTOR', 'NURSE']

    def handle_no_permission(self):
        messages.error(self.request, 'Access restricted to authorized pharmacy personnel.')
        return redirect('pharmacy:login')


# ==================== Medicine Inventory Views ====================

class MedicineListView(LoginRequiredMixin, PharmacyAccessMixin, ListView):
    """List all medicines in inventory"""
    model = Medicine
    template_name = 'pharmacy/medicine_list.html'
    context_object_name = 'medicines'
    paginate_by = 20

    def get_queryset(self):
        queryset = Medicine.objects.select_related('category', 'supplier')
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(generic_name__icontains=search) |
                Q(medicine_code__icontains=search)
            )
        
        # Filter by category
        category_id = self.request.GET.get('category', '')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter: Low Stock
        low_stock = self.request.GET.get('low_stock', '')
        if low_stock:
            queryset = queryset.filter(current_stock__lte=models.F('minimum_stock_level'))
        
        # Filter: Expiring Soon
        expiring = self.request.GET.get('expiring', '')
        if expiring:
            expiry_threshold = timezone.now().date() + timedelta(days=30)
            queryset = queryset.filter(
                expiry_date__isnull=False,
                expiry_date__lte=expiry_threshold,
                expiry_date__gte=timezone.now().date()
            )
        
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['categories'] = MedicineCategory.objects.all()
        
        # Summary stats
        context['total_medicines'] = Medicine.objects.count()
        context['low_stock_count'] = Medicine.objects.filter(
            current_stock__lte=models.F('minimum_stock_level')
        ).count()
        context['out_of_stock_count'] = Medicine.objects.filter(current_stock=0).count()
        
        # Expiring soon (within 30 days)
        expiry_threshold = timezone.now().date() + timedelta(days=30)
        context['expiring_soon_count'] = Medicine.objects.filter(
            expiry_date__isnull=False,
            expiry_date__lte=expiry_threshold,
            expiry_date__gte=timezone.now().date()
        ).count()
        
        return context


class MedicineDetailView(LoginRequiredMixin, DetailView):
    """View medicine details"""
    model = Medicine
    template_name = 'pharmacy/medicine_detail.html'
    context_object_name = 'medicine'


class CreateMedicineView(LoginRequiredMixin, PharmacyAccessMixin, CreateView):
    """Create new medicine"""
    model = Medicine
    form_class = MedicineForm
    template_name = 'pharmacy/create_medicine.html'
    success_url = reverse_lazy('pharmacy:medicine_list')


class UpdateMedicineView(LoginRequiredMixin, PharmacyAccessMixin, UpdateView):
    """Update medicine"""
    model = Medicine
    form_class = MedicineForm
    template_name = 'pharmacy/update_medicine.html'
    
    def get_success_url(self):
        return reverse_lazy('pharmacy:medicine_detail', kwargs={'pk': self.object.pk})


# ==================== Medicine Category Views ====================

class MedicineCategoryListView(LoginRequiredMixin, PharmacyAccessMixin, ListView):
    """List medicine categories"""
    model = MedicineCategory
    template_name = 'pharmacy/category_list.html'
    context_object_name = 'categories'


class CreateMedicineCategoryView(LoginRequiredMixin, PharmacyAccessMixin, CreateView):
    """Create medicine category"""
    model = MedicineCategory
    form_class = MedicineCategoryForm
    template_name = 'pharmacy/create_category.html'
    success_url = reverse_lazy('pharmacy:category_list')


# ==================== Supplier Views ====================

class SupplierListView(LoginRequiredMixin, PharmacyAccessMixin, ListView):
    """List suppliers"""
    model = Supplier
    template_name = 'pharmacy/supplier_list.html'
    context_object_name = 'suppliers'


class CreateSupplierView(LoginRequiredMixin, PharmacyAccessMixin, CreateView):
    """Create supplier"""
    model = Supplier
    form_class = SupplierForm
    template_name = 'pharmacy/create_supplier.html'
    success_url = reverse_lazy('pharmacy:supplier_list')


# ==================== E-Prescription Views ====================

class PrescriptionListView(LoginRequiredMixin, ListView):
    """List prescriptions"""
    model = Prescription
    template_name = 'pharmacy/prescription_list.html'
    context_object_name = 'prescriptions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Prescription.objects.select_related('patient__user', 'doctor__user')
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(prescription_id__icontains=search) |
                Q(patient__user__first_name__icontains=search) |
                Q(patient__user__last_name__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')


class PrescriptionDetailView(LoginRequiredMixin, DetailView):
    """View prescription details"""
    model = Prescription
    template_name = 'pharmacy/prescription_detail.html'
    context_object_name = 'prescription'


class CreatePrescriptionView(LoginRequiredMixin, PharmacyAccessMixin, CreateView):
    """Create prescription"""
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'pharmacy/create_prescription.html'
    success_url = reverse_lazy('pharmacy:prescription_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prescription_items_formset'] = self.get_formset()
        return context

    def get_formset(self):
        from django.forms import formset_factory
        PrescriptionItemFormSet = formset_factory(PrescriptionItemForm, extra=1)
        return PrescriptionItemFormSet(self.request.POST or None)

    def form_valid(self, form):
        context = self.get_context_data()
        prescription_items_formset = context['prescription_items_formset']
        
        if prescription_items_formset.is_valid():
            prescription = form.save()
            for item_form in prescription_items_formset:
                if item_form.cleaned_data:
                    item = item_form.save(commit=False)
                    item.prescription = prescription
                    item.save()
            messages.success(self.request, 'Prescription created successfully!')
            return super().form_valid(form)
        
        return self.form_invalid(form)


def dispense_prescription(request, pk):
    """Dispense medicines from a prescription"""
    prescription = get_object_or_404(Prescription, pk=pk)
    
    if request.method == 'POST':
        for item in prescription.items.all():
            quantity_dispensed = int(request.POST.get(f'quantity_{item.pk}', 0))
            
            if quantity_dispensed > 0 and item.medicine.current_stock >= quantity_dispensed:
                # Update dispensed quantity
                item.dispensed_quantity = quantity_dispensed
                item.is_dispensed = True
                item.save()
                
                # Update medicine stock
                medicine = item.medicine
                medicine.current_stock -= quantity_dispensed
                medicine.save()
                
                # Create stock history
                MedicineStockHistory.objects.create(
                    medicine=medicine,
                    action='SALE',
                    quantity=-quantity_dispensed,
                    previous_stock=medicine.current_stock + quantity_dispensed,
                    new_stock=medicine.current_stock,
                    reference_number=prescription.prescription_id,
                    created_by=request.user.username if request.user.is_authenticated else 'System'
                )
        
        # Update prescription status
        all_dispensed = all(item.is_dispensed for item in prescription.items.all())
        any_dispensed = any(item.is_dispensed for item in prescription.items.all())
        
        if all_dispensed:
            prescription.status = 'DISPENSED'
            prescription.dispensed_date = timezone.now()
        elif any_dispensed:
            prescription.status = 'PARTIALLY_DISPENSED'
        
        prescription.save()
        messages.success(request, 'Prescription dispensed successfully!')
        return redirect('pharmacy:prescription_detail', pk=pk)
    
    return redirect('pharmacy:prescription_detail', pk=pk)


# ==================== Medicine Request Views ====================

class MedicineRequestListView(LoginRequiredMixin, ListView):
    """List medicine requests"""
    model = MedicineRequest
    template_name = 'pharmacy/request_list.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        queryset = MedicineRequest.objects.select_related('patient__user', 'doctor__user')
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by urgency
        urgency = self.request.GET.get('urgency', '')
        if urgency:
            queryset = queryset.filter(urgency=urgency)
        
        return queryset.order_by('-created_at')


class CreateMedicineRequestView(LoginRequiredMixin, CreateView):
    """Create medicine request"""
    model = MedicineRequest
    form_class = MedicineRequestForm
    template_name = 'pharmacy/create_request.html'
    success_url = reverse_lazy('pharmacy:medicine_request_list')


class MedicineRequestDetailView(LoginRequiredMixin, DetailView):
    """View medicine request details"""
    model = MedicineRequest
    template_name = 'pharmacy/request_detail.html'
    context_object_name = 'medicine_request'


def approve_medicine_request(request, pk):
    """Approve a medicine request"""
    medicine_request = get_object_or_404(MedicineRequest, pk=pk)
    
    if request.method == 'POST':
        for item in medicine_request.items.all():
            quantity_approved = int(request.POST.get(f'quantity_{item.pk}', 0))
            
            if quantity_approved > 0 and item.medicine.current_stock >= quantity_approved:
                item.dispensed_quantity = quantity_approved
                item.is_dispensed = True
                item.save()
                
                # Update stock
                medicine = item.medicine
                medicine.current_stock -= quantity_approved
                medicine.save()
                
                # Create stock history
                MedicineStockHistory.objects.create(
                    medicine=medicine,
                    action='SALE',
                    quantity=-quantity_approved,
                    previous_stock=medicine.current_stock + quantity_approved,
                    new_stock=medicine.current_stock,
                    reference_number=medicine_request.request_id,
                    created_by=request.user.username if request.user.is_authenticated else 'System'
                )
        
        # Update request status
        medicine_request.status = 'DISPENSED'
        medicine_request.dispensed_date = timezone.now()
        medicine_request.save()
        
        messages.success(request, 'Medicine request approved and dispensed!')
        return redirect('pharmacy:medicine_request_detail', pk=pk)
    
    return redirect('pharmacy:medicine_request_detail', pk=pk)


# ==================== Purchase Order Views ====================

class PurchaseOrderListView(LoginRequiredMixin, PharmacyAccessMixin, ListView):
    """List purchase orders"""
    model = PurchaseOrder
    template_name = 'pharmacy/purchase_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = PurchaseOrder.objects.select_related('supplier')
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')


class PurchaseOrderDetailView(LoginRequiredMixin, PharmacyAccessMixin, DetailView):
    """View purchase order details"""
    model = PurchaseOrder
    template_name = 'pharmacy/purchase_order_detail.html'
    context_object_name = 'order'


class CreatePurchaseOrderView(LoginRequiredMixin, PharmacyAccessMixin, CreateView):
    """Create purchase order"""
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'pharmacy/create_purchase_order.html'
    success_url = reverse_lazy('pharmacy:purchase_order_list')


def receive_purchase_order(request, pk):
    """Receive items from a purchase order"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        for item in purchase_order.items.all():
            received_qty = int(request.POST.get(f'received_{item.pk}', 0))
            
            if received_qty > 0:
                item.received_quantity += received_qty
                if item.received_quantity >= item.ordered_quantity:
                    item.is_received = True
                item.save()
                
                # Update medicine stock
                medicine = item.medicine
                medicine.current_stock += received_qty
                
                # Update expiry and batch if provided
                if item.expiry_date:
                    medicine.expiry_date = item.expiry_date
                if item.batch_number:
                    medicine.batch_number = item.batch_number
                
                medicine.save()
                
                # Create stock history
                MedicineStockHistory.objects.create(
                    medicine=medicine,
                    action='PURCHASE',
                    quantity=received_qty,
                    previous_stock=medicine.current_stock - received_qty,
                    new_stock=medicine.current_stock,
                    reference_number=purchase_order.order_id,
                    created_by=request.user.username if request.user.is_authenticated else 'System'
                )
        
        # Check if all items received
        all_received = all(item.is_received for item in purchase_order.items.all())
        any_received = any(item.received_quantity > 0 for item in purchase_order.items.all())
        
        if all_received:
            purchase_order.status = 'RECEIVED'
            purchase_order.received_date = timezone.now()
        elif any_received:
            purchase_order.status = 'PARTIALLY_RECEIVED'
        
        purchase_order.save()
        messages.success(request, 'Purchase order received successfully!')
        return redirect('pharmacy:purchase_order_detail', pk=pk)
    
    return redirect('pharmacy:purchase_order_detail', pk=pk)


# ==================== Alerts & Dashboard Views ====================

class PharmacyDashboardView(LoginRequiredMixin, PharmacyAccessMixin, ListView):
    """Pharmacy dashboard with alerts and summary"""
    model = Medicine
    template_name = 'pharmacy/dashboard.html'
    context_object_name = 'medicines'

    def get_queryset(self):
        return Medicine.objects.select_related('category')[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Low stock medicines
        context['low_stock_medicines'] = Medicine.objects.filter(
            current_stock__lte=models.F('minimum_stock_level')
        )[:10]
        
        # Expiring soon (within 30 days)
        expiry_threshold = timezone.now().date() + timedelta(days=30)
        context['expiring_soon'] = Medicine.objects.filter(
            expiry_date__isnull=False,
            expiry_date__lte=expiry_threshold,
            expiry_date__gte=timezone.now().date()
        )[:10]
        
        # Expired medicines
        context['expired_medicines'] = Medicine.objects.filter(
            expiry_date__lt=timezone.now().date()
        )
        
        # Pending requests
        context['pending_requests'] = MedicineRequest.objects.filter(
            status='PENDING'
        ).order_by('-urgency')[:5]
        
        # Summary stats
        context['total_medicines'] = Medicine.objects.count()
        context['total_suppliers'] = Supplier.objects.filter(is_active=True).count()
        context['total_categories'] = MedicineCategory.objects.count()
        
        # Stock value
        context['total_stock_value'] = sum(
            m.current_stock * m.cost_price for m in Medicine.objects.all()
        )
        
        return context


def medicine_alerts(request):
    """Get medicine alerts as JSON"""
    alerts = []
    
    # Low stock
    low_stock = Medicine.objects.filter(
        current_stock__lte=models.F('minimum_stock_level')
    )
    for med in low_stock:
        alerts.append({
            'type': 'LOW_STOCK',
            'medicine': med.name,
            'message': f'Low stock: {med.current_stock} units (minimum: {med.minimum_stock_level})',
            'url': reverse('pharmacy:medicine_detail', args=[med.pk])
        })
    
    # Expiring soon
    expiry_threshold = timezone.now().date() + timedelta(days=30)
    expiring = Medicine.objects.filter(
        expiry_date__isnull=False,
        expiry_date__lte=expiry_threshold,
        expiry_date__gte=timezone.now().date()
    )
    for med in expiring:
        days = med.days_until_expiry
        alerts.append({
            'type': 'EXPIRY_WARNING',
            'medicine': med.name,
            'message': f'Expiring in {days} days',
            'url': reverse('pharmacy:medicine_detail', args=[med.pk])
        })
    
    # Expired
    expired = Medicine.objects.filter(expiry_date__lt=timezone.now().date())
    for med in expired:
        alerts.append({
            'type': 'EXPIRED',
            'medicine': med.name,
            'message': 'Medicine has expired',
            'url': reverse('pharmacy:medicine_detail', args=[med.pk])
        })
    
    return JsonResponse({'alerts': alerts})


# ==================== Stock Management Views ====================

def update_stock(request, pk):
    """Update medicine stock manually"""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        new_stock = int(request.POST.get('new_stock', 0))
        action = request.POST.get('action', 'ADJUSTMENT')
        notes = request.POST.get('notes', '')
        
        if new_stock != medicine.current_stock:
            # Create stock history
            MedicineStockHistory.objects.create(
                medicine=medicine,
                action=action,
                quantity=new_stock - medicine.current_stock,
                previous_stock=medicine.current_stock,
                new_stock=new_stock,
                notes=notes,
                created_by=request.user.username if request.user.is_authenticated else 'System'
            )
            
            medicine.current_stock = new_stock
            medicine.save()
            
            messages.success(request, f'Stock updated from {medicine.current_stock - (new_stock - medicine.current_stock)} to {new_stock}')
    
    return redirect('pharmacy:medicine_detail', pk=pk)


# ==================== Search & Availability Views ====================

def medicine_search(request):
    """Search medicines for availability"""
    query = request.GET.get('q', '')
    
    if query:
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) |
            Q(generic_name__icontains=query) |
            Q(medicine_code__icontains=query)
        ).filter(status='ACTIVE')[:10]
        
        results = [{
            'id': med.pk,
            'name': med.name,
            'generic_name': med.generic_name,
            'strength': med.strength,
            'unit': med.unit,
            'stock': med.current_stock,
            'price': str(med.selling_price),
            'available': med.current_stock > 0,
            'requires_prescription': med.requires_prescription
        } for med in medicines]
    else:
        results = []
    
    return JsonResponse({'results': results})


def check_availability(request, pk):
    """Check if specific medicine is available"""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    return JsonResponse({
        'available': medicine.current_stock > 0,
        'stock': medicine.current_stock,
        'name': medicine.name,
        'requires_prescription': medicine.requires_prescription
    })


# ==================== Reports Views ====================

def pharmacy_report(request):
    """Pharmacy reports and analytics"""
    # Date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Stock movement
    stock_in = MedicineStockHistory.objects.filter(
        created_at__gte=start_date,
        action='PURCHASE'
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    stock_out = MedicineStockHistory.objects.filter(
        created_at__gte=start_date,
        action='SALE'
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Prescriptions
    prescriptions = Prescription.objects.filter(
        created_at__gte=start_date
    ).count()
    
    # Requests
    requests = MedicineRequest.objects.filter(
        created_at__gte=start_date
    ).count()
    
    context = {
        'days': days,
        'stock_in': stock_in,
        'stock_out': abs(stock_out),
        'prescriptions': prescriptions,
        'requests': requests,
        'total_medicines': Medicine.objects.count(),
        'low_stock_count': Medicine.objects.filter(
            current_stock__lte=models.F('minimum_stock_level')
        ).count(),
    }
    
    return render(request, 'pharmacy/pharmacy_report.html', context)


# Import models for the queryset
from django.db import models

