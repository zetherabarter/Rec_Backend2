import jwt
import random
import string
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from ..core.config import settings

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_BCRYPT_LENGTH = 72  # bcrypt max password length in bytes

class AuthUtils:
    """Utility class for authentication operations"""

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate a random numeric OTP"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password, truncating to 72 bytes for bcrypt"""
        truncated_password = password[:MAX_BCRYPT_LENGTH]
        return pwd_context.hash(truncated_password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash, truncating to 72 bytes"""
        truncated_password = plain_password[:MAX_BCRYPT_LENGTH]
        return pwd_context.verify(truncated_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
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
        """Create a JWT refresh token valid for 30 days"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode a JWT token"""
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
