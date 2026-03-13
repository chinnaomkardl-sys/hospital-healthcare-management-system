from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Billing URLs
    path('', views.BillingListView.as_view(), name='billing_list'),
    path('create/', views.CreateBillingView.as_view(), name='create_billing'),
    path('<int:pk>/', views.BillingDetailView.as_view(), name='billing_detail'),
    path('<int:pk>/payment/', views.AddPaymentView.as_view(), name='add_payment'),
    path('patient/<str:patient_id>/', views.PatientBillingView.as_view(), name='patient_billing'),
    
    # PDF Invoice
    path('<int:pk>/pdf/', views.generate_invoice_pdf, name='generate_pdf'),
    
    # Payment Gateway
    path('<int:pk>/payment-gateway/', views.payment_gateway_view, name='payment_gateway'),
    path('<int:pk>/payment-callback/', views.payment_callback, name='payment_callback'),
    
    # Insurance Claims
    path('insurance-claims/', views.InsuranceClaimListView.as_view(), name='insurance_claim_list'),
    path('insurance-claims/create/', views.CreateInsuranceClaimView.as_view(), name='create_insurance_claim'),
    path('insurance-claims/<int:pk>/', views.InsuranceClaimDetailView.as_view(), name='insurance_claim_detail'),
    path('insurance-claims/<int:pk>/update/', views.UpdateInsuranceClaimView.as_view(), name='update_insurance_claim'),
    
    # Insurance Providers
    path('insurance-providers/', views.InsuranceProviderListView.as_view(), name='insurance_provider_list'),
    path('insurance-providers/create/', views.CreateInsuranceProviderView.as_view(), name='create_insurance_provider'),
    
    # Installment Plans
    path('installments/', views.InstallmentPlanListView.as_view(), name='installment_plan_list'),
    path('installments/create/', views.CreateInstallmentPlanView.as_view(), name='create_installment_plan'),
    path('installments/<int:pk>/', views.InstallmentPlanDetailView.as_view(), name='installment_plan_detail'),
    path('installments/<int:pk>/payment/', views.AddInstallmentPaymentView.as_view(), name='add_installment_payment'),
    
    # Financial Reports
    path('reports/', views.FinancialReportsView.as_view(), name='financial_reports'),
]

