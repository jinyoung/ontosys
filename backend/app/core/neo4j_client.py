from neo4j import GraphDatabase, Driver
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j database client singleton"""
    
    _instance: Optional["Neo4jClient"] = None
    _driver: Optional[Driver] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        """Establish connection to Neo4j"""
        if self._driver is None:
            try:
                self._driver = GraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password)
                )
                # Test connection
                self._driver.verify_connectivity()
                logger.info(f"Connected to Neo4j at {settings.neo4j_uri}")
                self._init_schema()
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {e}")
                logger.warning("Neo4j connection failed - continuing without database")
                self._driver = None
    
    def _init_schema(self):
        """Initialize Neo4j schema (constraints and indexes)"""
        queries = [
            "CREATE CONSTRAINT agg_id IF NOT EXISTS FOR (a:Aggregate) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT cmd_id IF NOT EXISTS FOR (c:Command) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT evt_id IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT pol_id IF NOT EXISTS FOR (p:Policy) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (d:DocFrag) REQUIRE d.id IS UNIQUE",
            "CREATE INDEX docfrag_doc_page IF NOT EXISTS FOR (d:DocFrag) ON (d.doc_id, d.page)",
        ]
        
        with self._driver.session() as session:
            for query in queries:
                try:
                    session.run(query)
                    logger.info(f"Executed: {query}")
                except Exception as e:
                    logger.warning(f"Schema query failed (may already exist): {e}")
    
    def close(self):
        """Close Neo4j connection"""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")
            self._driver = None
    
    @property
    def driver(self) -> Driver:
        """Get Neo4j driver instance"""
        if self._driver is None:
            self.connect()
        return self._driver


# Global instance
neo4j_client = Neo4jClient()



