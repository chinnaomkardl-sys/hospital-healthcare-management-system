from django.urls import path
from . import views

app_name = 'reception'

urlpatterns = [
    path('register-patient/', views.ReceptionRegisterPatientView.as_view(), name='register_patient'),
    path('patient-registered/<str:patient_id>/', views.PatientRegisteredView.as_view(), name='patient_registered'),
    
    path('book-appointment/', views.ReceptionBookAppointmentView.as_view(), name='book_appointment'),
    path('appointment-confirmed/<str:appointment_id>/', views.AppointmentConfirmedView.as_view(), name='appointment_confirmed'),
    
    path('appointments/', views.ReceptionAppointmentListView.as_view(), name='appointment_list'),
    path('appointments/schedule/', views.ReceptionViewAppointmentScheduleView.as_view(), name='appointment_schedule'),
    path('appointments/<str:appointment_id>/update/', views.ReceptionUpdateAppointmentStatusView.as_view(), name='update_appointment'),
    
    path('search-patient/', views.ReceptionSearchPatientView.as_view(), name='search_patient'),
]
