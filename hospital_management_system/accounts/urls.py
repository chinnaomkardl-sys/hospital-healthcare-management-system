from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('role-choice/', views.RoleChoiceView.as_view(), name='role_choice'),
    path('login/<str:role>/', views.RoleLoginView.as_view(), name='login'),
    path('login/', RedirectView.as_view(url='/accounts/role-choice/', permanent=False), name='login_default'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Registration
    path('admin-register/', views.AdminRegisterView.as_view(), name='admin_register'),
    path('doctor-register/', views.DoctorRegisterView.as_view(), name='doctor_register'),
    path('nurse-register/', views.NurseRegisterView.as_view(), name='nurse_register'),
    path('receptionist-register/', views.ReceptionistRegisterView.as_view(), name='receptionist_register'),
    path('pharmacist-register/', views.PharmacistRegisterView.as_view(), name='pharmacist_register'),
    path('patient-register/', views.PatientRegisterView.as_view(), name='patient_register'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
]
