from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import logging
import uuid
from typing import Dict

from app.services.extraction_service import extraction_service
from app.services.graph_service import graph_service
from app.core.neo4j_client import neo4j_client
from app.models.schemas import (
    ExtractionJobResponse, JobStatusResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/extract", tags=["extraction"])


# Simple in-memory job tracker (for MVP, use Redis in production)
job_status_store: Dict[str, JobStatusResponse] = {}


class ExtractRequest(BaseModel):
    doc_id: str


async def run_extraction_job(job_id: str, doc_id: str):
    """Background task to run extraction"""
    try:
        job_status_store[job_id] = JobStatusResponse(
            job_id=job_id,
            status="running",
            progress=10,
            message="Retrieving document fragments..."
        )
        
        # Get document fragments from Neo4j
        with neo4j_client.driver.session() as session:
            result = session.run(
                "MATCH (d:DocFrag {doc_id: $doc_id}) RETURN d",
                doc_id=doc_id
            )
            fragments = []
            for record in result:
                node = record["d"]
                from app.models.schemas import DocFragNode
                fragments.append(DocFragNode(
                    id=node["id"],
                    doc_id=node["doc_id"],
                    page=node["page"],
                    span=node["span"],
                    text=node["text"]
                ))
        
        if not fragments:
            job_status_store[job_id] = JobStatusResponse(
                job_id=job_id,
                status="error",
                progress=0,
                message="No fragments found for document"
            )
            return
        
        job_status_store[job_id] = JobStatusResponse(
            job_id=job_id,
            status="running",
            progress=30,
            message="Extracting domain concepts..."
        )
        
        # Run extraction
        extraction_output = await extraction_service.extract_from_fragments(fragments)
        
        job_status_store[job_id] = JobStatusResponse(
            job_id=job_id,
            status="running",
            progress=70,
            message="Storing graph data..."
        )
        
        # Store in Neo4j
        graph_service.store_extraction(doc_id, extraction_output)
        
        job_status_store[job_id] = JobStatusResponse(
            job_id=job_id,
            status="done",
            progress=100,
            message=f"Extracted {len(extraction_output.aggregates)} aggregates, "
                   f"{len(extraction_output.commands)} commands, "
                   f"{len(extraction_output.events)} events, "
                   f"{len(extraction_output.policies)} policies"
        )
        
        logger.info(f"Extraction job {job_id} completed for doc {doc_id}")
    
    except Exception as e:
        logger.error(f"Extraction job {job_id} failed: {e}")
        job_status_store[job_id] = JobStatusResponse(
            job_id=job_id,
            status="error",
            progress=0,
            message=str(e)
        )


@router.post("/run", response_model=ExtractionJobResponse)
async def start_extraction(
    request: ExtractRequest,
    background_tasks: BackgroundTasks
):
    """Start extraction job for a document"""
    job_id = f"job-{uuid.uuid4()}"
    
    # Initialize job status
    job_status_store[job_id] = JobStatusResponse(
        job_id=job_id,
        status="queued",
        progress=0,
        message="Job queued"
    )
    
    # Add background task
    background_tasks.add_task(run_extraction_job, job_id, request.doc_id)
    
    return ExtractionJobResponse(
        job_id=job_id,
        doc_id=request.doc_id,
        status="queued"
    )


@router.get("/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get extraction job status"""
    if job_id not in job_status_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_status_store[job_id]



