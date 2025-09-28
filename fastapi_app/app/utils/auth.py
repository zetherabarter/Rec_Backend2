import jwt
import random
import string
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from ..core.config import settings

# Note: bcrypt has a maximum input length of 72 bytes. To avoid issues with
# long passwords (and also to avoid depending on passlib's bcrypt backend
# detection), we pre-hash passwords with SHA-256 and then feed the digest to
# bcrypt. This is equivalent to what `passlib`'s `bcrypt_sha256` handler does
# and guarantees a fixed-size (32 byte) input to bcrypt.
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
        """Hash a password using SHA-256 pre-hash + bcrypt.

        Returns the bcrypt hash as a UTF-8 string.
        """
        if password is None:
            password = ""

        # Pre-hash with SHA-256 to produce a fixed-length input for bcrypt.
        pw_bytes = password.encode("utf-8", errors="ignore")
        sha = hashlib.sha256(pw_bytes).digest()
        try:
            hashed = bcrypt.hashpw(sha, bcrypt.gensalt())
            return hashed.decode("utf-8")
        except Exception as e:
            logger.exception("Error hashing password with bcrypt: %s", e)
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash, handling long passwords safely.

        Returns False if verification fails or an internal error occurs.
        """
        try:
            if plain_password is None:
                plain_password = ""

            # Ensure hashed_password is bytes for bcrypt functions
            if isinstance(hashed_password, str):
                hashed_bytes = hashed_password.encode("utf-8")
            else:
                hashed_bytes = hashed_password

            # If the stored hash looks like a bcrypt hash ($2b$, $2a$, $2y$...),
            # first try the SHA-256 pre-hash + bcrypt check (our new scheme).
            if isinstance(hashed_password, str) and hashed_password.startswith("$2"):
                try:
                    sha = hashlib.sha256(plain_password.encode("utf-8", errors="ignore")).digest()
                    if bcrypt.checkpw(sha, hashed_bytes):
                        return True
                except Exception as e:
                    # bcrypt.checkpw can raise ValueError for >72 bytes if raw
                    # bytes are used; our sha pre-hash is 32 bytes so this
                    # should not happen, but catch defensively.
                    logger.warning("bcrypt checkpw (sha) raised: %s", e)

                # Fallback: try verifying against raw password bytes (legacy)
                try:
                    pw_bytes = plain_password.encode("utf-8", errors="ignore")
                    # bcrypt raises ValueError if input > 72 bytes; truncate
                    if len(pw_bytes) > _BCRYPT_MAX_BYTES:
                        logger.warning(
                            "Password exceeded %d bytes when encoded; truncating for bcrypt compatibility",
                            _BCRYPT_MAX_BYTES,
                        )
                        pw_bytes = pw_bytes[:_BCRYPT_MAX_BYTES]

                    if bcrypt.checkpw(pw_bytes, hashed_bytes):
                        return True
                except Exception as e:
                    logger.warning("bcrypt checkpw (raw) raised: %s", e)

                return False

            # If stored hash doesn't look like bcrypt, we can't verify here.
            logger.warning("Unsupported hash format for verification")
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
