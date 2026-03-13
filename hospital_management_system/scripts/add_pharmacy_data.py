"""
Script to add sample pharmacy data and insurance providers
Run with: python manage.py runscript add_pharmacy_data
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_management_system.settings')
django.setup()

from pharmacy.models import MedicineCategory, Supplier, Medicine
from billing.models import InsuranceProvider


def run():
    print("Adding pharmacy data and insurance providers...")
    
    # ===== MEDICINE CATEGORIES =====
    categories_data = [
        {"name": "Analgesics", "description": "Pain relievers and fever reducers"},
        {"name": "Antibiotics", "description": "Medicines that kill or stop bacteria"},
        {"name": "Antipyretics", "description": "Fever reducing medicines"},
        {"name": "Anti-inflammatory", "description": "Inflammation and swelling reducers"},
        {"name": "Cardiovascular", "description": "Heart and blood pressure medicines"},
        {"name": "Respiratory", "description": "Breathing and lung medicines"},
        {"name": "Gastrointestinal", "description": "Stomach and digestive medicines"},
        {"name": "Antihistamines", "description": "Allergy medicines"},
        {"name": "Vitamins & Supplements", "description": "Nutritional supplements"},
        {"name": "Diabetes", "description": "Blood sugar control medicines"},
    ]
    
    categories = []
    for cat_data in categories_data:
        cat, created = MedicineCategory.objects.get_or_create(
            name=cat_data["name"],
            defaults={"description": cat_data["description"]}
        )
        categories.append(cat)
        if created:
            print(f"  Created category: {cat.name}")
    
    # ===== SUPPLIERS =====
    suppliers_data = [
        {"name": "MedPharma Distributors", "code": "SUP-MP01", "contact_person": "John Smith", "email": "john@medpharma.com", "phone": "+1-555-0101"},
        {"name": "Global Health Supplies", "code": "SUP-GH02", "contact_person": "Sarah Johnson", "email": "sarah@globalhealth.com", "phone": "+1-555-0102"},
        {"name": "PharmaCare Inc", "code": "SUP-PC03", "contact_person": "Mike Williams", "email": "mike@pharmacare.com", "phone": "+1-555-0103"},
        {"name": "BioMed Solutions", "code": "SUP-BM04", "contact_person": "Emily Brown", "email": "emily@biomedsol.com", "phone": "+1-555-0104"},
        {"name": "Apex Pharmaceuticals", "code": "SUP-AP05", "contact_person": "David Lee", "email": "david@apexpharma.com", "phone": "+1-555-0105"},
    ]
    
    suppliers = []
    for sup_data in suppliers_data:
        sup, created = Supplier.objects.get_or_create(
            code=sup_data["code"],
            defaults={
                "name": sup_data["name"],
                "contact_person": sup_data["contact_person"],
                "email": sup_data["email"],
                "phone": sup_data["phone"],
                "is_active": True
            }
        )
        suppliers.append(sup)
        if created:
            print(f"  Created supplier: {sup.name}")
    
    # ===== MEDICINES =====
    medicines_data = [
        # Analgesics
        {"name": "Paracetamol 500mg", "generic_name": "Acetaminophen", "category": "Analgesics", "dosage": "500mg", "unit": "TABLET", "strength": "500mg", "cost_price": 0.50, "selling_price": 1.00, "current_stock": 5000, "minimum_stock_level": 100, "requires_prescription": False},
        {"name": "Ibuprofen 400mg", "generic_name": "Ibuprofen", "category": "Analgesics", "dosage": "400mg", "unit": "TABLET", "strength": "400mg", "cost_price": 0.80, "selling_price": 1.50, "current_stock": 3000, "minimum_stock_level": 100, "requires_prescription": False},
        {"name": "Aspirin 325mg", "generic_name": "Acetylsalicylic Acid", "category": "Analgesics", "dosage": "325mg", "unit": "TABLET", "strength": "325mg", "cost_price": 0.30, "selling_price": 0.75, "current_stock": 4500, "minimum_stock_level": 100, "requires_prescription": False},
        
        # Antibiotics
        {"name": "Amoxicillin 500mg", "generic_name": "Amoxicillin Trihydrate", "category": "Antibiotics", "dosage": "500mg", "unit": "CAPSULE", "strength": "500mg", "cost_price": 2.50, "selling_price": 5.00, "current_stock": 1500, "minimum_stock_level": 50, "requires_prescription": True},
        {"name": "Azithromycin 250mg", "generic_name": "Azithromycin Dihydrate", "category": "Antibiotics", "dosage": "250mg", "unit": "TABLET", "strength": "250mg", "cost_price": 5.00, "selling_price": 10.00, "current_stock": 800, "minimum_stock_level": 50, "requires_prescription": True},
        {"name": "Ciprofloxacin 500mg", "generic_name": "Ciprofloxacin HCl", "category": "Antibiotics", "dosage": "500mg", "unit": "TABLET", "strength": "500mg", "cost_price": 3.00, "selling_price": 6.00, "current_stock": 1200, "minimum_stock_level": 50, "requires_prescription": True},
        
        # Anti-inflammatory
        {"name": "Diclofenac 50mg", "generic_name": "Diclofenac Sodium", "category": "Anti-inflammatory", "dosage": "50mg", "unit": "TABLET", "strength": "50mg", "cost_price": 1.00, "selling_price": 2.00, "current_stock": 2500, "minimum_stock_level": 75, "requires_prescription": False},
        {"name": "Naproxen 250mg", "generic_name": "Naproxen Sodium", "category": "Anti-inflammatory", "dosage": "250mg", "unit": "TABLET", "strength": "250mg", "cost_price": 1.50, "selling_price": 3.00, "current_stock": 1800, "minimum_stock_level": 75, "requires_prescription": False},
        
        # Cardiovascular
        {"name": "Amlodipine 5mg", "generic_name": "Amlodipine Besylate", "category": "Cardiovascular", "dosage": "5mg", "unit": "TABLET", "strength": "5mg", "cost_price": 1.00, "selling_price": 2.50, "current_stock": 3000, "minimum_stock_level": 100, "requires_prescription": True},
        {"name": "Metoprolol 50mg", "generic_name": "Metoprolol Tartrate", "category": "Cardiovascular", "dosage": "50mg", "unit": "TABLET", "strength": "50mg", "cost_price": 2.00, "selling_price": 4.00, "current_stock": 2200, "minimum_stock_level": 100, "requires_prescription": True},
        {"name": "Losartan 50mg", "generic_name": "Losartan Potassium", "category": "Cardiovascular", "dosage": "50mg", "unit": "TABLET", "strength": "50mg", "cost_price": 1.50, "selling_price": 3.50, "current_stock": 2800, "minimum_stock_level": 100, "requires_prescription": True},
        
        # Respiratory
        {"name": "Cetirizine 10mg", "generic_name": "Cetirizine Dihydrochloride", "category": "Respiratory", "dosage": "10mg", "unit": "TABLET", "strength": "10mg", "cost_price": 0.50, "selling_price": 1.25, "current_stock": 4000, "minimum_stock_level": 100, "requires_prescription": False},
        {"name": "Loratadine 10mg", "generic_name": "Loratadine", "category": "Respiratory", "dosage": "10mg", "unit": "TABLET", "strength": "10mg", "cost_price": 0.60, "selling_price": 1.50, "current_stock": 3500, "minimum_stock_level": 100, "requires_prescription": False},
        {"name": "Salbutamol Inhaler", "generic_name": "Salbutamol Sulfate", "category": "Respiratory", "dosage": "100mcg", "unit": "INHALER", "strength": "100mcg", "cost_price": 8.00, "selling_price": 15.00, "current_stock": 200, "minimum_stock_level": 20, "requires_prescription": True},
        
        # Gastrointestinal
        {"name": "Omeprazole 20mg", "generic_name": "Omeprazole", "category": "Gastrointestinal", "dosage": "20mg", "unit": "CAPSULE", "strength": "20mg", "cost_price": 1.00, "selling_price": 2.50, "current_stock": 3200, "minimum_stock_level": 100, "requires_prescription": False},
        {"name": "Pantoprazole 40mg", "generic_name": "Pantoprazole Magnesium", "category": "Gastrointestinal", "dosage": "40mg", "unit": "TABLET", "strength": "40mg", "cost_price": 2.50, "selling_price": 5.00, "current_stock": 1800, "minimum_stock_level": 75, "requires_prescription": True},
        {"name": "Antacid Syrup", "generic_name": "Aluminum Hydroxide + Magnesium Hydroxide", "category": "Gastrointestinal", "dosage": "10ml", "unit": "SYRUP", "strength": "200mg/200mg per 5ml", "cost_price": 3.00, "selling_price": 6.00, "current_stock": 500, "minimum_stock_level": 50, "requires_prescription": False},
        
        # Vitamins & Supplements
        {"name": "Vitamin C 500mg", "generic_name": "Ascorbic Acid", "category": "Vitamins & Supplements", "dosage": "500mg", "unit": "TABLET", "strength": "500mg", "cost_price": 0.30, "selling_price": 0.75, "current_stock": 8000, "minimum_stock_level": 200, "requires_prescription": False},
        {"name": "Vitamin B Complex", "generic_name": "Vitamin B Complex", "category": "Vitamins & Supplements", "dosage": "1 tablet", "unit": "TABLET", "strength": "B1+B2+B3+B5+B6", "cost_price": 0.50, "selling_price": 1.25, "current_stock": 5000, "minimum_stock_level": 150, "requires_prescription": False},
        {"name": "Ferrous Sulfate", "generic_name": "Ferrous Sulfate", "category": "Vitamins & Supplements", "dosage": "325mg", "unit": "TABLET", "strength": "65mg Iron", "cost_price": 0.25, "selling_price": 0.60, "current_stock": 4500, "minimum_stock_level": 100, "requires_prescription": False},
        
        # Diabetes
        {"name": "Metformin 500mg", "generic_name": "Metformin HCl", "category": "Diabetes", "dosage": "500mg", "unit": "TABLET", "strength": "500mg", "cost_price": 0.80, "selling_price": 2.00, "current_stock": 4000, "minimum_stock_level": 100, "requires_prescription": True},
        {"name": "Glipizide 5mg", "generic_name": "Glipizide", "category": "Diabetes", "dosage": "5mg", "unit": "TABLET", "strength": "5mg", "cost_price": 1.50, "selling_price": 3.50, "current_stock": 1500, "minimum_stock_level": 50, "requires_prescription": True},
        
        # Antipyretics
        {"name": "Nimulid MD", "generic_name": "Nimesulide", "category": "Antipyretics", "dosage": "100mg", "unit": "TABLET", "strength": "100mg", "cost_price": 2.00, "selling_price": 4.00, "current_stock": 2000, "minimum_stock_level": 75, "requires_prescription": True},
    ]
    
    # Add expiry dates (some expiring soon, some later)
    today = date.today()
    
    for med_data in medicines_data:
        category = next((c for c in categories if c.name == med_data["category"]), categories[0])
        supplier = suppliers[0] if suppliers else None
        
        # Generate expiry date
        if med_data.get("current_stock", 0) > 2000:
            # Good stock - expiry in 1-2 years
            days_until_expiry = 365 + (hash(med_data["name"]) % 365)
        else:
            # Low stock - expiry in 6-12 months
            days_until_expiry = 180 + (hash(med_data["name"]) % 180)
        
        expiry_date = today + timedelta(days=days_until_expiry)
        
        med, created = Medicine.objects.get_or_create(
            medicine_code=f"MED-{med_data['name'][:3].upper()}-{hash(med_data['name']) % 1000:03d}",
            defaults={
                "name": med_data["name"],
                "generic_name": med_data["generic_name"],
                "category": category,
                "supplier": supplier,
                "dosage": med_data["dosage"],
                "unit": med_data["unit"],
                "strength": med_data["strength"],
                "cost_price": Decimal(str(med_data["cost_price"])),
                "selling_price": Decimal(str(med_data["selling_price"])),
                "current_stock": med_data.get("current_stock", 100),
                "minimum_stock_level": med_data.get("minimum_stock_level", 10),
                "expiry_date": expiry_date,
                "status": "ACTIVE",
                "requires_prescription": med_data.get("requires_prescription", False)
            }
        )
        if created:
            print(f"  Created medicine: {med.name}")
    
    print(f"\n  Total Categories: {MedicineCategory.objects.count()}")
    print(f"  Total Suppliers: {Supplier.objects.count()}")
    print(f"  Total Medicines: {Medicine.objects.count()}")
    
    # ===== INSURANCE PROVIDERS =====
    print("\nAdding Insurance Providers...")
    
    insurance_data = [
        {"name": "Blue Cross Blue Shield", "code": "INS-BCBS", "contact_number": "+1-800-123-4567", "email": "claims@bcbs.com"},
        {"name": "Aetna Health Insurance", "code": "INS-AETNA", "contact_number": "+1-800-234-5678", "email": "claims@aetna.com"},
        {"name": "UnitedHealthcare", "code": "INS-UHC", "contact_number": "+1-800-345-6789", "email": "claims@uhc.com"},
        {"name": "Cigna Insurance", "code": "INS-CIGNA", "contact_number": "+1-800-456-7890", "email": "claims@cigna.com"},
        {"name": "Humana Insurance", "code": "INS-HUMANA", "contact_number": "+1-800-567-8901", "email": "claims@humana.com"},
        {"name": "Kaiser Permanente", "code": "INS-KAISER", "contact_number": "+1-800-678-9012", "email": "claims@kaiser.com"},
        {"name": "Medicare", "code": "INS-MEDICARE", "contact_number": "+1-800-789-0123", "email": "claims@medicare.gov"},
        {"name": "Medicaid", "code": "INS-MEDICAID", "contact_number": "+1-800-890-1234", "email": "claims@medicaid.gov"},
    ]
    
    for ins_data in insurance_data:
        ins, created = InsuranceProvider.objects.get_or_create(
            code=ins_data["code"],
            defaults={
                "name": ins_data["name"],
                "contact_number": ins_data["contact_number"],
                "email": ins_data["email"],
                "is_active": True
            }
        )
        if created:
            print(f"  Created insurance provider: {ins.name}")
    
    print(f"\n  Total Insurance Providers: {InsuranceProvider.objects.count()}")
    
    print("\n✅ Sample data added successfully!")
    print("You can now access the pharmacy portal with real data.")

