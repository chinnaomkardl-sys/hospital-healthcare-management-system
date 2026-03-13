from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from datetime import timedelta
from decimal import Decimal

from .models import Billing, Payment, InsuranceProvider, InsuranceClaim, InstallmentPlan, InstallmentPayment
from .forms import BillingForm, PaymentForm, InsuranceProviderForm, InsuranceClaimForm, InsuranceClaimUpdateForm, InstallmentPlanForm, InstallmentPaymentForm
from accounts.models import Patient

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Try to import payment gateways
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False


class ReceptionistBillingMixin(UserPassesTestMixin):
    """Mixin to check if user is receptionist or admin"""
    
    def test_func(self):
        return self.request.user.role in ['RECEPTIONIST', 'ADMIN']


# ==================== Billing Views ====================

class BillingListView(LoginRequiredMixin, ReceptionistBillingMixin, ListView):
    """List all billing records"""
    model = Billing
    template_name = 'billing/billing_list.html'
    context_object_name = 'billings'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Billing.objects.select_related('patient__user', 'doctor__user')
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(billing_id__icontains=search) |
                Q(patient__user__first_name__icontains=search) |
                Q(patient__user__last_name__icontains=search) |
                Q(patient__patient_id__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['statuses'] = Billing.STATUS_CHOICES
        
        # Summary stats
        today = timezone.now().date()
        context['total_bills'] = Billing.objects.count()
        context['pending_bills'] = Billing.objects.filter(status='PENDING').count()
        context['today_collections'] = Billing.objects.filter(
            status='PAID',
            payment_date__date=today
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        return context


class BillingDetailView(LoginRequiredMixin, DetailView):
    """View billing details"""
    model = Billing
    template_name = 'billing/billing_detail.html'
    context_object_name = 'billing'
    
    def get_queryset(self):
        return Billing.objects.select_related('patient__user', 'doctor__user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.object.payments.all()
        context['insurance_claims'] = self.object.insurance_claims.all()
        context['installment_plans'] = self.object.installment_plans.all()
        context['reportlab_available'] = REPORTLAB_AVAILABLE
        return context


class CreateBillingView(LoginRequiredMixin, ReceptionistBillingMixin, CreateView):
    """Create new billing"""
    model = Billing
    form_class = BillingForm
    template_name = 'billing/create_billing.html'
    success_url = reverse_lazy('billing:billing_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {
            'consultation_fee': 500,
        }
        return kwargs
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class AddPaymentView(LoginRequiredMixin, ReceptionistBillingMixin, CreateView):
    """Add payment to billing"""
    model = Payment
    form_class = PaymentForm
    template_name = 'billing/add_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['billing'] = get_object_or_404(Billing, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        billing = get_object_or_404(Billing, pk=self.kwargs['pk'])
        payment = form.save(commit=False)
        payment.billing = billing
        payment.save()
        
        # Update billing
        billing.amount_paid += payment.amount
        billing.payment_method = payment.payment_method
        billing.payment_date = timezone.now()
        billing.save()
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('billing:billing_detail', kwargs={'pk': self.kwargs['pk']})


class PatientBillingView(LoginRequiredMixin, ListView):
    """View patient's billing history"""
    model = Billing
    template_name = 'billing/patient_billing.html'
    context_object_name = 'billings'
    
    def get_queryset(self):
        patient = get_object_or_404(Patient, patient_id=self.kwargs['patient_id'])
        return Billing.objects.filter(patient=patient).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = get_object_or_404(Patient, patient_id=self.kwargs['patient_id'])
        return context


# ==================== PDF Invoice Generation ====================

def generate_invoice_pdf(request, pk):
    """Generate PDF invoice for a billing record"""
    billing = get_object_or_404(Billing, pk=pk)
    
    if not REPORTLAB_AVAILABLE:
        return HttpResponse("PDF generation not available. Please install reportlab.", status=500)
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{billing.billing_id}.pdf"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceBefore=20, spaceAfter=10)
    normal_style = styles['Normal']
    
    # Hospital Header
    elements.append(Paragraph("Hospital Management System", title_style))
    elements.append(Paragraph("123 Medical Center Drive", normal_style))
    elements.append(Paragraph("Healthcare City, HC 12345", normal_style))
    elements.append(Paragraph("Phone: (555) 123-4567", normal_style))
    elements.append(Spacer(1, 20))
    
    # Invoice Title
    elements.append(Paragraph(f"Invoice: {billing.billing_id}", heading_style))
    elements.append(Paragraph(f"Date: {billing.created_at.strftime('%B %d, %Y')}", normal_style))
    if billing.due_date:
        elements.append(Paragraph(f"Due Date: {billing.due_date.strftime('%B %d, %Y')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Patient Info
    elements.append(Paragraph("Bill To:", heading_style))
    elements.append(Paragraph(f"Patient Name: {billing.patient.user.get_full_name()}", normal_style))
    elements.append(Paragraph(f"Patient ID: {billing.patient.patient_id}", normal_style))
    if billing.doctor:
        elements.append(Paragraph(f"Doctor: Dr. {billing.doctor.user.get_full_name()}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Bill Items Table
    data = [['Description', 'Amount']]
    if billing.consultation_fee > 0:
        data.append(['Consultation Fee', f'${billing.consultation_fee}'])
    if billing.medicine_cost > 0:
        data.append(['Medicine Cost', f'${billing.medicine_cost}'])
    if billing.test_cost > 0:
        data.append(['Test/Lab Cost', f'${billing.test_cost}'])
    if billing.hospital_charges > 0:
        data.append(['Hospital Charges', f'${billing.hospital_charges}'])
    if billing.other_charges > 0:
        data.append(['Other Charges', f'${billing.other_charges}'])
    
    data.append(['Subtotal', f'${billing.subtotal}'])
    data.append(['Tax (10%)', f'${billing.tax}'])
    if billing.discount > 0:
        data.append(['Discount', f'-${billing.discount}'])
    data.append(['Total Amount', f'${billing.total_amount}'])
    data.append(['Amount Paid', f'${billing.amount_paid}'])
    data.append(['Balance Due', f'${billing.get_balance}'])
    
    table = Table(data, colWidths=[4*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    # Payment Status
    elements.append(Paragraph(f"Payment Status: {billing.get_status_display()}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Payment History
    if billing.payments.exists():
        elements.append(Paragraph("Payment History:", heading_style))
        payment_data = [['Date', 'Amount', 'Method', 'Transaction ID']]
        for payment in billing.payments.all():
            payment_data.append([
                payment.created_at.strftime('%Y-%m-%d'),
                f'${payment.amount}',
                payment.get_payment_method_display(),
                payment.transaction_id or '-'
            ])
        
        payment_table = Table(payment_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 2*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(payment_table)
    
    # Build PDF
    doc.build(elements)
    return response


# ==================== Insurance Claim Views ====================

class InsuranceClaimListView(LoginRequiredMixin, ReceptionistBillingMixin, ListView):
    """List all insurance claims"""
    model = InsuranceClaim
    template_name = 'billing/insurance_claim_list.html'
    context_object_name = 'claims'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = InsuranceClaim.objects.select_related('patient__user', 'billing', 'insurance_provider')
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(claim_id__icontains=search) |
                Q(patient__user__first_name__icontains=search) |
                Q(patient__user__last_name__icontains=search) |
                Q(policy_number__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['statuses'] = InsuranceClaim.CLAIM_STATUS_CHOICES
        return context


class InsuranceClaimDetailView(LoginRequiredMixin, DetailView):
    """View insurance claim details"""
    model = InsuranceClaim
    template_name = 'billing/insurance_claim_detail.html'
    context_object_name = 'claim'
    
    def get_queryset(self):
        return InsuranceClaim.objects.select_related('patient__user', 'billing', 'insurance_provider')


class CreateInsuranceClaimView(LoginRequiredMixin, ReceptionistBillingMixin, CreateView):
    """Create new insurance claim"""
    model = InsuranceClaim
    form_class = InsuranceClaimForm
    template_name = 'billing/create_insurance_claim.html'
    success_url = reverse_lazy('billing:insurance_claim_list')
    
    def get_initial(self):
        initial = super().get_initial()
        initial['submitted_date'] = timezone.now().date()
        if 'billing_id' in self.request.GET:
            try:
                billing = Billing.objects.get(pk=self.request.GET.get('billing_id'))
                initial['billing'] = billing
                initial['patient'] = billing.patient
                initial['claim_amount'] = billing.total_amount
            except Billing.DoesNotExist:
                pass
        return initial


class UpdateInsuranceClaimView(LoginRequiredMixin, ReceptionistBillingMixin, UpdateView):
    """Update insurance claim status"""
    model = InsuranceClaim
    form_class = InsuranceClaimUpdateForm
    template_name = 'billing/update_insurance_claim.html'
    
    def get_success_url(self):
        return reverse_lazy('billing:insurance_claim_detail', kwargs={'pk': self.kwargs['pk']})
    
    def form_valid(self, form):
        claim = form.save(commit=False)
        if claim.status in ['APPROVED', 'PARTIAL_APPROVED', 'REJECTED'] and not claim.processed_date:
            claim.processed_date = timezone.now().date()
            
            # If approved, update billing
            if claim.status == 'APPROVED' and claim.approved_amount > 0:
                billing = claim.billing
                billing.amount_paid += claim.approved_amount
                billing.payment_method = 'INSURANCE'
                billing.payment_date = timezone.now()
                billing.save()
        
        claim.save()
        return super().form_valid(form)


# ==================== Insurance Provider Views ====================

class InsuranceProviderListView(LoginRequiredMixin, ReceptionistBillingMixin, ListView):
    """List all insurance providers"""
    model = InsuranceProvider
    template_name = 'billing/insurance_provider_list.html'
    context_object_name = 'providers'


class CreateInsuranceProviderView(LoginRequiredMixin, ReceptionistBillingMixin, CreateView):
    """Create new insurance provider"""
    model = InsuranceProvider
    form_class = InsuranceProviderForm
    template_name = 'billing/create_insurance_provider.html'
    success_url = reverse_lazy('billing:insurance_provider_list')


# ==================== Installment Plan Views ====================

class InstallmentPlanListView(LoginRequiredMixin, ReceptionistBillingMixin, ListView):
    """List all installment plans"""
    model = InstallmentPlan
    template_name = 'billing/installment_plan_list.html'
    context_object_name = 'plans'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = InstallmentPlan.objects.select_related('patient__user', 'billing')
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(plan_id__icontains=search) |
                Q(patient__user__first_name__icontains=search) |
                Q(patient__user__last_name__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['statuses'] = InstallmentPlan.STATUS_CHOICES
        return context


class InstallmentPlanDetailView(LoginRequiredMixin, DetailView):
    """View installment plan details"""
    model = InstallmentPlan
    template_name = 'billing/installment_plan_detail.html'
    context_object_name = 'plan'
    
    def get_queryset(self):
        return InstallmentPlan.objects.select_related('patient__user', 'billing')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.object.payments.all()
        return context


class CreateInstallmentPlanView(LoginRequiredMixin, ReceptionistBillingMixin, CreateView):
    """Create new installment plan"""
    model = InstallmentPlan
    form_class = InstallmentPlanForm
    template_name = 'billing/create_installment_plan.html'
    success_url = reverse_lazy('billing:installment_plan_list')
    
    def get_initial(self):
        initial = super().get_initial()
        initial['start_date'] = timezone.now().date()
        initial['next_due_date'] = (timezone.now() + timedelta(days=30)).date()
        if 'billing_id' in self.request.GET:
            try:
                billing = Billing.objects.get(pk=self.request.GET.get('billing_id'))
                initial['billing'] = billing
                initial['patient'] = billing.patient
                initial['total_amount'] = billing.get_balance
            except Billing.DoesNotExist:
                pass
        return initial


class AddInstallmentPaymentView(LoginRequiredMixin, ReceptionistBillingMixin, CreateView):
    """Add payment to installment plan"""
    model = InstallmentPayment
    form_class = InstallmentPaymentForm
    template_name = 'billing/add_installment_payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plan'] = get_object_or_404(InstallmentPlan, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        plan = get_object_or_404(InstallmentPlan, pk=self.kwargs['pk'])
        payment = form.save(commit=False)
        payment.installment_plan = plan
        payment.save()
        
        # Update plan
        plan.amount_paid += payment.amount
        plan.installments_paid += 1
        plan.next_due_date = (timezone.now() + timedelta(days=30 * plan.get_remaining_installments)).date()
        plan.save()
        
        # Update billing
        billing = plan.billing
        billing.amount_paid += payment.amount
        billing.payment_date = timezone.now()
        billing.save()
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('billing:installment_plan_detail', kwargs={'pk': self.kwargs['pk']})


# ==================== Payment Gateway Views ====================

def payment_gateway_view(request, pk):
    """Payment gateway integration view (Razorpay/Stripe)"""
    billing = get_object_or_404(Billing, pk=pk)
    
    context = {
        'billing': billing,
        'stripe_available': STRIPE_AVAILABLE,
        'razorpay_available': RAZORPAY_AVAILABLE,
    }
    return render(request, 'billing/payment_gateway.html', context)


def payment_callback(request, pk):
    """Handle payment gateway callback"""
    billing = get_object_or_404(Billing, pk=pk)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'CARD')
        transaction_id = request.POST.get('transaction_id', '')
        amount = Decimal(request.POST.get('amount', 0))
        
        if amount > 0:
            # Create payment record
            Payment.objects.create(
                billing=billing,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id
            )
            
            # Update billing
            billing.amount_paid += amount
            billing.payment_method = payment_method
            billing.payment_date = timezone.now()
            billing.save()
            
            return redirect('billing:billing_detail', pk=billing.pk)
    
    return redirect('billing:billing_detail', pk=billing.pk)


# ==================== Financial Reports Views ====================

class FinancialReportsView(LoginRequiredMixin, ReceptionistBillingMixin, ListView):
    """Financial reports and analytics"""
    model = Billing
    template_name = 'billing/financial_reports.html'
    context_object_name = 'billings'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date range filter
        days = int(self.request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Revenue stats
        total_revenue = Billing.objects.filter(
            created_at__gte=start_date
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        collected_amount = Billing.objects.filter(
            payment_date__gte=start_date
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        pending_amount = Billing.objects.filter(
            status__in=['PENDING', 'PARTIAL']
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # By status
        status_counts = Billing.objects.values('status').annotate(count=Count('id'))
        
        # Insurance claims stats
        insurance_claims = InsuranceClaim.objects.filter(
            created_at__gte=start_date
        ).aggregate(
            total=Sum('claim_amount'),
            approved=Sum('approved_amount')
        )
        
        # Calculate claim_diff
        total_claims = insurance_claims.get('total') or 0
        approved_claims = insurance_claims.get('approved') or 0
        claim_diff = total_claims - approved_claims
        
        # Installment stats
        installment_stats = InstallmentPlan.objects.aggregate(
            total_plans=Count('id'),
            active=Count('id', filter=Q(status='ACTIVE')),
            completed=Count('id', filter=Q(status='COMPLETED')),
            defaulted=Count('id', filter=Q(status='DEFAULTED'))
        )
        
        context.update({
            'days': days,
            'total_revenue': total_revenue,
            'collected_amount': collected_amount,
            'pending_amount': pending_amount,
            'status_counts': status_counts,
            'insurance_claims': insurance_claims,
            'claim_diff': claim_diff,
            'installment_stats': installment_stats,
        })
        
        return context
    
    def get_queryset(self):
        return Billing.objects.none()

