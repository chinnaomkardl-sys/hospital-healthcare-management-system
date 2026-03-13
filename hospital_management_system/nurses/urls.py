from django.urls import path
from . import views

app_name = 'nurses'

urlpatterns = [
    path('list/', views.AdminNurseListView.as_view(), name='nurse_list'),
    path('<int:nurse_id>/', views.NurseDetailView.as_view(), name='nurse_detail'),
    path('patients/', views.NursePatientListView.as_view(), name='view_patients'),
    path('patient/<str:patient_id>/vitals/', views.NurseRecordVitalsView.as_view(), name='record_vitals'),
    path('patient/<str:patient_id>/vitals-history/', views.NurseViewVitalsHistoryView.as_view(), name='vitals_history'),
]
