from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum
from uuid import UUID


class SourceAnchor(BaseModel):
    """Reference to source document fragment"""
    doc_id: str
    page: int
    span: List[int]  # [start, end] character positions


class SourceRef(BaseModel):
    """Weighted reference to document fragment"""
    doc_frag_id: str
    weight: float = 1.0


class CommandIntent(str, Enum):
    CREATE = "Create"
    UPDATE = "Update"
    DELETE = "Delete"
    QUERY = "Query"
    CUSTOM = "Custom"


class PolicyType(str, Enum):
    PROCESS_POLICY = "ProcessPolicy"
    SAGA_POLICY = "SagaPolicy"
    RULE = "Rule"


class AggregateCreate(BaseModel):
    """Aggregate creation schema"""
    name: str
    description: str = ""
    source_anchor: SourceAnchor
    confidence: float = Field(ge=0.0, le=1.0)


class CommandCreate(BaseModel):
    """Command creation schema"""
    name: str
    intent: CommandIntent = CommandIntent.CUSTOM
    preconditions: List[str] = []
    source_anchor: SourceAnchor
    confidence: float = Field(ge=0.0, le=1.0)


class EventCreate(BaseModel):
    """Event creation schema"""
    name: str
    schema_hint: Dict[str, Any] = {}
    source_anchor: SourceAnchor
    confidence: float = Field(ge=0.0, le=1.0)


class PolicyCreate(BaseModel):
    """Policy creation schema"""
    name: str
    type: PolicyType = PolicyType.PROCESS_POLICY
    condition: str = ""
    source_anchor: SourceAnchor
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractionOutput(BaseModel):
    """Output from LangChain extraction pipeline"""
    aggregates: List[AggregateCreate] = []
    commands: List[CommandCreate] = []
    events: List[EventCreate] = []
    policies: List[PolicyCreate] = []


class DocFragNode(BaseModel):
    """Document fragment node"""
    id: str
    doc_id: str
    page: int
    span: List[int]
    text: str


class GraphNode(BaseModel):
    """Generic graph node"""
    id: str
    type: Literal["Aggregate", "Command", "Event", "Policy"]
    label: str
    props: Dict[str, Any] = {}


class GraphEdge(BaseModel):
    """Generic graph edge"""
    id: str
    type: Literal["TARGETS", "EMITS", "LISTENS", "ISSUES", "AFFECTS", "DERIVED_FROM"]
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    props: Dict[str, Any] = {}
    
    model_config = {"populate_by_name": True}


class GraphData(BaseModel):
    """Complete graph data structure"""
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []
    doc_frags: List[DocFragNode] = []


class UploadResponse(BaseModel):
    """Response after document upload"""
    doc_id: str
    filename: str
    pages: int
    fragments: int


class ExtractionJobResponse(BaseModel):
    """Response after starting extraction job"""
    job_id: str
    doc_id: str
    status: Literal["queued", "running", "done", "error"]


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: Literal["queued", "running", "done", "error"]
    progress: int = 0  # 0-100
    message: str = ""


class NodeCreateRequest(BaseModel):
    """Request to create/update graph nodes"""
    nodes: List[GraphNode]


class EdgeCreateRequest(BaseModel):
    """Request to create/update graph edges"""
    edges: List[GraphEdge]


class MSCandidate(BaseModel):
    """Microservice candidate cluster"""
    aggregates: List[str]
    rationale: str
    confidence: float


class MSRecommendationResponse(BaseModel):
    """Microservice candidate recommendation"""
    clusters: List[MSCandidate] = []



