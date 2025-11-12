from fastapi import APIRouter, HTTPException
import logging

from app.services.graph_service import graph_service
from app.models.schemas import (
    GraphData, NodeCreateRequest, EdgeCreateRequest,
    MSRecommendationResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("", response_model=GraphData)
async def get_graph(doc_id: str):
    """Get graph data for a document"""
    try:
        graph_data = graph_service.get_graph(doc_id)
        logger.info(f"Retrieved graph for doc {doc_id}: "
                   f"{len(graph_data.nodes)} nodes, {len(graph_data.edges)} edges")
        return graph_data
    except Exception as e:
        logger.error(f"Failed to get graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nodes")
async def create_or_update_nodes(request: NodeCreateRequest):
    """Create or update graph nodes (batch)"""
    try:
        # Implementation for node creation/update
        # For MVP, we'll keep it simple
        logger.info(f"Received request to create/update {len(request.nodes)} nodes")
        return {"status": "success", "count": len(request.nodes)}
    except Exception as e:
        logger.error(f"Failed to create/update nodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edges")
async def create_or_update_edges(request: EdgeCreateRequest):
    """Create or update graph edges (batch)"""
    try:
        logger.info(f"Received request to create/update {len(request.edges)} edges")
        return {"status": "success", "count": len(request.edges)}
    except Exception as e:
        logger.error(f"Failed to create/update edges: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    """Delete a graph node"""
    try:
        # Implementation for node deletion
        logger.info(f"Deleting node {node_id}")
        return {"status": "success", "deleted": node_id}
    except Exception as e:
        logger.error(f"Failed to delete node: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/edges/{edge_id}")
async def delete_edge(edge_id: str):
    """Delete a graph edge"""
    try:
        logger.info(f"Deleting edge {edge_id}")
        return {"status": "success", "deleted": edge_id}
    except Exception as e:
        logger.error(f"Failed to delete edge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/node/{node_id}/trace")
async def get_node_trace(node_id: str):
    """Get source document traces for a node"""
    try:
        # Implementation for getting trace info
        logger.info(f"Getting trace for node {node_id}")
        return {"node_id": node_id, "traces": []}
    except Exception as e:
        logger.error(f"Failed to get trace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend/ms-candidates", response_model=MSRecommendationResponse)
async def recommend_microservices(doc_id: str):
    """Recommend microservice candidates based on graph structure"""
    try:
        candidates = graph_service.recommend_ms_candidates(doc_id)
        logger.info(f"Generated {len(candidates)} MS candidates for doc {doc_id}")
        return MSRecommendationResponse(clusters=candidates)
    except Exception as e:
        logger.error(f"Failed to recommend MS candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))



