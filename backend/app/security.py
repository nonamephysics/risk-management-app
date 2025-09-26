import os
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import secrets
from datetime import datetime, timedelta

# Security configuration
SECURITY_CODE_HASH = os.getenv("SECURITY_CODE_HASH", "")  # Will be set via environment
DEFAULT_SECURITY_CODE = "admin123"  # Default for development (change in production)
TOKEN_EXPIRE_HOURS = 24

# In-memory token storage (in production, use Redis or database)
active_tokens = {}

security = HTTPBearer(auto_error=False)

def hash_security_code(code: str) -> str:
    """Hash a security code using SHA-256"""
    return hashlib.sha256(code.encode()).hexdigest()

def get_expected_hash() -> str:
    """Get the expected hash for the security code"""
    if SECURITY_CODE_HASH:
        return SECURITY_CODE_HASH
    # Development fallback
    return hash_security_code(DEFAULT_SECURITY_CODE)

def verify_security_code(provided_code: str) -> bool:
    """Verify if the provided security code is correct"""
    provided_hash = hash_security_code(provided_code)
    expected_hash = get_expected_hash()
    return provided_hash == expected_hash

def generate_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def create_access_token(security_code: str) -> str:
    """Create an access token if security code is valid"""
    if not verify_security_code(security_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security code"
        )
    
    token = generate_token()
    expire_time = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    
    # Use security code as user identifier (in production, map to actual usernames)
    user_id = f"user_{security_code}"
    
    active_tokens[token] = {
        "created_at": datetime.utcnow(),
        "expires_at": expire_time,
        "user_id": user_id
    }
    
    return token

def verify_token(token: str) -> bool:
    """Verify if a token is valid and not expired"""
    if token not in active_tokens:
        return False
    
    token_info = active_tokens[token]
    if datetime.utcnow() > token_info["expires_at"]:
        # Token expired, remove it
        del active_tokens[token]
        return False
    
    return True

def cleanup_expired_tokens():
    """Remove expired tokens from memory"""
    current_time = datetime.utcnow()
    expired_tokens = [
        token for token, info in active_tokens.items()
        if current_time > info["expires_at"]
    ]
    for token in expired_tokens:
        del active_tokens[token]

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Dependency to verify authentication"""
    print(f"DEBUG: Auth check - credentials: {credentials}")
    if not credentials:
        print("DEBUG: No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    print(f"DEBUG: Token verification - token: {token[:8]}...")
    if not verify_token(token):
        print("DEBUG: Token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user info from token
    token_info = active_tokens[token]
    user_id = token_info.get("user_id", "unknown")
    
    print(f"DEBUG: Authentication successful for user: {user_id}")
    return {"authenticated": True, "token": token, "user_id": user_id}

def get_token_info() -> dict:
    """Get information about active tokens (for debugging)"""
    cleanup_expired_tokens()
    return {
        "active_tokens": len(active_tokens),
        "tokens": [
            {
                "token": token[:8] + "...",
                "created_at": info["created_at"].isoformat(),
                "expires_at": info["expires_at"].isoformat()
            }
            for token, info in active_tokens.items()
        ]
    }