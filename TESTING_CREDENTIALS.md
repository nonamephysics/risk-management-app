# Test Credentials and Quick Setup

## Test User Credentials
For manual testing, you can use these test credentials:

**Username**: `testuser`  
**Password**: `testpass123`

## Quick Testing Flow

### 1. Access Application
- Open: `http://localhost:3000`
- Login with test credentials above

### 2. Test Excel Sheet Selection
1. **Single Sheet Test**:
   - Upload: `test_files/single_sheet_test.xlsx`
   - Expected: No dropdown, direct upload

2. **Multi-Sheet Test**:
   - Upload: `test_files/multi_sheet_test.xlsx`  
   - Expected: Dropdown with 3 options
   - Try each sheet: Employees, Products, Sales_Data

3. **Special Characters Test**:
   - Upload: `test_files/special_chars_test.xlsx`
   - Expected: Dropdown with special character sheet names

## API Endpoints for Testing

### Authentication Required Endpoints:
- `POST /login` - Login with credentials
- `POST /excel-sheets` - Get sheet names (requires auth)
- `POST /upload` - Upload file with optional sheet_name (requires auth)

### Public Endpoints:
- `GET /health` - Health check
- `GET /` - API status

## Container Management

### Start Testing Environment:
```powershell
docker-compose up -d
```

### Check Status:
```powershell
docker-compose ps
```

### View Logs:
```powershell
# Backend logs
docker logs risk_app_backend

# Frontend logs  
docker logs risk_app_frontend

# MongoDB logs
docker logs risk_app_mongodb
```

### Stop Environment:
```powershell
docker-compose down
```

## Troubleshooting

### Common Issues:
1. **Port conflicts**: Ensure ports 3000, 8000, 27017 are available
2. **Authentication errors**: Check if JWT secret is configured
3. **File upload errors**: Verify file paths and permissions
4. **CORS errors**: Check allowed origins in backend configuration

### Reset Environment:
```powershell
docker-compose down
docker-compose up -d
```

The application is ready for comprehensive testing! 🎉