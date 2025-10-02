# Risk App - Document Management System

A full-stack web application for uploading, validating, managing, and exporting documents (CSV, XLSX, SAS7BDAT, XPT) with enhanced statistical file support, comprehensive export functionality, Excel sheet selection, and non-ASCII character detection.

## 🆕 Recent Updates (October 2025)

**🎉 Comprehensive Export Functionality Added!**
- ✨ **Individual Document Export**: Export any document in CSV, XLSX, or JSON format
- 📦 **Bulk Export by Tag**: Export all documents with the same tag as combined CSV, multi-sheet Excel, or comprehensive JSON
- 🎨 **Enhanced UI**: New export dropdown menus and bulk export buttons with responsive design
- 🔧 **Backend Improvements**: Added xlsxwriter dependency and enhanced document service
- 📋 **Metadata Preservation**: JSON exports include full document metadata and validation information
- 🔐 **Secure Access**: All export operations require authentication
- 📱 **Mobile-Friendly**: Export interface optimized for all screen sizes

**✅ Current Status**: All containers rebuilt and deployed with export functionality
- Backend: Successfully rebuilt with xlsxwriter support
- Frontend: Updated with new export UI components  
- All services running and tested ✓

## Features

- 📁 **Multi-Format File Upload**: Support for CSV, XLSX, SAS7BDAT, and XPT files
- 📊 **Excel Sheet Selection**: Interactive dropdown for multi-sheet Excel files
- 🔬 **Statistical File Support**: Enhanced SAS7BDAT and XPT processing with `pyreadstat`
- 📋 **Dual Document Upload**: Creates separate data and metadata documents for statistical files
- 🔍 **Validation**: Automatic detection of non-ASCII characters with location reporting
- 💾 **Database Storage**: MongoDB integration for document persistence
- 📋 **Document Management**: View, edit, and delete stored documents
- 🏷️ **Unique Tagging System**: Organize documents with unique custom tags (no duplicates allowed)
- � **Multi-Format Export**: Export documents in CSV, XLSX, and JSON formats
- 📦 **Bulk Export**: Export multiple documents by tag with combined data or separate sheets
- �🔐 **Authentication**: Bearer token authentication with Swagger UI integration
- 🐳 **Dockerized**: Full containerization with Docker Compose
- 🎨 **Modern UI**: Responsive React frontend
- 📚 **API Documentation**: Interactive Swagger UI with authentication support

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database for document storage
- **Motor**: Async MongoDB driver
- **Pandas**: Data processing and file parsing
- **Pydantic**: Data validation and serialization
- **pyreadstat**: Statistical file format support (SAS7BDAT, XPT)
- **xlsxwriter**: Excel file export functionality

### Frontend
- **React**: Modern JavaScript frontend framework
- **Axios**: HTTP client for API communication
- **CSS3**: Custom styling with responsive design

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Frontend web server

## Project Structure

```
risk_app/
├── README.md                    # Project documentation
├── docker-compose.yml          # Container orchestration
├── .gitignore                   # Git ignore rules
├── usage.sh                     # CLI tool for document management
├── usage.ps1                    # PowerShell CLI tool
├── start.sh                     # Linux/macOS start script
├── start.bat                    # Windows start script
├──
├── backend/                     # FastAPI Backend
│   ├── Dockerfile               # Backend container definition
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Backend environment variables
│   ├── .dockerignore           # Docker build exclusions
│   └── app/
│       ├── main.py              # FastAPI application entry point
│       ├── database.py          # MongoDB connection setup
│       ├── security.py          # Authentication & token management
│       ├── models/
│       │   └── document.py      # Pydantic models for documents
│       ├── routes/
│       │   ├── auth.py          # Authentication endpoints
│       │   └── documents.py     # Document management endpoints
│       ├── services/
│       │   ├── document_service.py  # Document business logic
│       │   └── file_service.py      # File processing services
│       └── utils/               # Utility functions
│
├── frontend/                    # React Frontend  
│   ├── Dockerfile               # Frontend container definition
│   ├── package.json             # Node.js dependencies
│   ├── nginx.conf               # Nginx web server configuration
│   ├── .env                     # Frontend environment variables
│   ├── .dockerignore           # Docker build exclusions
│   ├── public/
│   │   └── index.html           # HTML template
│   └── src/
│       ├── index.js             # React application entry point
│       ├── App.js               # Main application component
│       ├── App.css              # Global styles
│       ├── index.css            # Base styles
│       ├── components/
│       │   ├── Login.js         # Authentication component
│       │   ├── DocumentList.js  # Document listing & management
│       │   ├── DocumentViewer.js # Document viewing & editing
│       │   ├── FileUpload.js    # File upload interface
│       │   ├── AdminToggle.js   # Admin view toggle
│       │   └── *.css            # Component styles
│       ├── contexts/
│       │   └── AuthContext.js   # Authentication state management
│       └── services/
│           └── api.js           # API communication layer
│
└── .vscode/                     # VS Code settings (optional)
    └── tasks.json               # VS Code tasks configuration
```

### Key Directories

#### Backend (`/backend`)
- **FastAPI Application**: Modern async Python web framework
- **Database Integration**: MongoDB with Motor async driver  
- **Authentication**: Token-based auth with user tracking
- **File Processing**: Multi-format validation and parsing (CSV, XLSX, SAS7BDAT, XPT)
- **API Documentation**: Auto-generated with OpenAPI/Swagger

#### Frontend (`/frontend`)
- **React SPA**: Modern JavaScript single-page application
- **Authentication UI**: Login and token management
- **Document Management**: Upload, view, edit, delete operations
- **Responsive Design**: Mobile-friendly interface
- **Nginx Serving**: Production-ready web server

#### CLI Tools
- **usage.sh**: Cross-platform bash script with multi-tool parsing
- **usage.ps1**: PowerShell alternative for Windows users
- **Authentication**: Token persistence and automatic login

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (for cloning the repository)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd risk_app
   ```

2. **Start the application**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Authentication

The Risk App uses token-based authentication to secure all operations. All API endpoints and frontend features require valid authentication.

### 🔐 Getting Authorization Token

#### Method 1: Using the Web Interface
1. Open the frontend at http://localhost:3000
2. Click "Login" button
3. Enter security code: `admin123` (default for development)
4. Token will be automatically stored in your browser

#### Method 2: Using API Directly
```bash
# Get Bearer token via API
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"security_code": "admin123"}'

# Response example:
{
  "access_token": "stRhs1bpSIs4k5mxXJF3MZpk37BPbKIPNtVihsUic7A",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### Method 3: Using CLI Tool
```bash
# Authenticate and save token for CLI use
bash usage.sh auth admin123

# Token is automatically saved for future CLI operations
```

### 🎫 Using the Bearer Token

#### In API Requests
```bash
# Include in Authorization header
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/documents/
```

#### Security Notes
- Default security code: `admin123` (change in production)
- Tokens expire after 24 hours
- Each user action is tracked with their identity
- Set `SECURITY_CODE_HASH` environment variable for production

### Development Setup

#### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm start
```

## Usage

**Note**: All operations require authentication. Please see the [Authentication](#authentication) section above.

### 🔐 Authentication Required
All features require login with security code (`admin123` by default).

### 📁 1. Upload Documents
- Click "Select File" and choose a supported file (CSV, XLSX, SAS7BDAT, or XPT)
- Enter a **unique** tag/name for the document (no duplicates allowed)
- Click "Upload File"
- Review any validation errors if non-ASCII characters are found
- **Tag uniqueness**: Each document must have a unique tag - you'll get an error if the tag already exists
- **User tracking**: Your identity is automatically recorded as the document creator

### 👀 2. View Documents  
- Browse the document list on the main page
- Each document shows:
  - Basic information and error count
  - **Created by** and **Updated by** user information
  - Creation and last modification dates
- Click "View/Edit" to open the document viewer

### ✏️ 3. Edit Documents
- In the document viewer, click "Edit"
- Modify the tag (must remain unique) or edit individual cell values
- Click "Save Changes" to persist modifications
- **Tag uniqueness**: When changing tags, the new tag must be unique across all documents
- **User tracking**: Your identity is recorded as the last modifier

### 🗑️ 4. Delete Documents
- Click "Delete" on any document in the list
- Confirm the deletion when prompted
- Document is permanently removed from the system

### 4. Manage Documents
- Delete documents using the "Delete" button
- View detailed validation errors in the document viewer

## API Endpoints

**Note**: All document endpoints require Bearer token authentication.

### 🔐 Authentication

- `POST /auth/login` - Authenticate with security code and get Bearer token
- `POST /auth/verify` - Verify security code without creating token

### 📄 Documents

- `POST /documents/upload` - Upload a new document with unique tag (records `created_by`, returns 409 if tag exists)
- `GET /documents/` - Get all documents (includes user tracking info)
- `GET /documents/tag/{tag}` - Get documents by tag
- `GET /documents/{id}` - Get document by ID (includes `created_by`, `updated_by`)
- `PUT /documents/{id}` - Update document with unique tag validation (records `updated_by`, returns 409 if tag exists)
- `DELETE /documents/{id}` - Delete document

### 📥 Export Endpoints

- `GET /documents/{id}/export/csv` - Export individual document as CSV
- `GET /documents/{id}/export/xlsx` - Export individual document as Excel file
- `GET /documents/{id}/export/json` - Export individual document as JSON with metadata
- `GET /documents/tag/{tag}/export/csv` - Export all documents by tag as combined CSV
- `GET /documents/tag/{tag}/export/xlsx` - Export all documents by tag as multi-sheet Excel file
- `GET /documents/tag/{tag}/export/json` - Export all documents by tag as JSON with metadata

### 🔍 Health & Status

- `GET /` - API status  
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## 📊 Supported File Formats

### Format Support Matrix

| **Format** | **Extension** | **Description** | **Library** | **Use Cases** |
|------------|---------------|-----------------|-------------|---------------|
| **CSV** | `.csv` | Comma-Separated Values | pandas | General data exchange, Excel exports |
| **Excel** | `.xlsx`, `.xls` | Microsoft Excel files | pandas + openpyxl | Spreadsheet data, formatted reports |
| **SAS7BDAT** | `.sas7bdat` | SAS dataset files | pyreadstat | Statistical analysis, pharmaceutical data |
| **XPT** | `.xpt` | SAS Transport files | pyreadstat | Regulatory submissions, data exchange |

### Enhanced Features

#### Excel File Enhancements

- **Multi-Sheet Support**: Interactive dropdown for sheet selection in multi-sheet Excel files
- **Sheet Preview**: Displays available sheets before upload for user selection
- **Format Compatibility**: Full support for both modern `.xlsx` and legacy `.xls` formats

#### Statistical File Processing (SAS7BDAT & XPT)

- **pyreadstat Integration**: Uses industry-standard `pyreadstat` library for robust file processing
- **Dual Document Upload**: Creates separate documents for data and metadata
- **Rich Metadata Extraction**: Preserves variable labels, value labels, formats, and file properties
- **Temporary File Processing**: Secure file handling with automatic cleanup
- **Enhanced Error Handling**: Comprehensive error reporting and safe type conversion

### Technical Details

- **CSV Files**: UTF-8, Latin-1, and CP1252 encoding support with automatic detection
- **Excel Files**: Automatic sheet detection with interactive selection for multi-sheet files
- **SAS7BDAT**: Native SAS dataset format reading with comprehensive metadata preservation
- **XPT**: SAS Transport format for regulatory compliance with full metadata support
- **Data Types**: Automatic handling of dates, numbers, text, and missing values
- **Large Files**: Efficient memory usage for processing large datasets
- **Authentication**: All file operations require Bearer token authentication

## File Validation

The system automatically validates uploaded files for:
- **Non-ASCII Characters**: Detects characters outside the ASCII range (0-127)
- **Location Reporting**: Provides exact row and column locations of issues
- **Multiple Encodings**: Attempts to read files with different encodings
- **Format Integrity**: Validates file structure and data consistency
- **Statistical Metadata**: Preserves variable labels and formats from SAS files

## 📥 Export Features

The application provides comprehensive export functionality for stored documents:

### Export Formats

- **CSV**: Plain comma-separated values for universal compatibility
- **XLSX**: Microsoft Excel format with proper formatting and data types
- **JSON**: Complete data export with metadata, validation errors, and document information

### Individual Document Export

Export any single document in your preferred format:
- Access via dropdown menu on each document card
- Filenames automatically include document tag and original filename
- All exports preserve data integrity and formatting

### Bulk Export by Tag

Export multiple documents sharing the same tag:
- **CSV Export**: Combines all data into single CSV with document metadata columns
- **XLSX Export**: Creates multi-sheet workbook with one sheet per document
- **JSON Export**: Comprehensive export with all document metadata and validation information

### Export Access

- All export operations require authentication
- Available through both the web interface and REST API
- Downloadable files with appropriate content-type headers
- Browser-friendly download experience with proper filenames

### Export Use Cases

- **Data Analysis**: Export to CSV/XLSX for analysis in Excel, R, Python, or SAS
- **Data Backup**: JSON exports include complete document information for backup/restore
- **Report Generation**: XLSX exports with proper formatting for stakeholder reports
- **Data Integration**: CSV exports for importing into other systems
- **Compliance**: Complete audit trail available in JSON exports

## Data Storage

Documents are stored in MongoDB with the following structure:

```json
{
  "_id": "ObjectId",
  "tag": "Document Name",
  "filename": "original_file.xlsx",
  "file_type": "xlsx",
  "data": [{"column1": "value1", "column2": "value2"}],
  "validation_errors": [
    {
      "column": "column_name",
      "row": 1,
      "value": "problematic_value",
      "message": "Contains non-ASCII characters: ñ, é"
    }
  ],
  "created_at": "2025-10-03T02:00:00Z",
  "updated_at": "2025-10-03T02:00:00Z",
  "created_by": "user_admin123",
  "updated_by": "user_admin123"
}
```

### 👤 User Tracking

The system automatically tracks user activity:
- **created_by**: User who uploaded the document
- **updated_by**: User who last modified the document  
- **Authentication-based**: Users identified by their security code
- **Audit trail**: Complete history of who did what and when

## Docker Configuration

### Services

- **mongodb**: MongoDB database server
- **backend**: FastAPI application server
- **frontend**: Nginx-served React application

### Volumes

- `mongodb_data`: Persistent storage for MongoDB data

### Networks

- `risk_app_network`: Internal network for service communication

## Environment Variables

### Backend (.env)

```env
MONGODB_URL=mongodb://mongodb:27017
DATABASE_NAME=risk_app
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend Environment

```env
REACT_APP_API_URL=http://localhost:8000
```

## Command-Line Interface (usage.sh)

A robust command-line interface for interacting with the Risk App API with **universal compatibility** across all Unix-like systems.

### 🚀 System Compatibility

The CLI tool automatically adapts to available system tools for maximum compatibility:

| **System Type** | **Available Tools** | **CSV Output Quality** | **Use Case** |
|---|---|---|---|
| **Full Linux/macOS** | Python 3 + shell tools | ✅ **Perfect** - Full data + proper escaping | Development, data analysis |
| **Docker containers** | Node.js + shell tools | ✅ **Good** - Full data + good formatting | CI/CD, microservices |
| **Minimal systems** | Shell tools only | ⚠️ **Basic** - Headers + metadata | Embedded, IoT, Alpine containers |
| **Windows** | Git Bash/WSL + tools | ✅ **Perfect/Good** - Depends on installed tools | Windows development |

### 🔧 Multi-Tool Processing

The script intelligently selects the best available tool:

- 🥇 **Python 3**: Optimal CSV extraction with proper data handling
- 🥈 **Node.js**: Reliable alternative with good CSV formatting  
- 🥉 **Shell tools**: Guaranteed compatibility using sed/awk/grep

### 📋 Core Features

- **Universal compatibility** - works on any Unix system
- **Automatic tool detection** - uses best available processor
- **Token persistence** - saves authentication for reuse
- **Multiple output formats** - CSV, XLSX, JSON
- **Robust error handling** - clear messages and fallbacks

### 🔐 Authentication & User Tracking

All API operations require authentication. The CLI tracks which user performs each action.

#### Set Authentication Token
```bash
# Authenticate with security code (default: admin123)
./usage.sh auth admin123

# This will save the authentication token for future use
# Token persists across script runs until it expires (24 hours)
# Your user identity (admin123) will be recorded with all actions
```

#### Alternative Authentication Methods
```bash
# Set environment variable (session-only)
export RISK_APP_TOKEN=your_jwt_token_here

# Or provide security code via environment (session-only)
export RISK_APP_TOKEN=admin123
./usage.sh auth $RISK_APP_TOKEN
```

### Available Commands

#### 1. Authentication
```bash
# Authenticate and save token
./usage.sh auth <security_code>

# Example
./usage.sh auth admin123
```

#### 2. List All Documents
```bash
# List all available documents
./usage.sh list-docs

# Output: JSON array of all documents with metadata
```

#### 3. Get Document by Tag
```bash
# Get document by tag (saves as CSV by default)
./usage.sh get-by-tag <tag>

# Get document and save with custom filename
./usage.sh get-by-tag <tag> <output_file>

# Examples
./usage.sh get-by-tag risk_data                    # Saves as risk_data.csv
./usage.sh get-by-tag risk_data my_report.csv      # Saves as my_report.csv  
./usage.sh get-by-tag risk_data /path/to/data.xlsx # Saves as Excel file
```

#### 4. Show Usage Examples
```bash
# Display comprehensive usage examples
./usage.sh examples
./usage.sh help
./usage.sh --help
```

### File Format Support & Quality Levels

The script supports multiple output formats with quality depending on available tools:

#### CSV Format (Default)
- **With Python 3**: Full CSV with proper escaping, handles quotes/commas/newlines
- **With Node.js**: Good CSV formatting, proper data extraction
- **Shell only**: Headers + basic data (metadata always preserved)

#### XLSX Format
- **With Python 3**: Full Excel conversion using pandas (requires: `pip install pandas openpyxl`)
- **Fallback**: Creates CSV and suggests conversion methods

#### JSON Format
- **Always available**: Raw API response for programmatic processing

### Usage Examples

#### Complete Workflow
```bash
# Step 1: Authenticate
./usage.sh auth admin123

# Step 2: List available documents
./usage.sh list-docs

# Step 3: Download specific document
./usage.sh get-by-tag financial_data quarterly_report.xlsx

# Step 4: Download to specific directory
./usage.sh get-by-tag risk_analysis /reports/2025/risk_analysis.csv
```

#### Direct API Calls (Alternative)

If you prefer using curl directly:
```bash
# Get authentication token first
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"security_code": "admin123"}' | \
  sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

# List documents  
curl -H "Authorization: Bearer $TOKEN" \
     -H "Accept: application/json" \
     "http://localhost:8000/documents/"

# Get document by tag
curl -H "Authorization: Bearer $TOKEN" \
     -H "Accept: application/json" \
     "http://localhost:8000/documents/tag/YOUR_TAG"
```

### PowerShell Examples (Windows)

For Windows users preferring PowerShell:
```powershell
# Authenticate and get token
$body = '{"security_code": "admin123"}'
$response = Invoke-WebRequest -Uri "http://localhost:8000/auth/login" -Method POST -ContentType "application/json" -Body $body
$token = ($response.Content | ConvertFrom-Json).access_token

# List documents
$headers = @{'Authorization' = "Bearer $token"; 'Accept' = 'application/json'}
$docs = Invoke-WebRequest -Uri "http://localhost:8000/documents/" -Headers $headers
$docs.Content

# Get document by tag and save
$data = Invoke-WebRequest -Uri "http://localhost:8000/documents/tag/YOUR_TAG" -Headers $headers
$data.Content | Out-File -FilePath "output.json"
```

### Script Prerequisites

The `usage.sh` script has **minimal requirements** and works on any Unix-like system:

#### Required (Always Available)
- **Bash**: Available in Git Bash, WSL, or Linux/macOS terminals
- **curl**: For HTTP requests (usually pre-installed)
- **sed/awk/grep**: For basic JSON parsing (standard Unix tools)

#### Optional (Enhanced Features)
- **Python 3**: Best quality CSV output with proper escaping and formatting
- **Node.js**: Good quality CSV output as alternative to Python
- **jq**: Advanced JSON processing (not required, but helpful)

The script automatically detects available tools and uses the best option:
- 🥇 **Python 3**: Full CSV extraction with proper data formatting
- 🥈 **Node.js**: Good CSV extraction with proper formatting
- 🥉 **Shell tools**: Basic extraction (metadata + headers, works everywhere)

#### Platform Setup
##### Linux/macOS
Works out of the box with standard system tools.

##### Windows Setup
1. Install Git for Windows (includes Git Bash)
2. Or use Windows Subsystem for Linux (WSL)
3. Ensure curl is available (included in Windows 10+)

##### Minimal Systems (Docker Alpine, Embedded)
Works with just bash, curl, and basic Unix utilities.

### Real-World Compatibility Examples

```bash
# Ubuntu/Debian/CentOS - Full functionality
./usage.sh get-by-tag data output.csv  # Perfect CSV output

# Docker Alpine containers - Basic functionality  
./usage.sh get-by-tag data output.csv  # Headers + metadata

# Windows Git Bash - Full functionality (if Python installed)
./usage.sh get-by-tag data output.csv  # Perfect CSV output

# Embedded Linux (OpenWrt, etc.) - Basic functionality
./usage.sh get-by-tag data output.csv  # Headers + metadata
```

### Token Management

- Tokens are automatically saved to `~/.risk_app_token` for persistence
- Tokens expire after 24 hours
- If authentication fails, re-run the auth command
- Clear stored token: `rm ~/.risk_app_token`

### Error Handling & Diagnostics

The script provides comprehensive error handling and diagnostics:

#### Common Issues
- **Authentication failures** - Clear token expired messages
- **Network connection problems** - HTTP status code reporting  
- **Invalid tags or missing documents** - Helpful suggestions
- **File permission issues** - Directory creation guidance

#### Tool Detection Messages
- ✅ `Python 3 available - will use for optimal CSV conversion`
- ✅ `Node.js available - will use for CSV conversion`  
- ⚠️ `No Python/Node.js found - will use basic shell extraction`

#### CSV Quality Indicators
- **Perfect**: Full data extraction with proper escaping
- **Good**: Full data extraction with standard formatting
- **Basic**: Headers + metadata (suitable for inspection)

## Development

### Adding New Features
1. Backend changes: Modify files in `backend/app/`
2. Frontend changes: Modify files in `frontend/src/`
3. Database changes: Update models in `backend/app/models/`

### Testing
```bash
# Backend tests (if implemented)
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Troubleshooting

### Common Issues

1. **Container fails to start**:
   - Check Docker daemon is running
   - Verify port 3000 and 8000 are available
   - Check logs: `docker-compose logs <service-name>`

2. **Database connection errors**:
   - Ensure MongoDB container is running
   - Check network connectivity between services

3. **File upload errors**:
   - Verify file format (CSV, XLSX, XLS)
   - Check file size limitations
   - Review backend logs for detailed errors

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository.