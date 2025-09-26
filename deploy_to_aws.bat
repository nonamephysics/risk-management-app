@echo off
REM AWS Deployment Script for Risk Management App (Windows)
REM This script automates the deployment process

setlocal enabledelayedexpansion

echo.
echo 🚀 Risk Management App - AWS Deployment
echo ================================================

REM Configuration
set AWS_REGION=us-east-1
set APP_NAME=risk-management-app

REM Check prerequisites
echo.
echo 📋 Checking prerequisites...

where aws >nul 2>&1
if errorlevel 1 (
    echo ✗ AWS CLI not found. Please install AWS CLI v2.
    pause
    exit /b 1
)

where terraform >nul 2>&1
if errorlevel 1 (
    echo ✗ Terraform not found. Please install Terraform.
    pause
    exit /b 1
)

where docker >nul 2>&1
if errorlevel 1 (
    echo ✗ Docker not found. Please install Docker.
    pause
    exit /b 1
)

echo ✓ All prerequisites satisfied

REM Check AWS credentials
echo.
echo 🔐 Checking AWS credentials...
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ✗ AWS credentials not configured. Run 'aws configure' first.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
echo ✓ AWS credentials configured (Account: %ACCOUNT_ID%)

REM Get deployment parameters
echo.
echo ⚙️ Configuration Setup
set /p DOMAIN_NAME="Enter your domain name (e.g., example.com): "
set /p EMAIL="Enter your email for SSL certificate notifications: "
set /p MONGODB_URL="Enter MongoDB connection string: "

if "%DOMAIN_NAME%"=="" (
    echo ✗ Domain name is required
    pause
    exit /b 1
)

REM Create secrets in AWS Secrets Manager
echo.
echo 🔒 Creating secrets in AWS Secrets Manager...

REM Generate JWT secret (simplified for Windows)
set JWT_SECRET=%RANDOM%%RANDOM%%RANDOM%%RANDOM%

REM Create JWT secret
aws secretsmanager create-secret --name "risk-app/jwt-secret" --description "JWT secret key for Risk Management App" --secret-string "{\"JWT_SECRET_KEY\":\"%JWT_SECRET%\"}" --region %AWS_REGION% >nul 2>&1
if errorlevel 1 (
    aws secretsmanager update-secret --secret-id "risk-app/jwt-secret" --secret-string "{\"JWT_SECRET_KEY\":\"%JWT_SECRET%\"}" --region %AWS_REGION% >nul 2>&1
)
echo ✓ JWT secret created/updated

REM Create database credentials
aws secretsmanager create-secret --name "risk-app/database" --description "Database credentials for Risk Management App" --secret-string "{\"MONGODB_URL\":\"%MONGODB_URL%\",\"DB_NAME\":\"risk_app\"}" --region %AWS_REGION% >nul 2>&1
if errorlevel 1 (
    aws secretsmanager update-secret --secret-id "risk-app/database" --secret-string "{\"MONGODB_URL\":\"%MONGODB_URL%\",\"DB_NAME\":\"risk_app\"}" --region %AWS_REGION% >nul 2>&1
)
echo ✓ Database credentials created/updated

REM Create application configuration
aws secretsmanager create-secret --name "risk-app/config" --description "Application configuration for Risk Management App" --secret-string "{\"CORS_ORIGINS\":\"[\\\"https://%DOMAIN_NAME%\\\", \\\"https://www.%DOMAIN_NAME%\\\"]\",\"ALLOWED_HOSTS\":\"[\\\"%%DOMAIN_NAME%%\\\", \\\"www.%DOMAIN_NAME%\\\"]\",\"DEBUG\":\"false\",\"ENVIRONMENT\":\"production\"}" --region %AWS_REGION% >nul 2>&1
if errorlevel 1 (
    aws secretsmanager update-secret --secret-id "risk-app/config" --secret-string "{\"CORS_ORIGINS\":\"[\\\"https://%DOMAIN_NAME%\\\", \\\"https://www.%DOMAIN_NAME%\\\"]\",\"ALLOWED_HOSTS\":\"[\\\"%%DOMAIN_NAME%%\\\", \\\"www.%DOMAIN_NAME%\\\"]\",\"DEBUG\":\"false\",\"ENVIRONMENT\":\"production\"}" --region %AWS_REGION% >nul 2>&1
)
echo ✓ Application configuration created/updated

REM Create infrastructure directory
echo.
echo 🏗️ Setting up infrastructure...
if not exist infrastructure mkdir infrastructure

REM Check if Terraform files exist
if not exist "infrastructure\main.tf" (
    echo ⚠️ Terraform files not found. Please copy the Terraform configuration from AWS_DEPLOYMENT.md to infrastructure\main.tf
    set /p OPEN_GUIDE="Would you like me to open the deployment guide? (y/n): "
    if /i "!OPEN_GUIDE!"=="y" (
        where code >nul 2>&1
        if not errorlevel 1 (
            code AWS_DEPLOYMENT.md
        ) else (
            echo Please manually copy the Terraform configuration from AWS_DEPLOYMENT.md
        )
    )
    pause
    exit /b 1
)

REM Initialize Terraform
echo.
echo 🔧 Initializing Terraform...
cd infrastructure
terraform init
if errorlevel 1 (
    echo ✗ Terraform initialization failed
    cd ..
    pause
    exit /b 1
)
echo ✓ Terraform initialized

REM Plan deployment
echo.
echo 📋 Planning deployment...
terraform plan -var="domain_name=%DOMAIN_NAME%" -var="alert_email=%EMAIL%" -var="aws_region=%AWS_REGION%" -out=tfplan
if errorlevel 1 (
    echo ✗ Terraform planning failed
    cd ..
    pause
    exit /b 1
)
echo ✓ Deployment plan created

REM Confirm deployment
echo.
echo ⚠️ Ready to deploy infrastructure. This will create AWS resources and may incur costs.
set /p CONFIRM="Do you want to proceed? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Deployment cancelled
    cd ..
    pause
    exit /b 0
)

REM Apply infrastructure
echo.
echo 🚀 Deploying infrastructure...
terraform apply tfplan
if errorlevel 1 (
    echo ✗ Terraform deployment failed
    cd ..
    pause
    exit /b 1
)
echo ✓ Infrastructure deployed successfully

REM Get outputs
for /f "tokens=*" %%i in ('terraform output -raw load_balancer_dns 2^>nul') do set ALB_DNS=%%i
if "%ALB_DNS%"=="" set ALB_DNS=Not available

cd ..

REM Display next steps
echo.
echo 🎉 Deployment Complete!
echo ================================================
echo Load Balancer DNS: %ALB_DNS%

echo.
echo 📝 Next Steps:
echo 1. Update your domain's DNS to point to the AWS name servers
echo 2. Wait for DNS propagation (can take up to 48 hours)
echo 3. Once DNS is propagated, your app will be available at: https://%DOMAIN_NAME%

echo.
echo 📊 Monitoring:
echo • CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=%AWS_REGION%#logsV2:log-groups/log-group/risk-app
echo • EC2 Instances: https://console.aws.amazon.com/ec2/v2/home?region=%AWS_REGION%#Instances:
echo • Load Balancer: https://console.aws.amazon.com/ec2/v2/home?region=%AWS_REGION%#LoadBalancers:

echo.
echo 💰 Cost Monitoring:
echo • Set up billing alerts in AWS Console
echo • Estimated monthly cost: ~$97/month

echo.
echo 🔧 Management Commands:
echo # View application logs:
echo aws logs tail risk-app --follow --region %AWS_REGION%
echo.
echo # Check Auto Scaling Group:
echo aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names %APP_NAME%-asg --region %AWS_REGION%

echo.
echo ✓ Deployment script completed successfully!
echo.
pause