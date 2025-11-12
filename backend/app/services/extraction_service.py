import uuid
import logging
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.config import settings
from app.models.schemas import (
    ExtractionOutput, DocFragNode,
    AggregateCreate, CommandCreate, EventCreate, PolicyCreate
)

logger = logging.getLogger(__name__)


EXTRACTION_SYSTEM_PROMPT = """You are a DDD (Domain-Driven Design) and Event Storming expert analyst.
Your task is to identify and extract the following domain concepts from text:

1. **Aggregates**: Core business entities/objects (nouns, singular form)
2. **Commands**: Actions that trigger changes (verb phrases, imperative form like "CreateOrder")
3. **Events**: Things that happened (past tense like "OrderCreated")
4. **Policies**: Business rules or reactive processes (when X then Y)

Naming Conventions:
- Events: Past tense (e.g., "OrderCreated", "PaymentCompleted")
- Commands: Verb form (e.g., "CreateOrder", "ProcessPayment")
- Aggregates: Noun, singular (e.g., "Order", "Payment", "Customer")
- Policies: Descriptive (e.g., "NotifyCustomerWhenOrderShipped")

For each identified concept:
- Provide a clear name following conventions
- Add a brief description
- Include source location (approximate character span)
- Assign confidence score (0.0-1.0)

Be precise and conservative. Only extract concepts that are clearly present in the text.
"""


EXTRACTION_USER_TEMPLATE = """Analyze the following document fragment and extract domain concepts:

Document ID: {doc_id}
Page/Section: {page}
Text:
---
{text}
---

Extract all Aggregates, Commands, Events, and Policies you can identify.
{format_instructions}
"""


class ExtractionService:
    """Service for extracting domain concepts using LangChain"""
    
    def __init__(self):
        self.llm = None
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=0.3,
                openai_api_key=settings.openai_api_key
            )
    
    async def extract_from_fragments(
        self, 
        fragments: List[DocFragNode]
    ) -> ExtractionOutput:
        """Extract domain concepts from document fragments"""
        
        if not self.llm:
            logger.warning("LLM not configured, returning mock data")
            return self._mock_extraction(fragments)
        
        all_aggregates = []
        all_commands = []
        all_events = []
        all_policies = []
        
        parser = PydanticOutputParser(pydantic_object=ExtractionOutput)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", EXTRACTION_SYSTEM_PROMPT),
            ("user", EXTRACTION_USER_TEMPLATE)
        ])
        
        # Process each fragment
        for frag in fragments[:10]:  # Limit to first 10 fragments for MVP
            try:
                chain = prompt | self.llm | parser
                
                result = await chain.ainvoke({
                    "doc_id": frag.doc_id,
                    "page": frag.page,
                    "text": frag.text,
                    "format_instructions": parser.get_format_instructions()
                })
                
                all_aggregates.extend(result.aggregates)
                all_commands.extend(result.commands)
                all_events.extend(result.events)
                all_policies.extend(result.policies)
                
                logger.info(f"Extracted from fragment {frag.id}: "
                          f"{len(result.aggregates)} aggs, "
                          f"{len(result.commands)} cmds, "
                          f"{len(result.events)} events, "
                          f"{len(result.policies)} policies")
            
            except Exception as e:
                logger.error(f"Extraction failed for fragment {frag.id}: {e}")
                continue
        
        # Merge duplicates
        merged_output = self._merge_duplicates(ExtractionOutput(
            aggregates=all_aggregates,
            commands=all_commands,
            events=all_events,
            policies=all_policies
        ))
        
        return merged_output
    
    def _merge_duplicates(self, output: ExtractionOutput) -> ExtractionOutput:
        """Merge duplicate entities based on name similarity"""
        # Simple name-based deduplication for MVP
        # In production, use fuzzy matching and embedding similarity
        
        def dedupe_by_name(items: List[Any]) -> List[Any]:
            seen = {}
            for item in items:
                name_lower = item.name.lower().strip()
                if name_lower not in seen:
                    seen[name_lower] = item
                else:
                    # Keep the one with higher confidence
                    if item.confidence > seen[name_lower].confidence:
                        seen[name_lower] = item
            return list(seen.values())
        
        return ExtractionOutput(
            aggregates=dedupe_by_name(output.aggregates),
            commands=dedupe_by_name(output.commands),
            events=dedupe_by_name(output.events),
            policies=dedupe_by_name(output.policies)
        )
    
    def _mock_extraction(self, fragments: List[DocFragNode]) -> ExtractionOutput:
        """Generate mock extraction data for development/testing"""
        logger.info("Generating mock extraction data")
        
        doc_id = fragments[0].doc_id if fragments else "doc-mock"
        
        return ExtractionOutput(
            aggregates=[
                AggregateCreate(
                    name="Order",
                    description="Customer order aggregate",
                    source_anchor={"doc_id": doc_id, "page": 1, "span": [0, 100]},
                    confidence=0.85
                ),
                AggregateCreate(
                    name="Customer",
                    description="Customer entity",
                    source_anchor={"doc_id": doc_id, "page": 1, "span": [100, 200]},
                    confidence=0.80
                ),
                AggregateCreate(
                    name="Payment",
                    description="Payment processing aggregate",
                    source_anchor={"doc_id": doc_id, "page": 2, "span": [0, 150]},
                    confidence=0.75
                ),
            ],
            commands=[
                CommandCreate(
                    name="CreateOrder",
                    intent="Create",
                    preconditions=["Customer must exist"],
                    source_anchor={"doc_id": doc_id, "page": 1, "span": [200, 300]},
                    confidence=0.80
                ),
                CommandCreate(
                    name="ProcessPayment",
                    intent="Update",
                    preconditions=["Order must be confirmed"],
                    source_anchor={"doc_id": doc_id, "page": 2, "span": [150, 250]},
                    confidence=0.75
                ),
                CommandCreate(
                    name="ShipOrder",
                    intent="Update",
                    preconditions=["Payment completed"],
                    source_anchor={"doc_id": doc_id, "page": 3, "span": [0, 100]},
                    confidence=0.78
                ),
            ],
            events=[
                EventCreate(
                    name="OrderCreated",
                    schema_hint={"orderId": "string", "customerId": "string"},
                    source_anchor={"doc_id": doc_id, "page": 1, "span": [300, 400]},
                    confidence=0.82
                ),
                EventCreate(
                    name="PaymentProcessed",
                    schema_hint={"paymentId": "string", "amount": "number"},
                    source_anchor={"doc_id": doc_id, "page": 2, "span": [250, 350]},
                    confidence=0.80
                ),
                EventCreate(
                    name="OrderShipped",
                    schema_hint={"orderId": "string", "trackingNumber": "string"},
                    source_anchor={"doc_id": doc_id, "page": 3, "span": [100, 200]},
                    confidence=0.85
                ),
            ],
            policies=[
                PolicyCreate(
                    name="NotifyCustomerOnOrderCreation",
                    type="ProcessPolicy",
                    condition="When OrderCreated then send notification",
                    source_anchor={"doc_id": doc_id, "page": 1, "span": [400, 500]},
                    confidence=0.70
                ),
                PolicyCreate(
                    name="ShipOrderWhenPaymentCompleted",
                    type="SagaPolicy",
                    condition="When PaymentProcessed then ShipOrder",
                    source_anchor={"doc_id": doc_id, "page": 2, "span": [350, 450]},
                    confidence=0.75
                ),
            ]
        )


extraction_service = ExtractionService()



