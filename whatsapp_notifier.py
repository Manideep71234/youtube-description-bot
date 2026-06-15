import os
import requests
import urllib.parse

def send_whatsapp_message(text):
    phone_number = os.getenv("WHATSAPP_PHONE_NUMBER")
    api_key = os.getenv("WHATSAPP_API_KEY")

    if not phone_number or not api_key or phone_number == "+1234567890":
        print("WhatsApp configuration is missing. Cannot send notification.")
        return False

    # Format the phone number (remove + if exists)
    phone_number = phone_number.replace("+", "")
    
    # URL encode the message
    encoded_text = urllib.parse.quote(text)
    
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={encoded_text}&apikey={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("WhatsApp notification sent successfully!")
            return True
        else:
            print(f"Failed to send WhatsApp message. Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False
