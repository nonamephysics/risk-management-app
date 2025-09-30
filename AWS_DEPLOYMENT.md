# 🚀 AWS Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Risk Management Application to AWS with proper user authentication, security configurations, and secret management.

## 🏗️ Architecture Overview

### Deployment Architecture
```
Internet Gateway
    ↓
Application Load Balancer (HTTPS)
    ↓
EC2 Auto Scaling Group (Frontend + Backend)
    ↓
MongoDB Atlas / AWS DocumentDB
    ↓
AWS Secrets Manager (JWT Keys, DB Credentials)
    ↓
CloudWatch (Logging & Monitoring)
```

### AWS Services Used
- **EC2** - Application hosting with Auto Scaling
- **Application Load Balancer** - HTTPS termination and traffic distribution
- **AWS Secrets Manager** - Secure credential storage
- **Route 53** - DNS management
- **Certificate Manager** - SSL/TLS certificates
- **CloudWatch** - Monitoring and logging
- **VPC** - Network isolation and security
- **IAM** - Access control and roles
- **S3** - Static file storage (optional)

## 📋 Prerequisites

### 1. AWS Account Setup
- Active AWS account with billing configured
- AWS CLI installed and configured
- Domain name registered (for SSL certificates)

### 2. Local Requirements
- Docker and Docker Compose installed
- AWS CLI v2.x
- Terraform (recommended) or AWS CDK

## 🔧 Step 1: Initial AWS Configuration

### Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Default region: us-east-1 (or your preferred region)
# Default output format: json
```

### Verify AWS Access
```bash
aws sts get-caller-identity
```

## 🔐 Step 2: Create Secrets in AWS Secrets Manager

### Create JWT Secret
```bash
# Generate a secure random JWT secret
JWT_SECRET=$(openssl rand -base64 32)

# Store in AWS Secrets Manager
aws secretsmanager create-secret \
    --name "risk-app/jwt-secret" \
    --description "JWT secret key for Risk Management App" \
    --secret-string "{\"JWT_SECRET_KEY\":\"$JWT_SECRET\"}"
```

### Create Database Credentials
```bash
# Create MongoDB connection credentials
aws secretsmanager create-secret \
    --name "risk-app/database" \
    --description "Database credentials for Risk Management App" \
    --secret-string '{
        "MONGODB_URL": "mongodb+srv://username:password@cluster.mongodb.net/risk_app?retryWrites=true&w=majority",
        "DB_NAME": "risk_app"
    }'
```

### Create Application Configuration
```bash
# Store application configuration
aws secretsmanager create-secret \
    --name "risk-app/config" \
    --description "Application configuration for Risk Management App" \
    --secret-string '{
        "CORS_ORIGINS": "[\"https://yourdomain.com\", \"https://www.yourdomain.com\"]",
        "ALLOWED_HOSTS": "[\"yourdomain.com\", \"www.yourdomain.com\"]",
        "DEBUG": "false",
        "ENVIRONMENT": "production"
    }'
```

## 🌐 Step 3: Database Setup

### Option A: MongoDB Atlas (Recommended)
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Configure network access (add AWS region IPs)
4. Create database user
5. Get connection string and update secrets

### Option B: AWS DocumentDB
```bash
# Create DocumentDB cluster (requires VPC setup)
aws docdb create-db-cluster \
    --db-cluster-identifier risk-app-docdb \
    --engine docdb \
    --master-username riskappadmin \
    --master-user-password YourSecurePassword123! \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name risk-app-subnet-group
```

## 🏛️ Step 4: Infrastructure Setup with Terraform

### Create Terraform Configuration

Create `infrastructure/main.tf`:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "risk-management-app"
}

# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.app_name}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.app_name}-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "${var.app_name}-public-subnet-${count.index + 1}"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.app_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Security Groups
resource "aws_security_group" "alb" {
  name        = "${var.app_name}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-alb-sg"
  }
}

resource "aws_security_group" "ec2" {
  name        = "${var.app_name}-ec2-sg"
  description = "Security group for EC2 instances"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Restrict this to your IP in production
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-ec2-sg"
  }
}

# IAM Role for EC2
resource "aws_iam_role" "ec2_role" {
  name = "${var.app_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "ec2_secrets_policy" {
  name = "${var.app_name}-secrets-policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:*:secret:risk-app/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.app_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# Launch Template
resource "aws_launch_template" "app" {
  name_prefix   = "${var.app_name}-"
  image_id      = "ami-0c02fb55956c7d316"  # Amazon Linux 2 AMI
  instance_type = "t3.medium"

  vpc_security_group_ids = [aws_security_group.ec2.id]

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_profile.name
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    aws_region = var.aws_region
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.app_name}-instance"
    }
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {
  name                = "${var.app_name}-asg"
  vpc_zone_identifier = aws_subnet.public[*].id
  target_group_arns   = [aws_lb_target_group.app.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300

  min_size         = 1
  max_size         = 3
  desired_capacity = 2

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "${var.app_name}-asg"
    propagate_at_launch = false
  }
}

# Application Load Balancer
resource "aws_lb" "app" {
  name               = "${var.app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = {
    Name = "${var.app_name}-alb"
  }
}

resource "aws_lb_target_group" "app" {
  name     = "${var.app_name}-tg"
  port     = 3000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    matcher             = "200"
  }
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate_validation.cert.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# HTTP to HTTPS redirect
resource "aws_lb_listener" "redirect" {
  load_balancer_arn = aws_lb.app.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# SSL Certificate
resource "aws_acm_certificate" "cert" {
  domain_name       = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = [
    "www.${var.domain_name}"
  ]

  lifecycle {
    create_before_destroy = true
  }
}

# Route 53 (optional - if you want AWS to manage DNS)
resource "aws_route53_zone" "main" {
  name = var.domain_name
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.main.zone_id
}

resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

resource "aws_route53_record" "app" {
  zone_id = aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_lb.app.dns_name
    zone_id                = aws_lb.app.zone_id
    evaluate_target_health = true
  }
}

# Outputs
output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.app.dns_name
}

output "name_servers" {
  description = "Name servers for the hosted zone"
  value       = aws_route53_zone.main.name_servers
}
```

### Create User Data Script

Create `infrastructure/user_data.sh`:

```bash
#!/bin/bash
yum update -y
yum install -y docker git awscli

# Start Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install CloudWatch agent
yum install -y amazon-cloudwatch-agent

# Clone application
cd /home/ec2-user
git clone https://github.com/nonamephysics/risk-management-app.git
cd risk-management-app

# Get secrets from AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id "risk-app/jwt-secret" --region ${aws_region} --query SecretString --output text | jq -r .JWT_SECRET_KEY > /tmp/jwt_secret
aws secretsmanager get-secret-value --secret-id "risk-app/database" --region ${aws_region} --query SecretString --output text | jq -r .MONGODB_URL > /tmp/mongodb_url
aws secretsmanager get-secret-value --secret-id "risk-app/config" --region ${aws_region} --query SecretString --output text > /tmp/app_config

# Create production environment file
cat > .env << EOF
JWT_SECRET_KEY=$(cat /tmp/jwt_secret)
MONGODB_URL=$(cat /tmp/mongodb_url)
CORS_ORIGINS=$(cat /tmp/app_config | jq -r .CORS_ORIGINS)
DEBUG=false
ENVIRONMENT=production
EOF

# Set proper permissions
chown -R ec2-user:ec2-user /home/ec2-user/risk-management-app
chmod 600 .env

# Create production docker-compose
cat > docker-compose.prod.yml << 'EOL'
version: '3.8'
services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - MONGODB_URL=${MONGODB_URL}
      - CORS_ORIGINS=${CORS_ORIGINS}
      - DEBUG=false
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "awslogs"
      options:
        awslogs-group: "risk-app"
        awslogs-region: "${aws_region}"
        awslogs-stream: "backend"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "awslogs"
      options:
        awslogs-group: "risk-app"
        awslogs-region: "${aws_region}"
        awslogs-stream: "frontend"
EOL

# Create CloudWatch log group
aws logs create-log-group --log-group-name "risk-app" --region ${aws_region} || true

# Start application
docker-compose -f docker-compose.prod.yml up -d

# Clean up sensitive files
rm -f /tmp/jwt_secret /tmp/mongodb_url /tmp/app_config
```

## 🚀 Step 5: Deploy Infrastructure

### Initialize and Deploy
```bash
cd infrastructure

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="domain_name=yourdomain.com"

# Apply infrastructure
terraform apply -var="domain_name=yourdomain.com"
```

## 🐳 Step 6: Create Production Dockerfiles

### Backend Dockerfile
Create `backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
Create `frontend/Dockerfile`:

```dockerfile
FROM node:16-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application (if using a build process)
# RUN npm run build

FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static files
COPY . /usr/share/nginx/html/

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup && \
    chown -R appuser:appgroup /usr/share/nginx/html

EXPOSE 3000

USER appuser

CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration
Create `frontend/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    server {
        listen 3000;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API proxy
        location /api/ {
            proxy_pass http://backend:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## 🔒 Step 7: Configure User Authentication

### Update Backend Configuration
Create `backend/app/config.py`:

```python
import os
from typing import List
import boto3
import json
from functools import lru_cache

class Settings:
    def __init__(self):
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.secrets_client = boto3.client('secretsmanager', region_name=self.aws_region)
        
        # Load secrets from AWS Secrets Manager
        self._load_secrets()
    
    def _load_secrets(self):
        try:
            # Load JWT secret
            jwt_response = self.secrets_client.get_secret_value(SecretId="risk-app/jwt-secret")
            jwt_data = json.loads(jwt_response['SecretString'])
            self.jwt_secret_key = jwt_data['JWT_SECRET_KEY']
            
            # Load database config
            db_response = self.secrets_client.get_secret_value(SecretId="risk-app/database")
            db_data = json.loads(db_response['SecretString'])
            self.mongodb_url = db_data['MONGODB_URL']
            self.db_name = db_data.get('DB_NAME', 'risk_app')
            
            # Load app config
            config_response = self.secrets_client.get_secret_value(SecretId="risk-app/config")
            config_data = json.loads(config_response['SecretString'])
            self.cors_origins = json.loads(config_data['CORS_ORIGINS'])
            self.debug = config_data.get('DEBUG', 'false').lower() == 'true'
            
        except Exception as e:
            # Fallback to environment variables for local development
            self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
            self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            self.db_name = os.getenv("DB_NAME", "risk_app")
            self.cors_origins = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))
            self.debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # JWT Settings
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Security Settings
    bcrypt_rounds: int = 12
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

@lru_cache()
def get_settings():
    return Settings()
```

### Enhanced User Model with Security Features
Update `backend/app/models/user.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from pymongo import MongoClient
from passlib.context import CryptContext
from bson import ObjectId

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
```

### Enhanced Authentication Service
Create `backend/app/services/auth_service.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from ..models.user import User, UserCreate, UserLogin
from ..config import get_settings
import secrets
import string

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password, rounds=settings.bcrypt_rounds)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_password_reset_token() -> str:
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
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
    
    @staticmethod
    def is_user_locked(user: User) -> bool:
        if user.locked_until and user.locked_until > datetime.utcnow():
            return True
        return False
    
    @staticmethod
    def should_lock_user(failed_attempts: int) -> bool:
        return failed_attempts >= settings.max_login_attempts
```

## 📊 Step 8: Monitoring and Logging

### CloudWatch Configuration
Create `infrastructure/monitoring.tf`:

```hcl
# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "app" {
  name              = "risk-app"
  retention_in_days = 30

  tags = {
    Environment = "production"
    Application = "risk-management-app"
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "risk-app-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_target_response_time" {
  alarm_name          = "risk-app-high-response-time"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "2"
  alarm_description   = "This metric monitors ALB target response time"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.app.arn_suffix
  }
}

# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "risk-app-alerts"
}

resource "aws_sns_topic_subscription" "email_alerts" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

variable "alert_email" {
  description = "Email for receiving alerts"
  type        = string
}
```

## 🔄 Step 9: CI/CD Pipeline (Optional)

### GitHub Actions Workflow
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  AWS_REGION: us-east-1

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: |
        cd backend
        pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Deploy to AWS
      run: |
        # Trigger Auto Scaling Group instance refresh
        aws autoscaling start-instance-refresh \
          --auto-scaling-group-name risk-management-app-asg \
          --preferences MinHealthyPercentage=50,InstanceWarmup=300
```

## 📝 Step 10: Production Deployment Checklist

### Pre-Deployment
- [ ] Domain name configured and verified
- [ ] SSL certificate validated
- [ ] Database connection tested
- [ ] Secrets stored in AWS Secrets Manager
- [ ] Terraform plan reviewed

### Deployment
- [ ] Infrastructure deployed via Terraform
- [ ] Application containers running
- [ ] Load balancer health checks passing
- [ ] DNS records pointing to load balancer
- [ ] SSL certificate working

### Post-Deployment
- [ ] User registration and login tested
- [ ] File upload functionality verified
- [ ] Tag uniqueness validation working
- [ ] CloudWatch logs streaming
- [ ] Monitoring alerts configured
- [ ] Backup strategy implemented

## 🔧 Maintenance Commands

### Update Application
```bash
# SSH into EC2 instance
aws ssm start-session --target i-1234567890abcdef0

# Pull latest code
cd /home/ec2-user/risk-management-app
git pull origin main

# Rebuild and restart containers
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### Monitor Application
```bash
# View logs
aws logs tail risk-app --follow

# Check Auto Scaling Group status
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names risk-management-app-asg

# Monitor ALB target health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/risk-app-tg/1234567890123456
```

## 💰 Cost Optimization

### Estimated Monthly Costs (us-east-1)
- **t3.medium instances (2x)**: ~$60/month
- **Application Load Balancer**: ~$22/month  
- **Route 53 hosted zone**: $0.50/month
- **CloudWatch logs**: ~$5/month
- **Data transfer**: ~$10/month
- **Total**: ~$97/month

### Cost Reduction Tips
1. Use **t3.small** instances for lower traffic
2. Enable **Auto Scaling** to scale down during low usage
3. Use **Reserved Instances** for predictable workloads
4. Set up **CloudWatch billing alerts**

## 🔒 Security Best Practices

### Implemented Security Measures
- ✅ HTTPS enforced with SSL certificates
- ✅ Secrets managed via AWS Secrets Manager  
- ✅ IAM roles with least privilege principle
- ✅ Security groups with restricted access
- ✅ Password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ Account lockout after failed attempts
- ✅ Non-root containers

### Additional Recommendations
- Enable **AWS WAF** for web application firewall
- Set up **VPN** for administrative access
- Implement **database encryption at rest**
- Enable **CloudTrail** for audit logging
- Regular **security updates** and patching
- **Backup strategy** for data protection

## 📞 Support and Troubleshooting

### Common Issues

**1. Application not starting**
```bash
# Check container logs
docker-compose -f docker-compose.prod.yml logs

# Check system resources
top
df -h
```

**2. Database connection issues**
```bash
# Test MongoDB connectivity
mongo "mongodb+srv://cluster.mongodb.net/test" --username your-username

# Check secrets
aws secretsmanager get-secret-value --secret-id "risk-app/database"
```

**3. SSL certificate issues**
```bash
# Check certificate status
aws acm describe-certificate --certificate-arn your-cert-arn

# Validate DNS records
dig yourdomain.com
```

---

This comprehensive deployment guide provides everything needed to deploy your Risk Management Application to AWS with proper security, monitoring, and scalability. Follow each step carefully and customize the configuration based on your specific requirements.