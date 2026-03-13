from django.contrib import admin
from .models import Billing, Payment, InsuranceProvider, InsuranceClaim, InstallmentPlan, InstallmentPayment


@admin.register(InsuranceProvider)
class InsuranceProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_number', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = ['claim_id', 'patient', 'insurance_provider', 'claim_amount', 'status', 'submitted_date']
    list_filter = ['status', 'submitted_date', 'insurance_provider']
    search_fields = ['claim_id', 'patient__user__first_name', 'patient__user__last_name', 'policy_number']
    readonly_fields = ['claim_id', 'created_at', 'updated_at']


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ['plan_id', 'patient', 'total_amount', 'amount_paid', 'status', 'next_due_date']
    list_filter = ['status', 'created_at']
    search_fields = ['plan_id', 'patient__user__first_name', 'patient__user__last_name']
    readonly_fields = ['plan_id', 'created_at', 'updated_at']


@admin.register(InstallmentPayment)
class InstallmentPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'installment_plan', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['payment_id', 'installment_plan__plan_id']


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ['billing_id', 'patient', 'total_amount', 'amount_paid', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['billing_id', 'patient__user__first_name', 'patient__user__last_name', 'patient__patient_id']
    readonly_fields = ['billing_id', 'subtotal', 'tax', 'total_amount', 'created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'billing', 'amount', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['payment_id', 'billing__billing_id']

