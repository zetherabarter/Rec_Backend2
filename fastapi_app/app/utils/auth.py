import jwt
import random
import string
import logging
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from ..core.config import settings

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# bcrypt has a maximum input length of 72 bytes. We'll normalize inputs to avoid
# passlib raising an error. Truncation is applied deterministically both when
# hashing and when verifying so the result remains consistent.
_BCRYPT_MAX_BYTES = 72
logger = logging.getLogger("auth_utils")


class AuthUtils:
    """Utility class for authentication operations"""

    @staticmethod
    def _normalize_password_for_bcrypt(password: str) -> str:
        """Normalize password so that its UTF-8 encoding is at most 72 bytes.

        If the UTF-8 byte length is greater than 72, truncate the bytes to 72 and
        decode back to a string (ignoring partial character at the end). This
        keeps hashing and verification consistent while avoiding passlib/bcrypt
        ValueError for long passwords.
        """
        if password is None:
            return ""
        pw_bytes = password.encode("utf-8", errors="ignore")
        if len(pw_bytes) <= _BCRYPT_MAX_BYTES:
            return password
        # Truncate and decode safely
        truncated = pw_bytes[:_BCRYPT_MAX_BYTES].decode("utf-8", errors="ignore")
        logger.warning(
            "Password exceeded %d bytes when encoded; truncating for bcrypt compatibility",
            _BCRYPT_MAX_BYTES,
        )
        return truncated

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password (normalizes to bcrypt max bytes)."""
        normalized = AuthUtils._normalize_password_for_bcrypt(password)
        try:
            return pwd_context.hash(normalized)
        except Exception as e:
            logger.exception("Error hashing password: %s", e)
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash, handling long passwords safely.

        Returns False if verification fails or an internal error occurs.
        """
        try:
            normalized = AuthUtils._normalize_password_for_bcrypt(plain_password)
            return pwd_context.verify(normalized, hashed_password)
        except ValueError as e:
            # passlib raises ValueError for inputs too long for the backend
            logger.warning("Password verification failed due to value error: %s", e)
            return False
        except Exception as e:
            logger.exception("Unexpected error during password verification: %s", e)
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)  # Refresh token expires in 30 days
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def get_otp_expiry() -> datetime:
        """Get OTP expiry time (5 minutes from now)"""
        return datetime.utcnow() + timedelta(minutes=5)

    @staticmethod
    def is_otp_expired(expires_at: datetime) -> bool:
        """Check if OTP is expired"""
        return datetime.utcnow() > expires_at
