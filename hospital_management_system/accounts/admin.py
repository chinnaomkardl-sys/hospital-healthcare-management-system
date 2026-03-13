from django.contrib import admin
from .models import CustomUser, Department, Doctor, Nurse, Receptionist, Patient

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'get_full_name', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'profile_picture')}),
        ('Address', {'fields': ('address', 'city', 'state')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role', {'fields': ('role', 'is_active_user')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head_doctor')
    search_fields = ('name', 'code')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'department', 'license_number', 'is_available')
    list_filter = ('specialization', 'department', 'is_available')
    search_fields = ('user__first_name', 'user__last_name', 'license_number')
    actions = ['delete_selected']


@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'shift', 'is_available')
    list_filter = ('department', 'shift', 'is_available')
    search_fields = ('user__first_name', 'user__last_name')
    actions = ['delete_selected']


@admin.register(Receptionist)
class ReceptionistAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id')
    actions = ['delete_selected']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'patient_id', 'assigned_doctor', 'admission_status')
    list_filter = ('admission_status', 'blood_group')
    search_fields = ('user__first_name', 'user__last_name', 'patient_id')
