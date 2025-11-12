import uuid
import logging
from typing import List, Dict, Any, Optional
from neo4j import Session

from app.core.neo4j_client import neo4j_client
from app.models.schemas import (
    DocFragNode, ExtractionOutput, GraphData, GraphNode, GraphEdge,
    MSCandidate
)

logger = logging.getLogger(__name__)


class GraphService:
    """Service for managing Neo4j graph operations"""
    
    def store_doc_fragments(self, fragments: List[DocFragNode]):
        """Store document fragments in Neo4j"""
        with neo4j_client.driver.session() as session:
            for frag in fragments:
                session.execute_write(self._create_doc_frag, frag)
        logger.info(f"Stored {len(fragments)} document fragments")
    
    @staticmethod
    def _create_doc_frag(tx, frag: DocFragNode):
        """Create DocFrag node"""
        query = """
        MERGE (d:DocFrag {id: $id})
        SET d.doc_id = $doc_id,
            d.page = $page,
            d.span = $span,
            d.text = $text
        """
        tx.run(query, 
               id=frag.id,
               doc_id=frag.doc_id,
               page=frag.page,
               span=frag.span,
               text=frag.text)
    
    def store_extraction(self, doc_id: str, extraction: ExtractionOutput):
        """Store extracted entities and create graph relationships"""
        with neo4j_client.driver.session() as session:
            # Create Aggregates
            agg_ids = {}
            for agg in extraction.aggregates:
                agg_id = f"agg-{uuid.uuid4()}"
                agg_ids[agg.name] = agg_id
                session.execute_write(self._create_aggregate, agg_id, doc_id, agg)
            
            # Create Commands
            cmd_ids = {}
            for cmd in extraction.commands:
                cmd_id = f"cmd-{uuid.uuid4()}"
                cmd_ids[cmd.name] = cmd_id
                session.execute_write(self._create_command, cmd_id, doc_id, cmd)
            
            # Create Events
            evt_ids = {}
            for evt in extraction.events:
                evt_id = f"evt-{uuid.uuid4()}"
                evt_ids[evt.name] = evt_id
                session.execute_write(self._create_event, evt_id, doc_id, evt)
            
            # Create Policies
            pol_ids = {}
            for pol in extraction.policies:
                pol_id = f"pol-{uuid.uuid4()}"
                pol_ids[pol.name] = pol_id
                session.execute_write(self._create_policy, pol_id, doc_id, pol)
            
            # Create relationships (basic heuristics)
            self._create_relationships(session, doc_id, cmd_ids, agg_ids, evt_ids, pol_ids, extraction)
        
        logger.info(f"Stored extraction for doc {doc_id}")
    
    @staticmethod
    def _create_aggregate(tx, agg_id: str, doc_id: str, agg):
        query = """
        CREATE (a:Aggregate {id: $id})
        SET a.doc_id = $doc_id,
            a.name = $name,
            a.description = $description,
            a.confidence = $confidence,
            a.tags = []
        """
        tx.run(query,
               id=agg_id,
               doc_id=doc_id,
               name=agg.name,
               description=agg.description,
               confidence=agg.confidence)
    
    @staticmethod
    def _create_command(tx, cmd_id: str, doc_id: str, cmd):
        query = """
        CREATE (c:Command {id: $id})
        SET c.doc_id = $doc_id,
            c.name = $name,
            c.intent = $intent,
            c.preconditions = $preconditions,
            c.confidence = $confidence
        """
        tx.run(query,
               id=cmd_id,
               doc_id=doc_id,
               name=cmd.name,
               intent=cmd.intent.value,
               preconditions=cmd.preconditions,
               confidence=cmd.confidence)
    
    @staticmethod
    def _create_event(tx, evt_id: str, doc_id: str, evt):
        query = """
        CREATE (e:Event {id: $id})
        SET e.doc_id = $doc_id,
            e.name = $name,
            e.schema_hint = $schema_hint,
            e.confidence = $confidence
        """
        tx.run(query,
               id=evt_id,
               doc_id=doc_id,
               name=evt.name,
               schema_hint=str(evt.schema_hint),
               confidence=evt.confidence)
    
    @staticmethod
    def _create_policy(tx, pol_id: str, doc_id: str, pol):
        query = """
        CREATE (p:Policy {id: $id})
        SET p.doc_id = $doc_id,
            p.name = $name,
            p.type = $type,
            p.condition = $condition,
            p.confidence = $confidence
        """
        tx.run(query,
               id=pol_id,
               doc_id=doc_id,
               name=pol.name,
               type=pol.type.value,
               condition=pol.condition,
               confidence=pol.confidence)
    
    def _create_relationships(self, session: Session, doc_id: str, 
                            cmd_ids: Dict, agg_ids: Dict, 
                            evt_ids: Dict, pol_ids: Dict,
                            extraction: ExtractionOutput):
        """Create relationships based on naming heuristics"""
        
        # Command -> Aggregate (TARGETS)
        for cmd in extraction.commands:
            cmd_id = cmd_ids.get(cmd.name)
            # Find aggregate by matching name in command
            for agg_name, agg_id in agg_ids.items():
                if agg_name.lower() in cmd.name.lower():
                    session.execute_write(
                        self._create_relationship,
                        cmd_id, agg_id, "TARGETS"
                    )
                    break
        
        # Command -> Event (EMITS)
        for cmd in extraction.commands:
            cmd_id = cmd_ids.get(cmd.name)
            # Match command "CreateX" with event "XCreated"
            for evt in extraction.events:
                evt_id = evt_ids.get(evt.name)
                if (cmd.name.lower().replace("create", "") in evt.name.lower() or
                    cmd.name.lower().replace("process", "") in evt.name.lower() or
                    cmd.name.lower().replace("update", "") in evt.name.lower()):
                    session.execute_write(
                        self._create_relationship,
                        cmd_id, evt_id, "EMITS"
                    )
        
        # Policy -> Event (LISTENS)
        for pol in extraction.policies:
            pol_id = pol_ids.get(pol.name)
            for evt in extraction.events:
                evt_id = evt_ids.get(evt.name)
                if evt.name.lower() in pol.condition.lower():
                    session.execute_write(
                        self._create_relationship,
                        pol_id, evt_id, "LISTENS"
                    )
        
        # Policy -> Command (ISSUES)
        for pol in extraction.policies:
            pol_id = pol_ids.get(pol.name)
            for cmd in extraction.commands:
                cmd_id = cmd_ids.get(cmd.name)
                if cmd.name.lower() in pol.condition.lower():
                    session.execute_write(
                        self._create_relationship,
                        pol_id, cmd_id, "ISSUES"
                    )
    
    @staticmethod
    def _create_relationship(tx, from_id: str, to_id: str, rel_type: str):
        query = f"""
        MATCH (a {{id: $from_id}})
        MATCH (b {{id: $to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        """
        tx.run(query, from_id=from_id, to_id=to_id)
    
    def get_graph(self, doc_id: str) -> GraphData:
        """Retrieve graph data for a document"""
        with neo4j_client.driver.session() as session:
            nodes = session.execute_read(self._get_nodes, doc_id)
            edges = session.execute_read(self._get_edges, doc_id)
            doc_frags = session.execute_read(self._get_doc_frags, doc_id)
        
        return GraphData(nodes=nodes, edges=edges, doc_frags=doc_frags)
    
    @staticmethod
    def _get_nodes(tx, doc_id: str) -> List[GraphNode]:
        query = """
        MATCH (n)
        WHERE n.doc_id = $doc_id AND (n:Aggregate OR n:Command OR n:Event OR n:Policy)
        RETURN n, labels(n) as labels
        """
        result = tx.run(query, doc_id=doc_id)
        nodes = []
        for record in result:
            node = record["n"]
            label = [l for l in record["labels"] if l in ["Aggregate", "Command", "Event", "Policy"]][0]
            nodes.append(GraphNode(
                id=node["id"],
                type=label,
                label=node.get("name", ""),
                props=dict(node)
            ))
        return nodes
    
    @staticmethod
    def _get_edges(tx, doc_id: str) -> List[GraphEdge]:
        query = """
        MATCH (a)-[r]->(b)
        WHERE a.doc_id = $doc_id AND b.doc_id = $doc_id
        AND type(r) IN ['TARGETS', 'EMITS', 'LISTENS', 'ISSUES', 'AFFECTS']
        RETURN a.id as from_id, b.id as to_id, type(r) as rel_type, id(r) as rel_id
        """
        result = tx.run(query, doc_id=doc_id)
        edges = []
        for record in result:
            edges.append(GraphEdge(
                id=f"edge-{record['rel_id']}",
                type=record["rel_type"],
                **{"from": record["from_id"], "to": record["to_id"]},
                props={}
            ))
        return edges
    
    @staticmethod
    def _get_doc_frags(tx, doc_id: str) -> List[DocFragNode]:
        query = """
        MATCH (d:DocFrag)
        WHERE d.doc_id = $doc_id
        RETURN d
        LIMIT 10
        """
        result = tx.run(query, doc_id=doc_id)
        frags = []
        for record in result:
            node = record["d"]
            frags.append(DocFragNode(
                id=node["id"],
                doc_id=node["doc_id"],
                page=node["page"],
                span=node["span"],
                text=node["text"]
            ))
        return frags
    
    def recommend_ms_candidates(self, doc_id: str) -> List[MSCandidate]:
        """Recommend microservice candidates based on graph structure"""
        with neo4j_client.driver.session() as session:
            result = session.execute_read(self._find_aggregate_clusters, doc_id)
        
        # Simple clustering based on connection density
        candidates = []
        for record in result[:5]:  # Top 5 clusters
            candidates.append(MSCandidate(
                aggregates=record["aggregates"],
                rationale=f"Strongly connected through {record['connections']} relationships",
                confidence=min(0.9, record["connections"] / 10.0)
            ))
        
        return candidates
    
    @staticmethod
    def _find_aggregate_clusters(tx, doc_id: str):
        query = """
        MATCH path = (a:Aggregate)-[:TARGETS|EMITS|AFFECTS*1..2]-(b:Aggregate)
        WHERE a.doc_id = $doc_id AND b.doc_id = $doc_id AND a <> b
        WITH a, b, length(path) as distance
        WITH a, collect(distinct b.name) as connected_aggs, count(*) as connections
        WHERE size(connected_aggs) >= 1
        RETURN a.name as agg_name, connected_aggs as aggregates, connections
        ORDER BY connections DESC
        """
        result = tx.run(query, doc_id=doc_id)
        clusters = []
        for record in result:
            clusters.append({
                "aggregates": [record["agg_name"]] + record["aggregates"],
                "connections": record["connections"]
            })
        return clusters


graph_service = GraphService()



