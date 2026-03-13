import json
import time
import re
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Try to import Gemini, but make it optional
try:
    import google.generativeai as genai
    from django.conf import settings
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# Local knowledge base for fallback responses
LOCAL_KNOWLEDGE_BASE = {
    # Greetings
    r'hello|hi|hey|greetings': [
        "Hello! Welcome to our Hospital Management System. I'm here to help you navigate and get information about our services. How can I assist you today?",
        "Hi there! I'm your AI assistant for this hospital system. Whether you need help with appointments, patient records, or general hospital information, I'm here to help!",
        "Welcome! I'm glad you're here. What would you like to know about our hospital services?"
    ],
    
    # Appointment related
    r'appointment|book|schedule|reserve': [
        "To book an appointment, please login to your account and go to the Reception section, or contact our reception desk directly.",
        "You can book appointments through the Reception portal after logging in. Our staff is also available to help you schedule appointments.",
        "For appointments, please use the 'Book Appointment' feature in your dashboard or visit the reception desk."
    ],
    
    # Patient records
    r'record|history|medical|report|prescription': [
        "Patient records and medical history can be accessed through the Patients section in your dashboard (for authorized staff) or through your patient portal.",
        "To view your medical records, please login to your patient account and navigate to the Medical Reports section.",
        "Medical reports and prescriptions are available in the Reports section of your dashboard."
    ],
    
    # Doctors
    r'doctor|physician|consultant|specialist': [
        "Our hospital has experienced doctors across various specialties. You can view our doctor list in the Doctors section.",
        "To see a doctor, please book an appointment through the reception. Our doctors are available for consultations during hospital hours.",
        "You can find doctor information in the 'Manage Doctors' section (for staff) or ask at reception."
    ],
    
    # Emergency
    r'emergency|urgent|critical|ambulance': [
        "For medical emergencies, please call our emergency hotline or go to our Emergency Department immediately.",
        "In case of emergency, please dial the hospital emergency number or visit the Emergency Room right away.",
        "Our emergency department is available 24/7 for critical medical situations."
    ],
    
    # Billing
    r'bill|payment|charge|cost|price|fee': [
        "For billing inquiries, please visit the Billing section in your dashboard or contact our billing department.",
        "You can view and pay bills through the Billing section after logging into your account.",
        "For cost estimates or insurance queries, please contact our billing department directly."
    ],
    
    # Working hours
    r'hour|time|open|close|available': [
        "Our hospital operates 24/7 for emergency services. Regular outpatient services are available from 8 AM to 8 PM.",
        "Hospital visiting hours are typically from 8 AM to 8 PM. Emergency services are available round the clock.",
        "Our reception is open from 8:00 AM to 8:00 PM, seven days a week."
    ],
    
    # Location
    r'location|address|direction|map|where': [
        "Our hospital is located at the main healthcare district. You can find directions on the hospital's website or contact reception.",
        "For directions to our hospital, please visit the Contact section on our website or call reception for assistance.",
        "We're situated in the central healthcare zone. Use our hospital map or ask for directions at the information desk."
    ],
    
    # Contact
    r'contact|phone|call|email|reach': [
        "You can contact our hospital through the contact information provided in the website footer or by calling reception.",
        "For general inquiries, please call our reception. For specific departments, check the directory in our website.",
        "You can reach us by phone, email, or visit the reception desk in person."
    ],
    
    # Login/Registration
    r'login|signin|register|signup|account': [
        "You can login through the role selection page. Choose your role (Patient, Doctor, Nurse, Receptionist, Admin) and enter your credentials.",
        "To create an account, click on 'Register' and choose your role. Patients can self-register, while staff accounts are created by administrators.",
        "For login issues, please contact your system administrator or use the forgot password option."
    ],
    
    # Password
    r'password|forgot|reset|change': [
        "For password issues, use the forgot password feature on the login page or contact your administrator.",
        "If you've forgotten your password, click on 'Forgot Password' on the login page to reset it.",
        "Password reset can be done through the login page or by contacting system support."
    ],
    
    # Services
    r'service|treatment|care|surgery|procedure': [
        "Our hospital offers a wide range of medical services including general medicine, surgery, cardiology, orthopedics, and more.",
        "We provide comprehensive healthcare services. Please check our services section or contact reception for specific treatments.",
        "From routine checkups to advanced surgeries, our hospital is equipped to handle various medical needs."
    ],
    
    # Thank you
    r'thank|thanks|appreciate': [
        "You're welcome! Is there anything else I can help you with?",
        "My pleasure! Feel free to ask if you have more questions.",
        "Happy to help! Let me know if you need any other assistance."
    ],
}


def get_knowledge_base_response(user_message):
    """Get a response from the local knowledge base based on user message."""
    user_message_lower = user_message.lower()
    
    for pattern, responses in LOCAL_KNOWLEDGE_BASE.items():
        if re.search(pattern, user_message_lower):
            return random.choice(responses)
    
    # Default fallback response
    return "I'm here to help with your hospital management system queries. You can ask me about appointments, patient records, doctors, billing, services, or any other general hospital information. How can I assist you?"


@csrf_exempt
@require_http_methods(["POST"])
def gemini_chat(request):
    """
    Chat view that uses Google Gemini API if available,
    otherwise falls back to local knowledge base.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        response_text = ""
        
        # Try to use Gemini if available
        if GEMINI_AVAILABLE:
            try:
                # Configure the Gemini API
                api_key = getattr(settings, 'GEMINI_API_KEY', None)
                if api_key:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-pro')
                    
                    # Add context about the hospital system
                    context = """You are a helpful AI assistant for a Hospital Management System. 
                    You should help users with:
                    - Booking and managing appointments
                    - Patient record information
                    - Doctor information and specialties
                    - Billing and payment inquiries
                    - Hospital services and facilities
                    - General hospital information
                    
                    Be friendly, professional, and concise in your responses."""
                    
                    full_prompt = f"{context}\n\nUser: {user_message}\nAssistant:"
                    response = model.generate_content(full_prompt)
                    response_text = response.text
                else:
                    # No API key, use knowledge base
                    response_text = get_knowledge_base_response(user_message)
            except Exception as e:
                # If Gemini fails, fall back to knowledge base
                print(f"Gemini API error: {e}")
                response_text = get_knowledge_base_response(user_message)
        else:
            # Gemini not available, use knowledge base
            response_text = get_knowledge_base_response(user_message)
        
        return JsonResponse({
            'response': response_text,
            'source': 'gemini' if GEMINI_AVAILABLE else 'knowledge_base'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """
    Simple health check endpoint to verify the chat service is running.
    """
    return JsonResponse({
        'status': 'healthy',
        'gemini_available': GEMINI_AVAILABLE,
        'service': 'hospital_chatbot'
    })

