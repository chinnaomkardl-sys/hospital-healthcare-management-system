from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Medical Reports
    path('medical-reports/', views.AdminMedicalReportListView.as_view(), name='medical_report_list'),
    path('medical-report/<int:report_id>/', views.MedicalReportDetailView.as_view(), name='medical_report_detail'),
    path('patient/<str:patient_id>/reports/', views.PatientMedicalReportListView.as_view(), name='patient_reports'),
    path('report/<int:report_id>/download/', views.DownloadMedicalReportView.as_view(), name='download_report'),
    
    # Prescriptions
    path('prescriptions/', views.DoctorPrescriptionListView.as_view(), name='prescription_list'),
    path('patient/<str:patient_id>/prescriptions/', views.PatientPrescriptionListView.as_view(), name='patient_prescriptions'),
]
