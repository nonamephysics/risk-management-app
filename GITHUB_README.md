# Risk Management App

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)
![React](https://img.shields.io/badge/react-18.x-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)

A comprehensive full-stack document management system for risk assessment and analysis. Features CSV/XLSX file upload with advanced validation, unique document tagging, user authentication, and real-time data processing.

## 🚀 Features

- **Document Upload & Processing**: Support for CSV and XLSX files with non-ASCII character validation
- **Unique Tagging System**: Prevents duplicate document tags across the system
- **User Authentication**: JWT-based secure authentication with user tracking
- **Real-time Validation**: Immediate feedback on file format and content validation
- **Responsive UI**: Modern React interface with intuitive file management
- **RESTful API**: Comprehensive FastAPI backend with OpenAPI documentation
- **MongoDB Integration**: Robust database storage with efficient querying

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance async web framework
- **MongoDB** - NoSQL database for document storage
- **PyJWT** - JSON Web Token implementation
- **Python 3.8+** - Core programming language

### Frontend
- **React 18** - Modern UI library
- **JavaScript (ES6+)** - Client-side programming
- **CSS3** - Responsive styling
- **Fetch API** - HTTP client for backend communication

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB (local installation or cloud service)
- Node.js 16+ (for frontend development)
- Git

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/nonamephysics/risk-management-app.git
cd risk-management-app
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
# Install dependencies (if using npm in future)
# npm install
```

### 4. Database Configuration
- Ensure MongoDB is running on localhost:27017
- Or update connection string in backend configuration

### 5. Start the Application

#### Backend (Terminal 1)
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend (Terminal 2)
```bash
cd frontend
# For development, serve the HTML file or use a local server
python -m http.server 3000
```

Access the application at `http://localhost:3000`

## 📊 API Documentation

### Authentication Endpoints
- `POST /register` - User registration
- `POST /token` - User authentication (login)

### Document Management Endpoints
- `POST /upload` - Upload and process documents
- `GET /documents` - List user documents
- `PUT /documents/{id}` - Update document information
- `DELETE /documents/{id}` - Delete documents

### API Features
- **Tag Uniqueness**: Returns 409 Conflict for duplicate tags
- **File Validation**: Supports CSV and XLSX with encoding validation
- **User Isolation**: Each user sees only their documents
- **Error Handling**: Comprehensive error responses with clear messages

Interactive API documentation available at `http://localhost:8000/docs`

## 🏗️ Project Structure

```
risk-management-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── models/              # Database models
│   │   ├── routes/              # API route handlers  
│   │   └── services/            # Business logic
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── index.html              # Main HTML file
│   ├── style.css               # Application styles
│   └── script.js               # Frontend JavaScript
└── README.md                   # Project documentation
```

## 🔐 Authentication

The application uses JWT (JSON Web Tokens) for authentication:

1. Register a new user account
2. Login to receive an access token
3. Include token in Authorization header: `Bearer <token>`
4. Token expires after configured time period

## 📝 Usage Examples

### Document Upload
```javascript
// Upload a CSV/XLSX file with unique tag
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('tag', 'unique-document-tag');

fetch('/upload', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer ' + token
    },
    body: formData
});
```

### Tag Uniqueness
- Each document must have a unique tag across the entire system
- Attempting to upload with existing tag returns 409 Conflict
- Updates are allowed for the same document (self-update)

## 🧪 Development

### Running Tests
```bash
cd backend
python -m pytest tests/
```

### Code Style
- Backend follows PEP 8 Python style guidelines
- Frontend uses modern ES6+ JavaScript patterns

## 🚀 Deployment

### Production Considerations
- Configure MongoDB connection for production environment
- Set secure JWT secret keys
- Enable HTTPS for production deployment
- Configure CORS for production domains
- Set up proper logging and monitoring

### Environment Variables
```bash
DATABASE_URL=mongodb://localhost:27017
JWT_SECRET_KEY=your-secure-secret-key
JWT_ALGORITHM=HS256
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**nonamephysics** - [GitHub Profile](https://github.com/nonamephysics)

## 🙏 Acknowledgments

- FastAPI community for excellent documentation
- React team for the powerful UI library
- MongoDB for flexible document storage
- All contributors to the open-source libraries used

---

⭐ **Star this repository if you found it helpful!**