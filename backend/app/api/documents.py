from fastapi import APIRouter, UploadFile, File, HTTPException
import logging

from app.services.document_service import document_service
from app.services.graph_service import graph_service
from app.models.schemas import UploadResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/docs", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document (PDF/DOCX/TXT) and extract text fragments"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ['pdf', 'docx', 'doc', 'txt']:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_ext}"
            )
        
        # Read and save file
        content = await file.read()
        doc_id, file_path = await document_service.save_upload(file.filename, content)
        
        # Extract text fragments
        fragments = document_service.extract_text(file_path)
        
        # Store fragments in Neo4j
        graph_service.store_doc_fragments(fragments)
        
        # Count pages (approximate)
        pages = max([f.page for f in fragments]) if fragments else 0
        
        logger.info(f"Uploaded document {doc_id}: {len(fragments)} fragments, {pages} pages")
        
        return UploadResponse(
            doc_id=doc_id,
            filename=file.filename,
            pages=pages,
            fragments=len(fragments)
        )
    
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



