from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.security import HTTPBearer
from typing import List
import io
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from typing import List
import io
import traceback
import traceback

from app.services.document_service import DocumentService
from app.services.file_service import FileValidationService
from app.models.document import DocumentResponse, DocumentListResponse, DocumentUpdate
from app.security import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])

# Security scheme for OpenAPI
security = HTTPBearer()


async def get_document_service():
    return DocumentService()


@router.post("/excel-sheets", dependencies=[Depends(security)])
async def get_excel_sheets(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Get sheet names from Excel file for selection
    
    Requires authentication with Bearer token.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400, 
                detail="Only Excel files (.xlsx, .xls) are supported for sheet selection"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Get sheet names
        from app.services.file_service import FileValidationService
        sheet_names = FileValidationService.get_excel_sheet_names(file_content, file.filename)
        
        return {
            "filename": file.filename,
            "sheet_names": sheet_names,
            "total_sheets": len(sheet_names)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Failed to get Excel sheets: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error reading Excel file: {str(e)}")

@router.post("/upload-debug", dependencies=[Depends(security)])
async def debug_upload(request: Request):
    """
    Debug endpoint to see raw request data
    
    Requires authentication with Bearer token.
    """
    print("DEBUG: Raw upload debug endpoint reached")
    print(f"DEBUG: Headers: {dict(request.headers)}")
    print(f"DEBUG: Method: {request.method}")
    print(f"DEBUG: URL: {request.url}")
    
    try:
        # Try to read the raw body
        body = await request.body()
        print(f"DEBUG: Body length: {len(body)}")
        print(f"DEBUG: Content-Type: {request.headers.get('content-type', 'NOT SET')}")
        
        # Try to parse form data
        form = await request.form()
        print(f"DEBUG: Form keys: {list(form.keys())}")
        for key in form.keys():
            value = form[key]
            if hasattr(value, 'filename'):
                print(f"DEBUG: Form field '{key}': File {value.filename} (size: {getattr(value, 'size', 'unknown')})")
            else:
                print(f"DEBUG: Form field '{key}': '{value}'")
        
        return {"status": "debug", "form_keys": list(form.keys())}
    except Exception as e:
        print(f"DEBUG: Error parsing request: {str(e)}")
        print(f"DEBUG: Error type: {type(e)}")
        return {"error": str(e)}

@router.post("/upload", response_model=dict, dependencies=[Depends(security)])
async def upload_document(
    request: Request,
    current_user: dict = Depends(get_current_user),
    file: UploadFile = File(...),
    tag: str = Form(...),
    sheet_name: str = Form(None),
    document_service: DocumentService = Depends(get_document_service)
):
    """Upload a CSV, XLSX, SAS7BDAT, or XPT file with validation (Excel files support sheet selection)"""
    print("DEBUG: Upload endpoint reached successfully")
    
    try:
        print(f"DEBUG: Upload attempt - file: {file.filename if file else 'NO FILE'}, tag: '{tag}', sheet: '{sheet_name}', user: {current_user}")
        print(f"DEBUG: File content type: {file.content_type if file else 'NO FILE'}")
        print(f"DEBUG: File object: {type(file)}")
        print(f"DEBUG: Tag object: {type(tag)}")
        print(f"DEBUG: Sheet name: {sheet_name}")
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        
        # Validate inputs exist
        if not file:
            print("ERROR: No file object received")
            raise HTTPException(status_code=422, detail="No file provided")
        
        if not hasattr(file, 'filename') or not file.filename:
            print("ERROR: File has no filename")
            raise HTTPException(status_code=422, detail="File must have a filename")
        
        if not tag or not tag.strip():
            print(f"ERROR: Invalid tag: '{tag}'")
            raise HTTPException(status_code=422, detail="Tag is required and cannot be empty")
        
        # Check if tag is unique
        tag_is_unique = await document_service.is_tag_unique(tag.strip())
        if not tag_is_unique:
            print(f"ERROR: Tag already exists: '{tag}'")
            raise HTTPException(status_code=409, detail=f"Tag '{tag.strip()}' already exists. Please choose a different tag.")
        
        # Validate file type
        supported_extensions = ('.csv', '.xlsx', '.xls', '.sas7bdat', '.xpt')
        if not file.filename.lower().endswith(supported_extensions):
            print(f"ERROR: Invalid file type: {file.filename}")
            raise HTTPException(
                status_code=400, 
                detail="Only CSV, XLSX, SAS7BDAT, and XPT files are supported"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error in upload validation: {str(e)}")
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Parse file and get data with metadata (with optional sheet selection for Excel files)
        data, file_type, metadata = FileValidationService.read_file_with_metadata(file_content, file.filename, sheet_name)
        
        # Validate for non-ASCII characters
        validation_errors = FileValidationService.detect_non_ascii_characters(data)
        
        # Prepare main document data
        document_data = {
            "tag": tag.strip(),
            "filename": file.filename,
            "file_type": file_type,
            "data": data,
            "validation_errors": [error.dict() for error in validation_errors],
            "created_by": current_user.get("user_id", "unknown")
        }
        
        # Save main document to database
        document_id = await document_service.create_document(document_data)
        
        # For SAS7BDAT and XPT files, also save metadata as a separate document
        metadata_document_id = None
        if file_type in ['sas7bdat', 'xpt'] and metadata:
            # Check if metadata tag is unique
            metadata_tag = f"{tag.strip()}_meta"
            meta_tag_unique = await document_service.is_tag_unique(metadata_tag)
            
            if meta_tag_unique:
                # Convert metadata to list format for storage
                metadata_as_list = [{"metadata_key": key, "metadata_value": str(value)} for key, value in metadata.items()]
                
                metadata_document_data = {
                    "tag": metadata_tag,
                    "filename": f"{file.filename}_metadata.json",
                    "file_type": "metadata",
                    "data": metadata_as_list,
                    "validation_errors": [],
                    "created_by": current_user.get("user_id", "unknown"),
                    "parent_document_id": document_id  # Link to main document
                }
                
                metadata_document_id = await document_service.create_document(metadata_document_data)
                print(f"DEBUG: Created metadata document with ID: {metadata_document_id}")
            else:
                print(f"WARNING: Metadata tag '{metadata_tag}' already exists, skipping metadata upload")
        
        response_data = {
            "message": "File uploaded successfully",
            "document_id": document_id,
            "validation_errors": [error.dict() for error in validation_errors],
            "has_errors": len(validation_errors) > 0
        }
        
        # Add metadata info if applicable
        if metadata_document_id:
            response_data["metadata_document_id"] = metadata_document_id
            response_data["metadata_tag"] = f"{tag.strip()}_meta"
            response_data["message"] = f"File and metadata uploaded successfully. Data: '{tag.strip()}', Metadata: '{tag.strip()}_meta'"
        
        return response_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/", response_model=List[DocumentListResponse], dependencies=[Depends(security)])
async def get_all_documents(
    document_service: DocumentService = Depends(get_document_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all documents with basic information
    
    Requires authentication with Bearer token.
    """
    return await document_service.get_all_documents()


@router.get("/tag/{tag}", response_model=List[DocumentResponse], dependencies=[Depends(security)])
async def get_documents_by_tag(
    tag: str,
    document_service: DocumentService = Depends(get_document_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get documents by tag with full content
    
    Requires authentication with Bearer token.
    """
    documents = await document_service.get_documents_by_tag_full(tag)
    return documents


@router.get("/{document_id}", response_model=DocumentResponse, dependencies=[Depends(security)])
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific document by ID
    
    Requires authentication with Bearer token.
    """
    document = await document_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.put("/{document_id}", response_model=dict, dependencies=[Depends(security)])
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    document_service: DocumentService = Depends(get_document_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a document
    
    Requires authentication with Bearer token.
    """
    if not await document_service.document_exists(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if tag is unique (if tag is being updated)
    if update_data.tag and update_data.tag.strip():
        tag_is_unique = await document_service.is_tag_unique(update_data.tag.strip(), document_id)
        if not tag_is_unique:
            raise HTTPException(status_code=409, detail=f"Tag '{update_data.tag.strip()}' already exists. Please choose a different tag.")
        # Ensure we use the trimmed tag
        update_data.tag = update_data.tag.strip()
    
    # Add user information to update data
    update_data.updated_by = current_user.get("user_id", "unknown")
    
    success = await document_service.update_document(document_id, update_data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update document")
    
    return {"message": "Document updated successfully"}


@router.delete("/{document_id}", response_model=dict, dependencies=[Depends(security)])
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a document
    
    Requires authentication with Bearer token.
    """
    if not await document_service.document_exists(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    
    success = await document_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete document")
    
    return {"message": "Document deleted successfully"}