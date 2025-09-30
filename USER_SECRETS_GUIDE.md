# 🔐 User Secret Configuration Guide

This guide explains how to configure secure user authentication and manage secret codes for your Risk Management Application deployed on AWS.

## 🔑 Authentication System Overview

Your application uses a multi-layered security approach:

1. **JWT (JSON Web Tokens)** - For session management
2. **AWS Secrets Manager** - For storing sensitive configuration
3. **Bcrypt Password Hashing** - For secure password storage
4. **Account Lockout Protection** - Against brute force attacks
5. **Password Reset Tokens** - For secure password recovery

## 🏗️ Secret Management Architecture

```
User Registration/Login
    ↓
JWT Token Generation (AWS Secrets Manager)
    ↓
Encrypted Password Storage (bcrypt + MongoDB)
    ↓
Session Management (JWT validation)
    ↓
Account Security (lockout, reset tokens)
```

## 📋 Configure User Secrets

### 1. Update JWT Configuration

Edit the JWT secret for enhanced security:

```bash
# Generate a new strong JWT secret
JWT_SECRET=$(openssl rand -base64 64)

# Update in AWS Secrets Manager
aws secretsmanager update-secret \
    --secret-id "risk-app/jwt-secret" \
    --secret-string "{
        \"JWT_SECRET_KEY\": \"$JWT_SECRET\",
        \"JWT_ALGORITHM\": \"HS256\",
        \"ACCESS_TOKEN_EXPIRE_MINUTES\": 30,
        \"REFRESH_TOKEN_EXPIRE_DAYS\": 7
    }"
```

### 2. Configure Password Security

Update password policies:

```bash
# Create password policy configuration
aws secretsmanager create-secret \
    --name "risk-app/security-policy" \
    --description "Security policies for user authentication" \
    --secret-string '{
        "MIN_PASSWORD_LENGTH": 8,
        "MAX_PASSWORD_LENGTH": 128,
        "REQUIRE_UPPERCASE": true,
        "REQUIRE_LOWERCASE": true,
        "REQUIRE_NUMBERS": true,
        "REQUIRE_SPECIAL_CHARS": true,
        "BCRYPT_ROUNDS": 12,
        "MAX_LOGIN_ATTEMPTS": 5,
        "LOCKOUT_DURATION_MINUTES": 15,
        "PASSWORD_RESET_TOKEN_EXPIRE_HOURS": 24
    }'
```

### 3. Configure Admin User

Create an initial admin user:

```bash
# Set admin credentials
aws secretsmanager create-secret \
    --name "risk-app/admin-user" \
    --description "Initial admin user credentials" \
    --secret-string '{
        "ADMIN_USERNAME": "admin",
        "ADMIN_EMAIL": "admin@yourdomain.com",
        "ADMIN_PASSWORD": "SecureAdminPassword123!",
        "IS_SUPER_ADMIN": true
    }'
```

## 🔧 Enhanced Authentication Backend

### Update User Model with Advanced Security

Create `backend/app/models/user.py`:

```python
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from pymongo import MongoClient
from passlib.context import CryptContext
from bson import ObjectId
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserSecurity(BaseModel):
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    last_password_change: Optional[datetime] = None
    login_history: List[dict] = Field(default_factory=list)
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    is_admin: bool = False
    is_super_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    security: UserSecurity = Field(default_factory=UserSecurity)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v

class UserLogin(BaseModel):
    username: str
    password: str
    remember_me: bool = False

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]
```

### Enhanced Authentication Service

Create `backend/app/services/enhanced_auth_service.py`:

```python
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import secrets
import string
from fastapi import HTTPException, status
from passlib.context import CryptContext
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import boto3
import json

from ..models.user import User, UserCreate, UserLogin, PasswordReset, PasswordResetConfirm
from ..config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class EnhancedAuthService:
    def __init__(self):
        self.secrets_client = boto3.client('secretsmanager', region_name=settings.aws_region)
        self.ses_client = boto3.client('ses', region_name=settings.aws_region)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with configured rounds"""
        return pwd_context.hash(password, rounds=settings.bcrypt_rounds)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with enhanced payload"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": self.generate_secure_token(16)  # JWT ID for token blacklisting
        })
        
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token for extended sessions"""
        data = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
            "jti": self.generate_secure_token(16)
        }
        
        return jwt.encode(data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify JWT token with type validation"""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token"
            )
    
    def is_user_locked(self, user: User) -> bool:
        """Check if user account is locked"""
        if user.security.locked_until and user.security.locked_until > datetime.utcnow():
            return True
        return False
    
    def should_lock_user(self, failed_attempts: int) -> bool:
        """Determine if user should be locked after failed attempts"""
        return failed_attempts >= settings.max_login_attempts
    
    def lock_user_account(self, user: User) -> User:
        """Lock user account after too many failed attempts"""
        user.security.locked_until = datetime.utcnow() + timedelta(minutes=settings.lockout_duration_minutes)
        user.security.failed_login_attempts = 0  # Reset counter
        return user
    
    def record_login_attempt(self, user: User, success: bool, ip_address: str, user_agent: str) -> User:
        """Record login attempt in user's history"""
        login_record = {
            "timestamp": datetime.utcnow(),
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        user.security.login_history.append(login_record)
        
        # Keep only last 10 login attempts
        if len(user.security.login_history) > 10:
            user.security.login_history = user.security.login_history[-10:]
        
        if success:
            user.security.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
        else:
            user.security.failed_login_attempts += 1
        
        return user
    
    def generate_password_reset_token(self) -> str:
        """Generate secure password reset token"""
        return self.generate_secure_token(48)
    
    def send_password_reset_email(self, user: User, reset_token: str) -> bool:
        """Send password reset email via AWS SES"""
        try:
            reset_url = f"https://{settings.domain}/reset-password?token={reset_token}"
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "Password Reset Request - Risk Management App"
            message["From"] = f"noreply@{settings.domain}"
            message["To"] = user.email
            
            html_body = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello {user.username},</p>
                <p>We received a request to reset your password for your Risk Management App account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't request this reset, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Risk Management App Team</p>
            </body>
            </html>
            """
            
            text_body = f"""
            Password Reset Request
            
            Hello {user.username},
            
            We received a request to reset your password for your Risk Management App account.
            
            Click the link below to reset your password:
            {reset_url}
            
            This link will expire in 24 hours.
            
            If you didn't request this reset, please ignore this email.
            
            Best regards,
            Risk Management App Team
            """
            
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            
            message.attach(part1)
            message.attach(part2)
            
            # Send via AWS SES
            self.ses_client.send_raw_email(
                Source=f"noreply@{settings.domain}",
                Destinations=[user.email],
                RawMessage={'Data': message.as_string()}
            )
            
            return True
        
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength and return detailed feedback"""
        issues = []
        score = 0
        
        if len(password) >= 8:
            score += 1
        else:
            issues.append("Password must be at least 8 characters long")
        
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            issues.append("Password must contain at least one uppercase letter")
        
        if re.search(r'[a-z]', password):
            score += 1
        else:
            issues.append("Password must contain at least one lowercase letter")
        
        if re.search(r'\d', password):
            score += 1
        else:
            issues.append("Password must contain at least one number")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        else:
            issues.append("Password must contain at least one special character")
        
        # Bonus points for longer passwords
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        strength_levels = {
            0: "Very Weak",
            1: "Weak",
            2: "Fair",
            3: "Good",
            4: "Strong",
            5: "Very Strong",
            6: "Excellent",
            7: "Exceptional"
        }
        
        return {
            "score": score,
            "max_score": 7,
            "strength": strength_levels.get(score, "Unknown"),
            "issues": issues,
            "is_valid": score >= 4  # Require at least "Strong"
        }
```

## 🚀 Deploy Authentication Updates

### 1. Update Secrets in AWS

```bash
# Update with enhanced configuration
./deploy_to_aws.sh
```

### 2. Create Admin User Script

Create `backend/create_admin.py`:

```python
#!/usr/bin/env python3
"""
Script to create initial admin user
Usage: python create_admin.py
"""

import asyncio
import sys
import os
from datetime import datetime
from getpass import getpass

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database
from app.models.user import User, UserCreate
from app.services.enhanced_auth_service import EnhancedAuthService

async def create_admin_user():
    """Create initial admin user"""
    print("🔐 Risk Management App - Admin User Creation")
    print("=" * 50)
    
    # Get database connection
    db = await get_database()
    users_collection = db.users
    
    # Check if admin user already exists
    existing_admin = await users_collection.find_one({"is_super_admin": True})
    if existing_admin:
        print("❌ Super admin user already exists!")
        return
    
    # Get admin details
    print("\nEnter admin user details:")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = getpass("Password: ")
    confirm_password = getpass("Confirm Password: ")
    
    if password != confirm_password:
        print("❌ Passwords don't match!")
        return
    
    # Validate password strength
    auth_service = EnhancedAuthService()
    password_validation = auth_service.validate_password_strength(password)
    
    if not password_validation["is_valid"]:
        print(f"❌ Password too weak! Issues:")
        for issue in password_validation["issues"]:
            print(f"   • {issue}")
        return
    
    # Create user
    try:
        hashed_password = auth_service.hash_password(password)
        
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
            is_admin=True,
            is_super_admin=True,
            created_at=datetime.utcnow()
        )
        
        # Insert into database
        result = await users_collection.insert_one(admin_user.dict(by_alias=True))
        
        print(f"✅ Super admin user created successfully!")
        print(f"   • User ID: {result.inserted_id}")
        print(f"   • Username: {username}")
        print(f"   • Email: {email}")
        print(f"   • Password Strength: {password_validation['strength']}")
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
```

### 3. User Management Commands

Create useful management commands:

```bash
# Create admin user
python backend/create_admin.py

# Reset user password (emergency)
python backend/reset_user_password.py --username admin --new-password NewSecurePassword123!

# List all users
python backend/list_users.py

# Lock/unlock user account
python backend/manage_user.py --username problematic_user --action lock
python backend/manage_user.py --username fixed_user --action unlock
```

## 🔒 Security Configuration Checklist

### ✅ Authentication Security
- [ ] Strong JWT secret (64+ characters)
- [ ] Password complexity requirements enforced
- [ ] Account lockout after failed attempts
- [ ] Secure password reset flow
- [ ] Password history tracking
- [ ] Session timeout configuration

### ✅ AWS Security
- [ ] Secrets stored in AWS Secrets Manager
- [ ] IAM roles with minimal permissions
- [ ] VPC with private subnets for database
- [ ] Security groups with restricted access
- [ ] CloudTrail logging enabled
- [ ] CloudWatch monitoring configured

### ✅ Application Security
- [ ] HTTPS enforced (SSL certificates)
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] SQL/NoSQL injection prevention
- [ ] Rate limiting implemented
- [ ] Error messages don't leak information

## 📊 Monitoring User Activity

### CloudWatch Dashboards

Create monitoring for user authentication:

```bash
# Create CloudWatch dashboard for auth metrics
aws cloudwatch put-dashboard \
    --dashboard-name "RiskApp-Authentication" \
    --dashboard-body '{
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "risk-management-app-alb"],
                        [".", "TargetResponseTime", ".", "."],
                        [".", "HTTPCode_Target_4XX_Count", ".", "."],
                        [".", "HTTPCode_Target_5XX_Count", ".", "."]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1",
                    "title": "Application Metrics"
                }
            }
        ]
    }'
```

### Custom Metrics

Log authentication events:

```python
# Add to your auth service
import boto3

cloudwatch = boto3.client('cloudwatch')

def log_auth_event(event_type: str, success: bool, user_id: str = None):
    """Log authentication events to CloudWatch"""
    try:
        cloudwatch.put_metric_data(
            Namespace='RiskApp/Authentication',
            MetricData=[
                {
                    'MetricName': f'Auth_{event_type}',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {
                            'Name': 'Success',
                            'Value': str(success)
                        }
                    ]
                }
            ]
        )
    except Exception as e:
        print(f"Failed to log metric: {e}")

# Usage in your endpoints:
log_auth_event('Login', True, user.id)  # Successful login
log_auth_event('Login', False)          # Failed login
log_auth_event('Registration', True, user.id)  # User registration
log_auth_event('PasswordReset', True, user.id)  # Password reset
```

## 🚨 Security Alerts

Set up alerts for security events:

```bash
# Create alarm for failed login attempts
aws cloudwatch put-metric-alarm \
    --alarm-name "RiskApp-FailedLogins" \
    --alarm-description "High number of failed login attempts" \
    --metric-name "Auth_Login" \
    --namespace "RiskApp/Authentication" \
    --statistic "Sum" \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 20 \
    --comparison-operator "GreaterThanThreshold" \
    --dimensions "Name=Success,Value=false" \
    --alarm-actions "arn:aws:sns:us-east-1:123456789012:security-alerts"
```

This comprehensive security configuration ensures your Risk Management Application has enterprise-level user authentication and secret management! 🔐