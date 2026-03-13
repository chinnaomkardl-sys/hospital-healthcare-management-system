from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('doctor/', views.DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('nurse/', views.NurseDashboardView.as_view(), name='nurse_dashboard'),
    path('receptionist/', views.ReceptionistDashboardView.as_view(), name='receptionist_dashboard'),
    path('patient/', views.PatientDashboardView.as_view(), name='patient_dashboard'),
]
