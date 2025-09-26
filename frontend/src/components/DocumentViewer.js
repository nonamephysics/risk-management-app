import React, { useState, useEffect } from 'react';
import { documentService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import './DocumentViewer.css';

const DocumentViewer = ({ documentId, onClose }) => {
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedTag, setEditedTag] = useState('');
  const [editedData, setEditedData] = useState([]);
  const { getAuthHeaders } = useAuth();

  useEffect(() => {
    if (documentId) {
      fetchDocument();
    }
  }, [documentId]);

  const fetchDocument = async () => {
    try {
      setLoading(true);
      const authHeaders = getAuthHeaders();
      const data = await documentService.getDocumentById(documentId, authHeaders);
      setDocument(data);
      setEditedTag(data.tag);
      setEditedData([...data.data]);
      setError(null);
    } catch (err) {
      console.error('Error fetching document:', err);
      setError('Failed to load document');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const authHeaders = getAuthHeaders();
      await documentService.updateDocument(documentId, {
        tag: editedTag,
        data: editedData
      }, authHeaders);
      
      setDocument(prev => ({
        ...prev,
        tag: editedTag,
        data: editedData
      }));
      
      setIsEditing(false);
      alert('Document updated successfully');
    } catch (err) {
      console.error('Error updating document:', err);
      alert('Failed to update document');
    }
  };

  const handleCellEdit = (rowIndex, column, value) => {
    const newData = [...editedData];
    newData[rowIndex][column] = value;
    setEditedData(newData);
  };

  if (loading) return <div className="loading">Loading document...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!document) return <div className="error">Document not found</div>;

  const columns = document.data.length > 0 ? Object.keys(document.data[0]) : [];

  return (
    <div className="document-viewer">
      <div className="viewer-header">
        <div className="header-left">
          <h2>{isEditing ? 'Edit Document' : 'View Document'}</h2>
          <div className="document-meta">
            <p><strong>File:</strong> {document.filename}</p>
            <p><strong>Type:</strong> {document.file_type.toUpperCase()}</p>
            <p><strong>Created:</strong> {new Date(document.created_at).toLocaleDateString()}</p>
            {document.created_by && <p><strong>Created by:</strong> {document.created_by.replace('user_', '')}</p>}
            <p><strong>Updated:</strong> {new Date(document.updated_at).toLocaleDateString()}</p>
            {document.updated_by && <p><strong>Updated by:</strong> {document.updated_by.replace('user_', '')}</p>}
            <p><strong>Rows:</strong> {document.data.length}</p>
          </div>
        </div>
        
        <div className="header-actions">
          {isEditing ? (
            <>
              <button onClick={handleSave} className="btn-success">Save Changes</button>
              <button onClick={() => {
                setIsEditing(false);
                setEditedTag(document.tag);
                setEditedData([...document.data]);
              }} className="btn-secondary">Cancel</button>
            </>
          ) : (
            <button onClick={() => setIsEditing(true)} className="btn-primary">Edit</button>
          )}
          <button onClick={onClose} className="btn-secondary">Close</button>
        </div>
      </div>

      <div className="document-info">
        <div className="tag-section">
          <label><strong>Tag:</strong></label>
          {isEditing ? (
            <input
              type="text"
              value={editedTag}
              onChange={(e) => setEditedTag(e.target.value)}
              className="tag-input"
            />
          ) : (
            <span>{document.tag}</span>
          )}
        </div>

        {document.validation_errors.length > 0 && (
          <div className="validation-errors">
            <h3>Validation Errors ({document.validation_errors.length})</h3>
            <div className="error-list">
              {document.validation_errors.map((error, index) => (
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

      <div className="data-table-container">
        <h3>Data ({document.data.length} rows)</h3>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                {columns.map(column => (
                  <th key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(isEditing ? editedData : document.data).map((row, rowIndex) => (
                <tr key={rowIndex}>
                  <td>{rowIndex + 1}</td>
                  {columns.map(column => (
                    <td key={column}>
                      {isEditing ? (
                        <input
                          type="text"
                          value={row[column] || ''}
                          onChange={(e) => handleCellEdit(rowIndex, column, e.target.value)}
                          className="cell-input"
                        />
                      ) : (
                        <span>{row[column] || ''}</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;