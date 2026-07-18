from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from datetime import datetime
import uuid
from app.services.document_service import document_service

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md", "csv", "pptx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

def validate_file(file: UploadFile):
    # Validate extension
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension .{file_ext} not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check size constraint if content_length header is available
    # (Fallback check happens during stream reading in service layer)
    return file_ext

@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_document(file: UploadFile = File(...)):
    file_ext = validate_file(file)
    
    try:
        # Read file contents securely
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the maximum 50 MB limit."
            )
            
        # Compile metadata required by Section 5.1
        metadata = {
            "filename": file.filename,
            "upload_time": datetime.utcnow().isoformat(),
            "source_type": file_ext
        }
        
        # Delegate parsing, chunking, embedding, and upserting to document_service
        result = await document_service.process_and_store(
            filename=file.filename,
            contents=contents,
            file_ext=file_ext,
            metadata=metadata
        )
        return {"status": "success", "data": result}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )

@router.get("", response_model=List[dict])
async def list_documents():
    try:
        # Pulls tracked documents from metadata inventory
        docs = await document_service.get_all_documents()
        return docs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch documents: {str(e)}"
        )

@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: str):
    try:
        success = await document_service.delete_document_by_id(document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found."
            )
        return {"status": "success", "message": f"Document {document_id} deleted successfully from index."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )