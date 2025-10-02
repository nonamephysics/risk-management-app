from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
import pandas as pd
import json
import io

from app.database import get_database
from app.models.document import Document, DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse


class DocumentService:
    def __init__(self):
        self.collection_name = "documents"

    async def get_collection(self):
        db = await get_database()
        return db[self.collection_name]

    async def is_tag_unique(self, tag: str, exclude_id: Optional[str] = None) -> bool:
        """Check if a tag is unique (not used by any other document)"""
        collection = await self.get_collection()
        
        # Build query to check for existing tag
        query = {"tag": tag}
        
        # Exclude current document if updating
        if exclude_id and ObjectId.is_valid(exclude_id):
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        
        # Count documents with this tag
        count = await collection.count_documents(query)
        return count == 0

    async def create_document(self, document_data: Dict[str, Any]) -> str:
        """Create a new document in the database"""
        collection = await self.get_collection()
        
        document = Document(**document_data)
        result = await collection.insert_one(document.dict(by_alias=True))
        return str(result.inserted_id)

    async def get_document_by_id(self, document_id: str) -> Optional[DocumentResponse]:
        """Get a document by its ID"""
        if not ObjectId.is_valid(document_id):
            return None
            
        collection = await self.get_collection()
        document = await collection.find_one({"_id": ObjectId(document_id)})
        
        if document:
            document["id"] = str(document["_id"])
            del document["_id"]
            
            # Ensure required fields exist with default values
            from datetime import datetime
            if "created_at" not in document:
                document["created_at"] = datetime.utcnow()
            if "updated_at" not in document:
                document["updated_at"] = datetime.utcnow()
            
            return DocumentResponse(**document)
        return None

    async def get_all_documents(self) -> List[DocumentListResponse]:
        """Get all documents with basic information"""
        collection = await self.get_collection()
        cursor = collection.find({}, {
            "tag": 1,
            "filename": 1,
            "file_type": 1,
            "created_at": 1,
            "updated_at": 1,
            "validation_errors": 1,
            "created_by": 1,
            "updated_by": 1
        })
        
        documents = []
        async for document in cursor:
            document["id"] = str(document["_id"])
            document["error_count"] = len(document.get("validation_errors", []))
            del document["_id"]
            if "validation_errors" in document:
                del document["validation_errors"]
            
            # Ensure required fields exist with default values
            from datetime import datetime
            if "created_at" not in document:
                document["created_at"] = datetime.utcnow()
            if "updated_at" not in document:
                document["updated_at"] = datetime.utcnow()
            
            documents.append(DocumentListResponse(**document))
        
        return documents

    async def get_documents_by_tag(self, tag: str) -> List[DocumentListResponse]:
        """Get documents by tag"""
        collection = await self.get_collection()
        cursor = collection.find({"tag": tag}, {
            "tag": 1,
            "filename": 1,
            "file_type": 1,
            "created_at": 1,
            "updated_at": 1,
            "validation_errors": 1,
            "created_by": 1,
            "updated_by": 1
        })
        
        documents = []
        async for document in cursor:
            document["id"] = str(document["_id"])
            document["error_count"] = len(document.get("validation_errors", []))
            del document["_id"]
            if "validation_errors" in document:
                del document["validation_errors"]
            
            # Ensure required fields exist with default values
            from datetime import datetime
            if "created_at" not in document:
                document["created_at"] = datetime.utcnow()
            if "updated_at" not in document:
                document["updated_at"] = datetime.utcnow()
            
            documents.append(DocumentListResponse(**document))
        
        return documents

    async def get_documents_by_tag_full(self, tag: str) -> List[DocumentResponse]:
        """Get documents by tag with full content"""
        collection = await self.get_collection()
        cursor = collection.find({"tag": tag})
        
        documents = []
        async for document in cursor:
            document["id"] = str(document["_id"])
            del document["_id"]
            
            # Ensure required fields exist with default values
            from datetime import datetime
            if "created_at" not in document:
                document["created_at"] = datetime.utcnow()
            if "updated_at" not in document:
                document["updated_at"] = datetime.utcnow()
            
            documents.append(DocumentResponse(**document))
        
        return documents

    async def update_document(self, document_id: str, update_data: DocumentUpdate) -> bool:
        """Update a document"""
        if not ObjectId.is_valid(document_id):
            return False
            
        collection = await self.get_collection()
        
        update_dict = update_data.dict(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": update_dict}
        )
        
        return result.modified_count > 0

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        if not ObjectId.is_valid(document_id):
            return False
            
        collection = await self.get_collection()
        result = await collection.delete_one({"_id": ObjectId(document_id)})
        
        return result.deleted_count > 0

    async def document_exists(self, document_id: str) -> bool:
        """Check if a document exists"""
        if not ObjectId.is_valid(document_id):
            return False
            
        collection = await self.get_collection()
        count = await collection.count_documents({"_id": ObjectId(document_id)})
        return count > 0

    async def export_document_to_csv(self, document_id: str) -> Optional[bytes]:
        """Export a document to CSV format"""
        document = await self.get_document_by_id(document_id)
        if not document or not document.data:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(document.data)
        
        # Convert to CSV bytes
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        
        return csv_buffer.getvalue().encode('utf-8')

    async def export_document_to_xlsx(self, document_id: str) -> Optional[bytes]:
        """Export a document to XLSX format"""
        document = await self.get_document_by_id(document_id)
        if not document or not document.data:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(document.data)
        
        # Convert to Excel bytes
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
        
        excel_buffer.seek(0)
        return excel_buffer.getvalue()

    async def export_document_to_json(self, document_id: str) -> Optional[bytes]:
        """Export a document to JSON format"""
        document = await self.get_document_by_id(document_id)
        if not document or not document.data:
            return None
        
        # Create export structure
        export_data = {
            "document_info": {
                "id": document.id,
                "tag": document.tag,
                "filename": document.filename,
                "file_type": document.file_type,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
                "created_by": document.created_by,
                "updated_by": document.updated_by
            },
            "data": document.data,
            "validation_errors": [error.dict() for error in document.validation_errors]
        }
        
        # Convert to JSON bytes
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        return json_str.encode('utf-8')

    async def export_documents_by_tag_to_csv(self, tag: str) -> Optional[bytes]:
        """Export all documents with a specific tag to CSV format (combined)"""
        documents = await self.get_documents_by_tag_full(tag)
        if not documents:
            return None
        
        all_data = []
        for doc in documents:
            if doc.data:
                # Add document metadata to each row
                for row in doc.data:
                    row_with_meta = {
                        'document_id': doc.id,
                        'document_tag': doc.tag,
                        'document_filename': doc.filename,
                        **row
                    }
                    all_data.append(row_with_meta)
        
        if not all_data:
            return None
        
        # Convert to DataFrame and CSV
        df = pd.DataFrame(all_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        
        return csv_buffer.getvalue().encode('utf-8')

    async def export_documents_by_tag_to_xlsx(self, tag: str) -> Optional[bytes]:
        """Export all documents with a specific tag to XLSX format (multiple sheets)"""
        documents = await self.get_documents_by_tag_full(tag)
        if not documents:
            return None
        
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            for i, doc in enumerate(documents):
                if doc.data:
                    df = pd.DataFrame(doc.data)
                    sheet_name = f"{doc.tag}_{i+1}" if len(documents) > 1 else doc.tag
                    # Excel sheet names can't be longer than 31 characters
                    sheet_name = sheet_name[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        excel_buffer.seek(0)
        return excel_buffer.getvalue()

    async def export_documents_by_tag_to_json(self, tag: str) -> Optional[bytes]:
        """Export all documents with a specific tag to JSON format"""
        documents = await self.get_documents_by_tag_full(tag)
        if not documents:
            return None
        
        # Create export structure for multiple documents
        export_data = {
            "tag": tag,
            "export_timestamp": datetime.utcnow().isoformat(),
            "documents": []
        }
        
        for doc in documents:
            doc_data = {
                "document_info": {
                    "id": doc.id,
                    "tag": doc.tag,
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat(),
                    "created_by": doc.created_by,
                    "updated_by": doc.updated_by
                },
                "data": doc.data,
                "validation_errors": [error.dict() for error in doc.validation_errors]
            }
            export_data["documents"].append(doc_data)
        
        # Convert to JSON bytes
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
        return json_str.encode('utf-8')