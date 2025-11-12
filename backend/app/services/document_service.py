import uuid
import os
from pathlib import Path
from typing import List, Tuple
import logging
from pypdf import PdfReader
from docx import Document
import aiofiles

from app.core.config import settings
from app.models.schemas import DocFragNode

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document upload and text extraction"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_upload(self, filename: str, content: bytes) -> Tuple[str, Path]:
        """Save uploaded file and return doc_id and file path"""
        doc_id = f"doc-{uuid.uuid4()}"
        file_ext = Path(filename).suffix
        file_path = self.upload_dir / f"{doc_id}{file_ext}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        logger.info(f"Saved document {doc_id} to {file_path}")
        return doc_id, file_path
    
    def extract_text(self, file_path: Path) -> List[DocFragNode]:
        """Extract text from document and create fragments"""
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return self._extract_from_docx(file_path)
        elif file_ext == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def _extract_from_pdf(self, file_path: Path) -> List[DocFragNode]:
        """Extract text from PDF with page-based chunking"""
        fragments = []
        doc_id = file_path.stem
        
        try:
            reader = PdfReader(str(file_path))
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if not text.strip():
                    continue
                
                # Split into chunks (max 1200 chars)
                chunks = self._chunk_text(text, max_length=1200)
                char_offset = 0
                
                for chunk in chunks:
                    frag_id = f"{doc_id}-p{page_num}-{len(fragments)}"
                    fragment = DocFragNode(
                        id=frag_id,
                        doc_id=doc_id,
                        page=page_num,
                        span=[char_offset, char_offset + len(chunk)],
                        text=chunk
                    )
                    fragments.append(fragment)
                    char_offset += len(chunk)
            
            logger.info(f"Extracted {len(fragments)} fragments from PDF")
            return fragments
        
        except Exception as e:
            logger.error(f"Failed to extract PDF: {e}")
            raise
    
    def _extract_from_docx(self, file_path: Path) -> List[DocFragNode]:
        """Extract text from DOCX with paragraph-based chunking"""
        fragments = []
        doc_id = file_path.stem
        
        try:
            doc = Document(str(file_path))
            text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
            full_text = "\n\n".join(text_parts)
            
            # Split into chunks
            chunks = self._chunk_text(full_text, max_length=1200)
            char_offset = 0
            
            for idx, chunk in enumerate(chunks):
                frag_id = f"{doc_id}-chunk-{idx}"
                fragment = DocFragNode(
                    id=frag_id,
                    doc_id=doc_id,
                    page=1,  # DOCX doesn't have pages in the same way
                    span=[char_offset, char_offset + len(chunk)],
                    text=chunk
                )
                fragments.append(fragment)
                char_offset += len(chunk)
            
            logger.info(f"Extracted {len(fragments)} fragments from DOCX")
            return fragments
        
        except Exception as e:
            logger.error(f"Failed to extract DOCX: {e}")
            raise
    
    def _extract_from_txt(self, file_path: Path) -> List[DocFragNode]:
        """Extract text from plain text file"""
        fragments = []
        doc_id = file_path.stem
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            chunks = self._chunk_text(text, max_length=1200)
            char_offset = 0
            
            for idx, chunk in enumerate(chunks):
                frag_id = f"{doc_id}-chunk-{idx}"
                fragment = DocFragNode(
                    id=frag_id,
                    doc_id=doc_id,
                    page=1,
                    span=[char_offset, char_offset + len(chunk)],
                    text=chunk
                )
                fragments.append(fragment)
                char_offset += len(chunk)
            
            logger.info(f"Extracted {len(fragments)} fragments from TXT")
            return fragments
        
        except Exception as e:
            logger.error(f"Failed to extract TXT: {e}")
            raise
    
    def _chunk_text(self, text: str, max_length: int = 1200) -> List[str]:
        """Split text into chunks at paragraph boundaries"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_len = len(para)
            
            if current_length + para_len > max_length and current_chunk:
                # Save current chunk and start new one
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_len
            else:
                current_chunk.append(para)
                current_length += para_len + 2  # +2 for \n\n
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks


document_service = DocumentService()



