import React, { useState, useEffect } from 'react';
import { documentService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import './DocumentList.css';

const DocumentList = ({ refreshTrigger, onDocumentSelect }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTag, setSearchTag] = useState('');
  const { isAuthenticated, getAuthHeaders } = useAuth();

  const fetchDocuments = async (tag = '') => {
    if (!isAuthenticated) {
      setDocuments([]);
      setLoading(false);
      setError(null);
      return;
    }

    try {
      setLoading(true);
      const authHeaders = getAuthHeaders();
      const data = tag.trim() 
        ? await documentService.getDocumentsByTag(tag.trim(), authHeaders)
        : await documentService.getAllDocuments(authHeaders);
      setDocuments(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [refreshTrigger, isAuthenticated]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchDocuments(searchTag);
  };

  const handleClearSearch = () => {
    setSearchTag('');
    fetchDocuments('');
  };

  const handleDelete = async (id, tag) => {
    if (window.confirm(`Are you sure you want to delete "${tag}"?`)) {
      try {
        const authHeaders = getAuthHeaders();
        await documentService.deleteDocument(id, authHeaders);
        await fetchDocuments(); // Refresh the list
      } catch (err) {
        console.error('Error deleting document:', err);
        alert('Failed to delete document');
      }
    }
  };

  const downloadFile = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleExportDocument = async (id, tag, filename, format) => {
    try {
      const authHeaders = getAuthHeaders();
      let blob;
      let exportFilename;
      
      switch (format) {
        case 'csv':
          blob = await documentService.exportDocumentCSV(id, authHeaders);
          exportFilename = `${tag}_${filename.split('.')[0]}.csv`;
          break;
        case 'xlsx':
          blob = await documentService.exportDocumentXLSX(id, authHeaders);
          exportFilename = `${tag}_${filename.split('.')[0]}.xlsx`;
          break;
        case 'json':
          blob = await documentService.exportDocumentJSON(id, authHeaders);
          exportFilename = `${tag}_${filename.split('.')[0]}.json`;
          break;
        default:
          throw new Error('Unsupported format');
      }
      
      downloadFile(blob, exportFilename);
    } catch (err) {
      console.error(`Error exporting document as ${format}:`, err);
      alert(`Failed to export document as ${format.toUpperCase()}`);
    }
  };

  const handleExportByTag = async (tag, format) => {
    try {
      const authHeaders = getAuthHeaders();
      let blob;
      let exportFilename;
      
      switch (format) {
        case 'csv':
          blob = await documentService.exportDocumentsByTagCSV(tag, authHeaders);
          exportFilename = `${tag}_combined.csv`;
          break;
        case 'xlsx':
          blob = await documentService.exportDocumentsByTagXLSX(tag, authHeaders);
          exportFilename = `${tag}_multiple_sheets.xlsx`;
          break;
        case 'json':
          blob = await documentService.exportDocumentsByTagJSON(tag, authHeaders);
          exportFilename = `${tag}_documents.json`;
          break;
        default:
          throw new Error('Unsupported format');
      }
      
      downloadFile(blob, exportFilename);
    } catch (err) {
      console.error(`Error exporting documents by tag as ${format}:`, err);
      alert(`Failed to export documents by tag as ${format.toUpperCase()}`);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="document-list">
        <h2>📄 Documents</h2>
        <div className="auth-required-message">
          <p>🔒 Please log in to view and manage documents.</p>
          <p>Click "Switch to Admin Mode" above to authenticate.</p>
        </div>
      </div>
    );
  }

  if (loading) return <div className="loading">Loading documents...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="document-list">
      <h2>Documents ({documents.length})</h2>
      
      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search by tag..."
            value={searchTag}
            onChange={(e) => setSearchTag(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="btn-search">
            Search
          </button>
          {searchTag && (
            <button type="button" onClick={handleClearSearch} className="btn-clear">
              Clear
            </button>
          )}
        </form>
        {searchTag && (
          <>
            <p className="search-info">Showing results for: "{searchTag}"</p>
            {documents.length > 0 && (
              <div className="export-by-tag-section">
                <p><strong>Export all documents with tag "{searchTag}":</strong></p>
                <div className="export-buttons">
                  <button 
                    onClick={() => handleExportByTag(searchTag, 'csv')}
                    className="btn-export btn-export-csv"
                    title="Export as CSV (combined data)"
                  >
                    📊 CSV
                  </button>
                  <button 
                    onClick={() => handleExportByTag(searchTag, 'xlsx')}
                    className="btn-export btn-export-xlsx"
                    title="Export as XLSX (multiple sheets)"
                  >
                    📈 XLSX
                  </button>
                  <button 
                    onClick={() => handleExportByTag(searchTag, 'json')}
                    className="btn-export btn-export-json"
                    title="Export as JSON (with metadata)"
                  >
                    📄 JSON
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
      
      {documents.length === 0 ? (
        <p className="no-documents">No documents uploaded yet.</p>
      ) : (
        <div className="documents-grid">
          {documents.map((doc) => (
            <div key={doc.id} className="document-card">
              <div className="document-header">
                <h3>{doc.tag}</h3>
                {doc.error_count > 0 && (
                  <span className="error-badge">{doc.error_count} errors</span>
                )}
              </div>
              
              <div className="document-info">
                <p><strong>File:</strong> {doc.filename}</p>
                <p><strong>Type:</strong> {doc.file_type.toUpperCase()}</p>
                <p><strong>Created:</strong> {new Date(doc.created_at).toLocaleDateString()}</p>
                {doc.created_by && <p><strong>Created by:</strong> {doc.created_by.replace('user_', '')}</p>}
                <p><strong>Updated:</strong> {new Date(doc.updated_at).toLocaleDateString()}</p>
                {doc.updated_by && <p><strong>Updated by:</strong> {doc.updated_by.replace('user_', '')}</p>}
              </div>
              
              <div className="document-actions">
                <button 
                  onClick={() => onDocumentSelect(doc.id)}
                  className="btn-primary"
                >
                  View/Edit
                </button>
                
                <div className="export-dropdown">
                  <button className="btn-export-toggle">
                    📥 Export ▼
                  </button>
                  <div className="export-dropdown-content">
                    <button 
                      onClick={() => handleExportDocument(doc.id, doc.tag, doc.filename, 'csv')}
                      className="btn-export-option"
                      title="Export as CSV file"
                    >
                      📊 CSV
                    </button>
                    <button 
                      onClick={() => handleExportDocument(doc.id, doc.tag, doc.filename, 'xlsx')}
                      className="btn-export-option"
                      title="Export as Excel file"
                    >
                      📈 XLSX
                    </button>
                    <button 
                      onClick={() => handleExportDocument(doc.id, doc.tag, doc.filename, 'json')}
                      className="btn-export-option"
                      title="Export as JSON file with metadata"
                    >
                      📄 JSON
                    </button>
                  </div>
                </div>
                
                <button 
                  onClick={() => handleDelete(doc.id, doc.tag)}
                  className="btn-danger"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentList;