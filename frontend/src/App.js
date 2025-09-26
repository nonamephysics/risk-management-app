import React, { useState } from 'react';
import { AuthProvider } from './contexts/AuthContext';
import AdminToggle from './components/AdminToggle';
import FileUpload from './components/FileUpload';
import DocumentList from './components/DocumentList';
import DocumentViewer from './components/DocumentViewer';
import './App.css';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);

  const handleUploadSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const handleDocumentSelect = (documentId) => {
    setSelectedDocumentId(documentId);
  };

  const handleCloseViewer = () => {
    setSelectedDocumentId(null);
    setRefreshTrigger(prev => prev + 1); // Refresh list in case of edits
  };

  return (
    <AuthProvider>
      <div className="App">
        <AdminToggle>
          <header className="App-header">
            <h1>Risk App - Document Management</h1>
          </header>
          
          <main className="App-main">
        {selectedDocumentId ? (
          <DocumentViewer 
            documentId={selectedDocumentId}
            onClose={handleCloseViewer}
          />
        ) : (
          <div className="main-content">
            <div className="upload-section">
              <FileUpload onUploadSuccess={handleUploadSuccess} />
            </div>
            
            <div className="list-section">
              <DocumentList 
                refreshTrigger={refreshTrigger}
                onDocumentSelect={handleDocumentSelect}
              />
            </div>
          </div>
        )}
          </main>
        </AdminToggle>
      </div>
    </AuthProvider>
  );
}

export default App;