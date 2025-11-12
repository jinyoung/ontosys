from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.neo4j_client import neo4j_client
from app.api import documents, extraction, graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Event-Storming to Neo4j API",
    description="Extract domain concepts from documents and visualize as graph",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(extraction.router)
app.include_router(graph.router)


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    logger.info("Starting Event-Storming API...")
    try:
        neo4j_client.connect()
        if neo4j_client._driver:
            logger.info("✓ Neo4j connected")
        else:
            logger.warning("⚠ Neo4j connection failed - API will run in limited mode")
    except Exception as e:
        logger.warning(f"⚠ Failed to connect to Neo4j: {e} - API will run in limited mode")


@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown"""
    logger.info("Shutting down Event-Storming API...")
    neo4j_client.close()
    logger.info("✓ Connections closed")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Event-Storming to Neo4j API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Neo4j connection
        if neo4j_client._driver:
            neo4j_client.driver.verify_connectivity()
            return {"status": "healthy", "neo4j": "connected"}
        else:
            return {"status": "degraded", "neo4j": "disconnected", "api": "running"}
    except Exception as e:
        return {"status": "degraded", "neo4j": "disconnected", "api": "running", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )



