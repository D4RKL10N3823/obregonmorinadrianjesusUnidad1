import os
import requests
from django.conf import settings

class ApiError(Exception):
    pass

def verify_recaptcha(token: str) -> bool:
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY") or getattr(settings, 'RECAPTCHA_SECRET_KEY', None)
    if not secret_key:
        raise ApiError("RECAPTCHA_SECRET_KEY not set.")
    
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": secret_key, "response": token}
    )

    if not response.ok:
        raise ApiError(f"Google reCAPTCHA error: {response.status_code}")

    data = response.json()
    return data.get("success", False)
