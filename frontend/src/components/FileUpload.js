import React, { useState } from 'react';
import { documentService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import './FileUpload.css';

const FileUpload = ({ onUploadSuccess }) => {
  const { isAuthenticated, getAuthHeaders } = useAuth();
  const [file, setFile] = useState(null);
  const [tag, setTag] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [validationErrors, setValidationErrors] = useState([]);
  const [uploadResult, setUploadResult] = useState(null);
  const [excelSheets, setExcelSheets] = useState([]);
  const [selectedSheet, setSelectedSheet] = useState('');
  const [isLoadingSheets, setIsLoadingSheets] = useState(false);

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const fileType = selectedFile.name.split('.').pop().toLowerCase();
      const supportedTypes = ['csv', 'xlsx', 'xls', 'sas7bdat', 'xpt'];
      
      if (supportedTypes.includes(fileType)) {
        setFile(selectedFile);
        setValidationErrors([]);
        setUploadResult(null);
        setExcelSheets([]);
        setSelectedSheet('');
        
        // If it's an Excel file, get sheet names
        if (['xlsx', 'xls'].includes(fileType)) {
          await loadExcelSheets(selectedFile);
        }
      } else {
        alert('Please select a CSV, XLSX, SAS7BDAT, or XPT file');
        e.target.value = '';
      }
    }
  };

  const loadExcelSheets = async (excelFile) => {
    setIsLoadingSheets(true);
    try {
      const result = await documentService.getExcelSheets(excelFile, getAuthHeaders(false));
      setExcelSheets(result.sheet_names || []);
      
      // Auto-select first sheet if only one sheet
      if (result.sheet_names && result.sheet_names.length === 1) {
        setSelectedSheet(result.sheet_names[0]);
      }
    } catch (error) {
      console.error('Failed to load Excel sheets:', error);
      alert('Failed to load Excel sheets. You can still upload, but the first sheet will be used.');
      setExcelSheets([]);
    } finally {
      setIsLoadingSheets(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file || !tag.trim()) {
      alert('Please select a file and provide a tag');
      return;
    }

    // Check if Excel file needs sheet selection
    const fileType = file.name.split('.').pop().toLowerCase();
    if (['xlsx', 'xls'].includes(fileType) && excelSheets.length > 1 && !selectedSheet) {
      alert('Please select which Excel sheet to upload');
      return;
    }

    setIsUploading(true);
    setValidationErrors([]);
    setUploadResult(null);

    try {
      const result = await documentService.uploadDocument(
        file, 
        tag.trim(), 
        selectedSheet || null, 
        getAuthHeaders(false)
      );
      setUploadResult(result);
      setValidationErrors(result.validation_errors || []);
      
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
      
      // Reset form if upload was successful
      if (!result.has_errors) {
        setFile(null);
        setTag('');
        setExcelSheets([]);
        setSelectedSheet('');
        document.getElementById('file-input').value = '';
      }
    } catch (error) {
      console.error('Upload error details:', {
        error,
        response: error.response,
        data: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText
      });
      
      let errorMessage = 'Error uploading file';
      
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map(d => d.msg || d.message || d).join(', ');
        } else {
          errorMessage = error.response.data.detail;
        }
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      } else {
        errorMessage = `Network error (${error.response?.status || 'Unknown'})`;
      }
      
      alert(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="file-upload">
        <div className="auth-required-message">
          <h2>🔒 Upload Documents</h2>
          <p>Admin access required to upload documents.</p>
          <p>Switch to Admin Mode to enable this feature.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="file-upload">
      <h2>Upload Document</h2>
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label htmlFor="tag">Tag/Name:</label>
          <input
            type="text"
            id="tag"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
            placeholder="Enter document tag/name"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="file-input">Select File:</label>
          <input
            type="file"
            id="file-input"
            accept=".csv,.xlsx,.xls,.sas7bdat,.xpt"
            onChange={handleFileChange}
            required
          />
          <small>Supported formats: CSV, XLSX, XLS, SAS7BDAT, XPT</small>
        </div>

        {/* Excel Sheet Selection */}
        {excelSheets.length > 0 && (
          <div className="form-group">
            <label htmlFor="sheet-select">Select Excel Sheet:</label>
            {isLoadingSheets ? (
              <div className="loading-sheets">Loading sheets...</div>
            ) : (
              <select
                id="sheet-select"
                value={selectedSheet}
                onChange={(e) => setSelectedSheet(e.target.value)}
                required
              >
                <option value="">Choose a sheet...</option>
                {excelSheets.map((sheet, index) => (
                  <option key={index} value={sheet}>
                    {sheet}
                  </option>
                ))}
              </select>
            )}
            <small>
              This Excel file contains multiple sheets. Please select which sheet to process.
            </small>
          </div>
        )}
        
        <button 
          type="submit" 
          disabled={
            isUploading || 
            !file || 
            !tag.trim() || 
            (excelSheets.length > 0 && !selectedSheet) ||
            isLoadingSheets
          }
        >
          {isUploading ? 'Uploading...' : 'Upload File'}
        </button>
      </form>

      {uploadResult && (
        <div className={`upload-result ${uploadResult.has_errors ? 'has-errors' : 'success'}`}>
          <h3>Upload Result</h3>
          <p>{uploadResult.message}</p>
          <p>Document ID: {uploadResult.document_id}</p>
          
          {validationErrors.length > 0 && (
            <div className="validation-errors">
              <h4>Validation Errors Found:</h4>
              <div className="error-list">
                {validationErrors.map((error, index) => (
                  <div key={index} className="error-item">
                    <strong>Row {error.row}, Column "{error.column}":</strong>
                    <br />
                    Value: "{error.value}"
                    <br />
                    Error: {error.message}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FileUpload;