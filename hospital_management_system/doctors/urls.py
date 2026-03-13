from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('list/', views.AdminDoctorListView.as_view(), name='doctor_list'),
    path('<int:doctor_id>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('appointments/', views.DoctorViewAppointmentsView.as_view(), name='view_appointments'),
    path('patient/<str:patient_id>/diagnosis/', views.DoctorAddDiagnosisView.as_view(), name='add_diagnosis'),
    path('patient/<str:patient_id>/prescription/', views.DoctorPharmacyPrescriptionView.as_view(), name='add_prescription'),
    path('patient/<str:patient_id>/report/', views.DoctorUploadMedicalReportView.as_view(), name='upload_report'),
    path('report/<int:report_id>/update/', views.DoctorUpdateTreatmentNotesView.as_view(), name='update_treatment_notes'),
]
