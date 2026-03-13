from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    # Patient self-service views (must come before generic patient_id pattern)
    path('book-appointment/', views.PatientBookAppointmentView.as_view(), name='book_appointment'),
    path('appointment-confirmed/<str:appointment_id>/', views.PatientAppointmentConfirmedView.as_view(), name='appointment_confirmed'),
    
    # Prescription refill
    path('prescription-refill/', views.PatientPrescriptionRefillView.as_view(), name='prescription_refill'),
    
    # Billing & Payment
    path('bills/', views.PatientBillingListView.as_view(), name='patient_bills'),
    path('bills/<str:billing_id>/pay/', views.PatientMakePaymentView.as_view(), name='make_payment'),
    
    # Teleconsultation
    path('teleconsultation/', views.PatientTeleconsultationView.as_view(), name='request_teleconsultation'),
    path('teleconsultations/', views.PatientTeleconsultationListView.as_view(), name='teleconsultation_list'),
    
    # Admin/Reception views
    path('list/', views.AdminPatientListView.as_view(), name='patient_list'),
    path('search/', views.AdminSearchPatientView.as_view(), name='search_patients'),
    
    # Patient detail views (must come after specific patterns)
    path('<str:patient_id>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('<str:patient_id>/assign-doctor/', views.AdminAssignDoctorView.as_view(), name='assign_doctor'),
]
