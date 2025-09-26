from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.security import create_access_token, get_token_info, verify_security_code

router = APIRouter(prefix="/auth", tags=["Authentication"])

class SecurityCodeRequest(BaseModel):
    security_code: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds

class AuthStatusResponse(BaseModel):
    authenticated: bool
    message: str

@router.post("/login", response_model=AuthResponse)
async def login(request: SecurityCodeRequest):
    """
    Authenticate with security code and receive access token
    """
    try:
        token = create_access_token(request.security_code)
        return AuthResponse(
            access_token=token,
            token_type="bearer"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.post("/verify", response_model=AuthStatusResponse)
async def verify_code(request: SecurityCodeRequest):
    """
    Verify security code without creating a token
    """
    if verify_security_code(request.security_code):
        return AuthStatusResponse(
            authenticated=True,
            message="Security code is valid"
        )
    else:
        return AuthStatusResponse(
            authenticated=False,
            message="Invalid security code"
        )

@router.get("/status")
async def auth_status():
    """
    Get authentication system status (for debugging)
    """
    return {
        "auth_system": "active",
        **get_token_info()
    }