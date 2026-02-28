"""
Security Utilities for Y.S.M Education Management System
Implements secure password generation, file validation, and input sanitization
"""

import secrets
import string
import re
import mimetypes
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email


def generate_secure_password(length=16):
    """
    Generate cryptographically secure password
    SECURITY FIX #9: Replace random.choice() with secrets.choice()
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Ensure password has at least one of each type
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()" for c in password)
    
    if not (has_upper and has_lower and has_digit and has_special):
        # Regenerate if requirements not met
        return generate_secure_password(length)
    
    return password


def generate_secure_otp(length=6):
    """
    Generate cryptographically secure OTP
    SECURITY FIX #25: Use secrets for OTP generation
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_transaction_id():
    """
    Generate secure transaction ID
    SECURITY FIX #17: Use full entropy tokens instead of truncated UUIDs
    """
    return secrets.token_urlsafe(32)


def validate_file_upload(file, allowed_types=None, max_size_mb=5):
    """
    Validate uploaded files for security
    SECURITY FIX #5: File upload validation
    
    Args:
        file: UploadedFile object
        allowed_types: List of allowed MIME types (default: images only)
        max_size_mb: Maximum file size in MB
    """
    if allowed_types is None:
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    
    # 1. Size validation
    max_size = max_size_mb * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(f"File size exceeds {max_size_mb}MB limit")
    
    # 2. MIME type verification
    # Using Django's UploadedFile content_type and mimetypes fallback
    content_type = getattr(file, 'content_type', None)
    
    if not content_type:
        content_type, _ = mimetypes.guess_type(file.name)
        
    if content_type not in allowed_types:
        raise ValidationError(f"Invalid file type: {content_type}. Allowed types: {', '.join(allowed_types)}")
    
    # 3. Deep Image verification (Pillow)
    if content_type and content_type.startswith('image/'):
        try:
            # Re-verify with Pillow to ensure it's a valid image and not a polyglot file
            file.seek(0)
            img = Image.open(file)
            img.verify()
            
            # Re-open for format check (verify closes the file)
            file.seek(0)
            img = Image.open(file)
            
            # Dimension checks to prevent Zip bomb/pixel bomb style DOS
            if img.size[0] > 10000 or img.size[1] > 10000:
                raise ValidationError("Image dimensions too large (max 10000x10000)")
                
            file.seek(0)  # Final reset
            
        except Exception as e:
            raise ValidationError(f"Corrupted or invalid image file: {str(e)}")
    
    return file


def sanitize_search_query(query, max_length=100):
    """
    Sanitize user search input
    SECURITY FIX #3: SQL Injection prevention
    
    Args:
        query: User search input
        max_length: Maximum allowed length
        
    Returns:
        Sanitized query string
    """
    if not query:
        return ""
    
    # Remove SQL metacharacters and limit length
    sanitized = re.sub(r'[^\w\s-]', '', str(query))[:max_length]
    
    # Remove excessive whitespace
    sanitized = ' '.join(sanitized.split())
    
    return sanitized


def validate_email_safe(email):
    """
    Validate email and prevent header injection
    SECURITY FIX #11: Email header injection prevention
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError("Email address is required")
    
    # Check for newlines (header injection attempt)
    if '\n' in email or '\r' in email:
        raise ValidationError("Invalid email address format")
    
    # Use Django's validator
    django_validate_email(email)
    
    # Additional length check
    if len(email) > 254:  # RFC 5321
        raise ValidationError("Email address too long")
    
    return True


def sanitize_subject_line(subject, max_length=200):
    """
    Sanitize email subject line
    SECURITY FIX #11: Prevent email header injection
    """
    if not subject:
        return ""
    
    # Remove newlines and carriage returns
    sanitized = subject.replace('\n', '').replace('\r', '')
    
    # Limit length
    return sanitized[:max_length]


def verify_payment_signature(request, secret_key):
    """
    Verify payment webhook signature
    SECURITY FIX #4: CSRF protection for payment endpoints
    
    Args:
        request: Django request object
        secret_key: Webhook secret key
        
    Returns:
        bool: True if signature is valid
        
    Raises:
        ValidationError: If signature is invalid
    """
    import hmac
    import hashlib
    
    signature = request.headers.get('X-Payment-Signature', '')
    if not signature:
        raise ValidationError("Missing payment signature")
    
    payload = request.body
    expected = hmac.new(
        secret_key.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        raise ValidationError("Invalid payment signature")
    
    return True


# Replace the old generate_password function
generate_password = generate_secure_password
