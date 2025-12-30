"""
Password hashing utilities using bcrypt
"""
from passlib.context import CryptContext

# Create password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Bcrypt has a 72-byte limit. Passwords longer than this will be truncated.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
        
    Raises:
        ValueError: If password is empty or hashing fails
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # Ensure password is a string (not bytes)
    if isinstance(password, bytes):
        password = password.decode('utf-8', errors='ignore')
    
    # Check byte length
    password_bytes = password.encode('utf-8')
    byte_length = len(password_bytes)
    
    # Truncate if necessary (bcrypt limit is 72 bytes)
    if byte_length > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    # Hash using passlib - it should handle normal passwords fine
    # The error we're seeing suggests something else might be wrong
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

