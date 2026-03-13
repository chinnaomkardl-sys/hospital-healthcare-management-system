import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
sys.path.insert(0, 'C:/Users/Omkar/Desktop/hospital/hos/hospital_management_system')
django.setup()

from pharmacy.models import MedicineCategory, Supplier, Medicine
from billing.models import InsuranceProvider

print("Adding sample data to pharmacy and insurance...")

# Add categories
categories_data = [
    {'name': 'Analgesics', 'description': 'Pain relievers and fever reducers'},
    {'name': 'Antibiotics', 'description': 'Medicines that kill or stop bacteria'},
    {'name': 'Antipyretics', 'description': 'Fever reducing medicines'},
    {'name': 'Anti-inflammatory', 'description': 'Inflammation and swelling reducers'},
    {'name': 'Cardiovascular', 'description': 'Heart and blood pressure medicines'},
    {'name': 'Respiratory', 'description': 'Breathing and lung medicines'},
    {'name': 'Gastrointestinal', 'description': 'Stomach and digestive medicines'},
    {'name': 'Antihistamines', 'description': 'Allergy medicines'},
    {'name': 'Vitamins & Supplements', 'description': 'Nutritional supplements'},
    {'name': 'Diabetes', 'description': 'Blood sugar control medicines'},
]

for cat_data in categories_data:
    cat, created = MedicineCategory.objects.get_or_create(name=cat_data['name'], defaults={'description': cat_data['description']})
    if created:
        print(f'Created category: {cat.name}')

# Add suppliers
suppliers_data = [
    {'name': 'MedPharma Distributors', 'code': 'SUP-MP01', 'contact_person': 'John Smith', 'email': 'john@medpharma.com', 'phone': '+1-555-0101'},
    {'name': 'Global Health Supplies', 'code': 'SUP-GH02', 'contact_person': 'Sarah Johnson', 'email': 'sarah@globalhealth.com', 'phone': '+1-555-0102'},
    {'name': 'PharmaCare Inc', 'code': 'SUP-PC03', 'contact_person': 'Mike Williams', 'email': 'mike@pharmacare.com', 'phone': '+1-555-0103'},
    {'name': 'BioMed Solutions', 'code': 'SUP-BM04', 'contact_person': 'Emily Brown', 'email': 'emily@biomedsol.com', 'phone': '+1-555-0104'},
    {'name': 'Apex Pharmaceuticals', 'code': 'SUP-AP05', 'contact_person': 'David Lee', 'email': 'david@apexpharma.com', 'phone': '+1-555-0105'},
]

for sup_data in suppliers_data:
    sup, created = Supplier.objects.get_or_create(code=sup_data['code'], defaults={'name': sup_data['name'], 'contact_person': sup_data['contact_person'], 'email': sup_data['email'], 'phone': sup_data['phone'], 'is_active': True})
    if created:
        print(f'Created supplier: {sup.name}')

# Add medicines
today = date.today()
medicines_data = [
    {'name': 'Paracetamol 500mg', 'category': 'Analgesics', 'cost': 0.50, 'selling': 1.00, 'stock': 5000},
    {'name': 'Ibuprofen 400mg', 'category': 'Analgesics', 'cost': 0.80, 'selling': 1.50, 'stock': 3000},
    {'name': 'Aspirin 325mg', 'category': 'Analgesics', 'cost': 0.30, 'selling': 0.75, 'stock': 4500},
    {'name': 'Amoxicillin 500mg', 'category': 'Antibiotics', 'cost': 2.50, 'selling': 5.00, 'stock': 1500},
    {'name': 'Azithromycin 250mg', 'category': 'Antibiotics', 'cost': 5.00, 'selling': 10.00, 'stock': 800},
    {'name': 'Ciprofloxacin 500mg', 'category': 'Antibiotics', 'cost': 3.00, 'selling': 6.00, 'stock': 1200},
    {'name': 'Diclofenac 50mg', 'category': 'Anti-inflammatory', 'cost': 1.00, 'selling': 2.00, 'stock': 2500},
    {'name': 'Naproxen 250mg', 'category': 'Anti-inflammatory', 'cost': 1.50, 'selling': 3.00, 'stock': 1800},
    {'name': 'Amlodipine 5mg', 'category': 'Cardiovascular', 'cost': 1.00, 'selling': 2.50, 'stock': 3000},
    {'name': 'Metoprolol 50mg', 'category': 'Cardiovascular', 'cost': 2.00, 'selling': 4.00, 'stock': 2200},
    {'name': 'Losartan 50mg', 'category': 'Cardiovascular', 'cost': 1.50, 'selling': 3.50, 'stock': 2800},
    {'name': 'Cetirizine 10mg', 'category': 'Respiratory', 'cost': 0.50, 'selling': 1.25, 'stock': 4000},
    {'name': 'Loratadine 10mg', 'category': 'Respiratory', 'cost': 0.60, 'selling': 1.50, 'stock': 3500},
    {'name': 'Salbutamol Inhaler', 'category': 'Respiratory', 'cost': 8.00, 'selling': 15.00, 'stock': 200},
    {'name': 'Omeprazole 20mg', 'category': 'Gastrointestinal', 'cost': 1.00, 'selling': 2.50, 'stock': 3200},
    {'name': 'Pantoprazole 40mg', 'category': 'Gastrointestinal', 'cost': 2.50, 'selling': 5.00, 'stock': 1800},
    {'name': 'Antacid Syrup', 'category': 'Gastrointestinal', 'cost': 3.00, 'selling': 6.00, 'stock': 500},
    {'name': 'Vitamin C 500mg', 'category': 'Vitamins & Supplements', 'cost': 0.30, 'selling': 0.75, 'stock': 8000},
    {'name': 'Vitamin B Complex', 'category': 'Vitamins & Supplements', 'cost': 0.50, 'selling': 1.25, 'stock': 5000},
    {'name': 'Ferrous Sulfate', 'category': 'Vitamins & Supplements', 'cost': 0.25, 'selling': 0.60, 'stock': 4500},
    {'name': 'Metformin 500mg', 'category': 'Diabetes', 'cost': 0.80, 'selling': 2.00, 'stock': 4000},
    {'name': 'Glipizide 5mg', 'category': 'Diabetes', 'cost': 1.50, 'selling': 3.50, 'stock': 1500},
]

supplier = Supplier.objects.first()
for med_data in medicines_data:
    category = MedicineCategory.objects.get(name=med_data['category'])
    expiry = today + timedelta(days=365 + (hash(med_data['name']) % 365))
    code = f"MED-{med_data['name'][:3].upper()}-{abs(hash(med_data['name'])) % 1000:03d}"
    med, created = Medicine.objects.get_or_create(
        name=med_data['name'],
        defaults={
            'medicine_code': code,
            'category': category,
            'supplier': supplier,
            'generic_name': med_data['name'],
            'dosage': 'As directed',
            'unit': 'TABLET',
            'strength': '500mg',
            'cost_price': Decimal(str(med_data['cost'])),
            'selling_price': Decimal(str(med_data['selling'])),
            'current_stock': med_data['stock'],
            'minimum_stock_level': 50,
            'expiry_date': expiry,
            'status': 'ACTIVE',
            'requires_prescription': med_data['category'] in ['Antibiotics', 'Diabetes', 'Cardiovascular']
        }
    )
    if created:
        print(f'Created medicine: {med.name}')

# Add insurance providers
insurance_data = [
    {'name': 'Blue Cross Blue Shield', 'code': 'INS-BCBS', 'contact': '+1-800-123-4567', 'email': 'claims@bcbs.com'},
    {'name': 'Aetna Health Insurance', 'code': 'INS-AETNA', 'contact': '+1-800-234-5678', 'email': 'claims@aetna.com'},
    {'name': 'UnitedHealthcare', 'code': 'INS-UHC', 'contact': '+1-800-345-6789', 'email': 'claims@uhc.com'},
    {'name': 'Cigna Insurance', 'code': 'INS-CIGNA', 'contact': '+1-800-456-7890', 'email': 'claims@cigna.com'},
    {'name': 'Humana Insurance', 'code': 'INS-HUMANA', 'contact': '+1-800-567-8901', 'email': 'claims@humana.com'},
    {'name': 'Kaiser Permanente', 'code': 'INS-KAISER', 'contact': '+1-800-678-9012', 'email': 'claims@kaiser.com'},
    {'name': 'Medicare', 'code': 'INS-MEDICARE', 'contact': '+1-800-789-0123', 'email': 'claims@medicare.gov'},
    {'name': 'Medicaid', 'code': 'INS-MEDICAID', 'contact': '+1-800-890-1234', 'email': 'claims@medicaid.gov'},
]

for ins_data in insurance_data:
    ins, created = InsuranceProvider.objects.get_or_create(code=ins_data['code'], defaults={'name': ins_data['name'], 'contact_number': ins_data['contact'], 'email': ins_data['email'], 'is_active': True})
    if created:
        print(f'Created insurance: {ins.name}')

print(f'\nTotal Categories: {MedicineCategory.objects.count()}')
print(f'Total Suppliers: {Supplier.objects.count()}')
print(f'Total Medicines: {Medicine.objects.count()}')
print(f'Total Insurance Providers: {InsuranceProvider.objects.count()}')
print('\nDone! Sample data added successfully.')
