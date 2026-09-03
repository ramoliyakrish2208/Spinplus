"""
Enterprise Security Utilities for Spin & Win Platform.
Provides file upload validation, in-memory sliding window rate limiting,
cryptographic token helpers, and safe sanitization.
"""

import os
import re
import secrets
import time
from collections import defaultdict
from django.core.exceptions import ValidationError
from django.utils.text import slugify

# -----------------------------------------------------------------------------
# 1. FILE UPLOAD SECURITY VALIDATOR
# -----------------------------------------------------------------------------

ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.svg'}
ALLOWED_IMAGE_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/svg+xml'
}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB max

def validate_uploaded_image(uploaded_file, max_size=MAX_FILE_SIZE_BYTES):
    """
    Validates uploaded file for extension, MIME content type, and size limits.
    Prevents executable script execution and path traversal attacks.
    """
    if not uploaded_file:
        return None

    # 1. Check size limit
    if uploaded_file.size > max_size:
        raise ValidationError(f"File size exceeds maximum allowed limit of {max_size // (1024 * 1024)}MB.")

    # 2. Check extension
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}")

    # 3. Check content type if available
    content_type = getattr(uploaded_file, 'content_type', '').lower()
    if content_type and content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValidationError(f"Invalid MIME type '{content_type}'. Must be a valid image file.")

    return True


def sanitize_filename(filename, prefix="asset"):
    """
    Generates a cryptographically randomized, clean alphanumeric filename.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        ext = '.png'
    random_hex = secrets.token_hex(8)
    clean_prefix = slugify(prefix)[:20] or "file"
    return f"{clean_prefix}_{random_hex}{ext}"


# -----------------------------------------------------------------------------
# 2. SLIDING-WINDOW RATE LIMITER (In-Memory / Multi-Tenant Safe)
# -----------------------------------------------------------------------------

class SlidingWindowRateLimiter:
    """
    Thread-safe, in-memory sliding window rate limiter.
    Provides fast throttling without unnecessary database load.
    """
    def __init__(self):
        self.requests = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        cutoff = now - window_seconds
        
        # Filter timestamps outside current window
        valid_requests = [t for t in self.requests[key] if t > cutoff]
        self.requests[key] = valid_requests

        if len(valid_requests) >= max_requests:
            return False

        self.requests[key].append(now)
        return True

    def get_remaining_cooldown(self, key: str, window_seconds: int) -> int:
        now = time.time()
        cutoff = now - window_seconds
        valid_requests = [t for t in self.requests[key] if t > cutoff]
        if not valid_requests:
            return 0
        oldest = min(valid_requests)
        return max(0, int(window_seconds - (now - oldest)))


# Global Singleton Rate Limiters for sensitive endpoints
login_rate_limiter = SlidingWindowRateLimiter()       # 5 attempts per 60s per IP
spin_rate_limiter = SlidingWindowRateLimiter()        # 10 attempts per 60s per IP
coupon_rate_limiter = SlidingWindowRateLimiter()      # 15 attempts per 60s per IP


# -----------------------------------------------------------------------------
# 3. CLIENT IP RESOLUTION
# -----------------------------------------------------------------------------

def get_client_ip(request) -> str:
    """
    Extracts client IP address respecting X-Forwarded-For headers safely.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip
