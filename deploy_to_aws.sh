#!/bin/bash

# AWS Deployment Script for Risk Management App
# This script automates the deployment process

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="us-east-1"
APP_NAME="risk-management-app"

echo -e "${BLUE}🚀 Risk Management App - AWS Deployment${NC}"
echo "================================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command_exists aws; then
    print_error "AWS CLI not found. Please install AWS CLI v2."
    exit 1
fi

if ! command_exists terraform; then
    print_error "Terraform not found. Please install Terraform."
    exit 1
fi

if ! command_exists docker; then
    print_error "Docker not found. Please install Docker."
    exit 1
fi

print_status "All prerequisites satisfied"

# Check AWS credentials
echo -e "\n${BLUE}🔐 Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    print_error "AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
print_status "AWS credentials configured (Account: $ACCOUNT_ID)"

# Get deployment parameters
echo -e "\n${BLUE}⚙️ Configuration Setup${NC}"
read -p "Enter your domain name (e.g., example.com): " DOMAIN_NAME
read -p "Enter your email for SSL certificate notifications: " EMAIL
read -p "Enter MongoDB connection string: " MONGODB_URL

if [ -z "$DOMAIN_NAME" ]; then
    print_error "Domain name is required"
    exit 1
fi

# Create secrets in AWS Secrets Manager
echo -e "\n${BLUE}🔒 Creating secrets in AWS Secrets Manager...${NC}"

# Generate JWT secret
JWT_SECRET=$(openssl rand -base64 32)

# Create JWT secret
aws secretsmanager create-secret \
    --name "risk-app/jwt-secret" \
    --description "JWT secret key for Risk Management App" \
    --secret-string "{\"JWT_SECRET_KEY\":\"$JWT_SECRET\"}" \
    --region $AWS_REGION >/dev/null 2>&1 || \
aws secretsmanager update-secret \
    --secret-id "risk-app/jwt-secret" \
    --secret-string "{\"JWT_SECRET_KEY\":\"$JWT_SECRET\"}" \
    --region $AWS_REGION >/dev/null 2>&1

print_status "JWT secret created/updated"

# Create database credentials
aws secretsmanager create-secret \
    --name "risk-app/database" \
    --description "Database credentials for Risk Management App" \
    --secret-string "{\"MONGODB_URL\":\"$MONGODB_URL\",\"DB_NAME\":\"risk_app\"}" \
    --region $AWS_REGION >/dev/null 2>&1 || \
aws secretsmanager update-secret \
    --secret-id "risk-app/database" \
    --secret-string "{\"MONGODB_URL\":\"$MONGODB_URL\",\"DB_NAME\":\"risk_app\"}" \
    --region $AWS_REGION >/dev/null 2>&1

print_status "Database credentials created/updated"

# Create application configuration
aws secretsmanager create-secret \
    --name "risk-app/config" \
    --description "Application configuration for Risk Management App" \
    --secret-string "{\"CORS_ORIGINS\":\"[\\\"https://$DOMAIN_NAME\\\", \\\"https://www.$DOMAIN_NAME\\\"]\",\"ALLOWED_HOSTS\":\"[\\\"$DOMAIN_NAME\\\", \\\"www.$DOMAIN_NAME\\\"]\",\"DEBUG\":\"false\",\"ENVIRONMENT\":\"production\"}" \
    --region $AWS_REGION >/dev/null 2>&1 || \
aws secretsmanager update-secret \
    --secret-id "risk-app/config" \
    --secret-string "{\"CORS_ORIGINS\":\"[\\\"https://$DOMAIN_NAME\\\", \\\"https://www.$DOMAIN_NAME\\\"]\",\"ALLOWED_HOSTS\":\"[\\\"$DOMAIN_NAME\\\", \\\"www.$DOMAIN_NAME\\\"]\",\"DEBUG\":\"false\",\"ENVIRONMENT\":\"production\"}" \
    --region $AWS_REGION >/dev/null 2>&1

print_status "Application configuration created/updated"

# Create infrastructure directory
echo -e "\n${BLUE}🏗️ Setting up infrastructure...${NC}"
mkdir -p infrastructure

# Check if Terraform files exist
if [ ! -f "infrastructure/main.tf" ]; then
    print_warning "Terraform files not found. Please copy the Terraform configuration from AWS_DEPLOYMENT.md to infrastructure/main.tf"
    echo "Would you like me to open the deployment guide? (y/n)"
    read -p "> " OPEN_GUIDE
    if [ "$OPEN_GUIDE" = "y" ]; then
        if command_exists code; then
            code AWS_DEPLOYMENT.md
        else
            echo "Please manually copy the Terraform configuration from AWS_DEPLOYMENT.md"
        fi
    fi
    exit 1
fi

# Initialize Terraform
echo -e "\n${BLUE}🔧 Initializing Terraform...${NC}"
cd infrastructure
terraform init

print_status "Terraform initialized"

# Plan deployment
echo -e "\n${BLUE}📋 Planning deployment...${NC}"
terraform plan \
    -var="domain_name=$DOMAIN_NAME" \
    -var="alert_email=$EMAIL" \
    -var="aws_region=$AWS_REGION" \
    -out=tfplan

print_status "Deployment plan created"

# Confirm deployment
echo -e "\n${YELLOW}⚠️ Ready to deploy infrastructure. This will create AWS resources and may incur costs.${NC}"
read -p "Do you want to proceed? (y/N): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Deployment cancelled"
    exit 0
fi

# Apply infrastructure
echo -e "\n${BLUE}🚀 Deploying infrastructure...${NC}"
terraform apply tfplan

print_status "Infrastructure deployed successfully"

# Get outputs
ALB_DNS=$(terraform output -raw load_balancer_dns 2>/dev/null || echo "Not available")
NAME_SERVERS=$(terraform output -json name_servers 2>/dev/null || echo "[]")

cd ..

# Display next steps
echo -e "\n${GREEN}🎉 Deployment Complete!${NC}"
echo "================================================"
echo -e "${BLUE}Load Balancer DNS:${NC} $ALB_DNS"
echo -e "${BLUE}Name Servers:${NC} $NAME_SERVERS"

echo -e "\n${YELLOW}📝 Next Steps:${NC}"
echo "1. Update your domain's DNS to point to the name servers above"
echo "2. Wait for DNS propagation (can take up to 48 hours)"
echo "3. Once DNS is propagated, your app will be available at: https://$DOMAIN_NAME"

echo -e "\n${YELLOW}📊 Monitoring:${NC}"
echo "• CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logsV2:log-groups/log-group/risk-app"
echo "• EC2 Instances: https://console.aws.amazon.com/ec2/v2/home?region=$AWS_REGION#Instances:"
echo "• Load Balancer: https://console.aws.amazon.com/ec2/v2/home?region=$AWS_REGION#LoadBalancers:"

echo -e "\n${YELLOW}💰 Cost Monitoring:${NC}"
echo "• Set up billing alerts in AWS Console"
echo "• Estimated monthly cost: ~$97/month"

echo -e "\n${BLUE}🔧 Management Commands:${NC}"
echo "# View application logs:"
echo "aws logs tail risk-app --follow --region $AWS_REGION"
echo ""
echo "# Check Auto Scaling Group:"
echo "aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names $APP_NAME-asg --region $AWS_REGION"
echo ""
echo "# Update application (SSH to instances and pull latest code):"
echo "# Find instance IDs and use AWS Systems Manager Session Manager"

print_status "Deployment script completed successfully!"