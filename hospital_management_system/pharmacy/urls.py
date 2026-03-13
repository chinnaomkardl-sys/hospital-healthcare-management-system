from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'pharmacy'

urlpatterns = [
    # Login/Logout
    path('login/', views.pharmacy_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='pharmacy:login'), name='logout'),
    
    # Dashboard
path('', views.pharmacy_login, name='home'),
path('dashboard/', views.PharmacyDashboardView.as_view(), name='dashboard'),
    path('alerts/', views.medicine_alerts, name='medicine_alerts'),
    
    # Medicine Inventory
    path('medicines/', views.MedicineListView.as_view(), name='medicine_list'),
    path('medicines/create/', views.CreateMedicineView.as_view(), name='create_medicine'),
    path('medicines/<int:pk>/', views.MedicineDetailView.as_view(), name='medicine_detail'),
    path('medicines/<int:pk>/update/', views.UpdateMedicineView.as_view(), name='update_medicine'),
    path('medicines/<int:pk>/update-stock/', views.update_stock, name='update_stock'),
    path('medicines/search/', views.medicine_search, name='medicine_search'),
    path('medicines/<int:pk>/check/', views.check_availability, name='check_availability'),
    
    # Medicine Categories
    path('categories/', views.MedicineCategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CreateMedicineCategoryView.as_view(), name='create_category'),
    
    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', views.CreateSupplierView.as_view(), name='create_supplier'),
    
    # Prescriptions (E-Prescription to Pharmacy)
    path('prescriptions/', views.PrescriptionListView.as_view(), name='prescription_list'),
    path('prescriptions/create/', views.CreatePrescriptionView.as_view(), name='create_prescription'),
    path('prescriptions/<int:pk>/', views.PrescriptionDetailView.as_view(), name='prescription_detail'),
    path('prescriptions/<int:pk>/dispense/', views.dispense_prescription, name='dispense_prescription'),
    
    # Medicine Requests
    path('requests/', views.MedicineRequestListView.as_view(), name='medicine_request_list'),
    path('requests/create/', views.CreateMedicineRequestView.as_view(), name='create_medicine_request'),
    path('requests/<int:pk>/', views.MedicineRequestDetailView.as_view(), name='medicine_request_detail'),
    path('requests/<int:pk>/approve/', views.approve_medicine_request, name='approve_medicine_request'),
    
    # Purchase Orders
    path('purchase-orders/', views.PurchaseOrderListView.as_view(), name='purchase_order_list'),
    path('purchase-orders/create/', views.CreatePurchaseOrderView.as_view(), name='create_purchase_order'),
    path('purchase-orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='purchase_order_detail'),
    path('purchase-orders/<int:pk>/receive/', views.receive_purchase_order, name='receive_purchase_order'),
    
    # Reports
    path('reports/', views.pharmacy_report, name='pharmacy_report'),
]

