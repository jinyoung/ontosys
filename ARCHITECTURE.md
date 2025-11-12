# 아키텍처 문서

## 시스템 개요

Event-Storming → Neo4j → VueFlow는 자연어 문서에서 DDD/이벤트스토밍 개념을 자동 추출하고 그래프로 시각화하는 시스템입니다.

## 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Upload Panel │  │ Graph Canvas │  │   VueFlow    │      │
│  │              │  │              │  │  (Nodes/     │      │
│  │              │  │              │  │   Edges)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│           │                 │                                │
│           └─────────────────┴───── Pinia Store              │
└─────────────────────────────┬───────────────────────────────┘
                              │ REST API
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Document   │  │  Extraction  │  │    Graph     │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  │  (Text       │  │  (LangChain) │  │  (Neo4j)     │      │
│  │   Extract)   │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│           │                 │                 │              │
│           └─────────────────┴─────────────────┘              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────┴───────┐   ┌───────┴───────┐
            │    Neo4j      │   │     Redis     │
            │   (Graph DB)  │   │   (Cache/     │
            │               │   │    Queue)     │
            └───────────────┘   └───────────────┘
```

## 데이터 흐름

### 1. 문서 업로드 및 추출

```
User → Upload File
  → Frontend: api.uploadDocument()
    → Backend: POST /api/docs/upload
      → DocumentService.save_upload()
      → DocumentService.extract_text()
        → [PDF/DOCX/TXT Parser]
      → Create DocFrag nodes
      → Store in Neo4j
    ← Return {doc_id, pages, fragments}
  ← Update UI
```

### 2. 엔티티 추출

```
User → Start Extraction
  → Frontend: api.startExtraction()
    → Backend: POST /api/extract/run
      → Create job_id
      → Background Task:
        → Load DocFrags from Neo4j
        → ExtractionService.extract_from_fragments()
          → For each fragment:
            → LangChain Pipeline:
              → Prompt with system instructions
              → LLM processing (GPT-4)
              → Parse JSON output
            → Aggregate/Command/Event/Policy objects
          → Merge duplicates
        → GraphService.store_extraction()
          → Create entity nodes
          → Create relationships (heuristic)
          → Store in Neo4j
    ← Poll job status
  ← Load graph when done
```

### 3. 그래프 시각화

```
Backend → GET /api/graph?doc_id=xxx
  → GraphService.get_graph()
    → Query Neo4j:
      → MATCH all nodes with doc_id
      → MATCH all edges between nodes
      → RETURN nodes, edges, doc_frags
  ← Convert to API format
    
Frontend ← Receive graph data
  → Transform to VueFlow format:
    → nodes: {id, type, position, data}
    → edges: {id, source, target, type}
  → Render on canvas
```

### 4. 편집 및 저장

```
User → Edit nodes/edges on canvas
  → VueFlow: drag, edit labels, etc.
  → Store: mark isDirty = true

User → Click Save
  → Frontend: api.saveNodes() + api.saveEdges()
    → Backend: POST /api/graph/nodes + /api/graph/edges
      → GraphService: Update Neo4j
        → MERGE nodes with new properties
        → MERGE edges
    ← Success
  ← Store: isDirty = false
```

## 핵심 컴포넌트

### Backend

#### 1. DocumentService
- **역할**: 파일 업로드, 텍스트 추출, 청킹
- **기술**: pypdf, python-docx
- **출력**: DocFragNode 리스트

#### 2. ExtractionService
- **역할**: LLM 기반 엔티티 추출
- **기술**: LangChain, OpenAI GPT-4
- **프롬프트**: DDD/이벤트스토밍 전문 프롬프트
- **출력**: ExtractionOutput (aggregates, commands, events, policies)

#### 3. GraphService
- **역할**: Neo4j CRUD, 관계 생성, 추천
- **스키마**:
  ```cypher
  (:Aggregate {id, name, description, confidence})
  (:Command {id, name, intent, preconditions})
  (:Event {id, name, schema_hint})
  (:Policy {id, name, type, condition})
  (:DocFrag {id, doc_id, page, span, text})
  
  (:Command)-[:TARGETS]->(:Aggregate)
  (:Command)-[:EMITS]->(:Event)
  (:Policy)-[:LISTENS]->(:Event)
  (:Policy)-[:ISSUES]->(:Command)
  ```

### Frontend

#### 1. GraphStore (Pinia)
- **상태**: nodes, edges, docFrags, isLoading, isDirty
- **액션**: uploadDocument, startExtraction, loadGraph, saveGraph

#### 2. 커스텀 노드 타입
- **AggregateNode**: 카드 형태, 그라데이션 배경
- **CommandNode**: Pill 형태, 액션 강조
- **EventNode**: 다이아몬드(45도 회전), 이벤트 표현
- **PolicyNode**: 육각형(clip-path), 정책 표현

#### 3. GraphCanvas
- **VueFlow**: 드래그 앤 드롭 캔버스
- **Controls**: 줌, 팬, 피트
- **MiniMap**: 전체 그래프 미니맵

## 데이터베이스 스키마 (Neo4j)

### 노드 라벨

| Label | Properties | Description |
|-------|-----------|-------------|
| Aggregate | id, doc_id, name, description, confidence, tags | 비즈니스 엔티티 |
| Command | id, doc_id, name, intent, preconditions, confidence | 명령/액션 |
| Event | id, doc_id, name, schema_hint, confidence | 도메인 이벤트 |
| Policy | id, doc_id, name, type, condition, confidence | 비즈니스 규칙 |
| DocFrag | id, doc_id, page, span, text | 문서 조각 |

### 관계 타입

| Type | From → To | Description |
|------|-----------|-------------|
| TARGETS | Command → Aggregate | 커맨드가 어그리게이트에 작용 |
| EMITS | Command → Event | 커맨드가 이벤트 발생 |
| LISTENS | Policy → Event | 폴리시가 이벤트를 감지 |
| ISSUES | Policy → Command | 폴리시가 커맨드 발행 |
| AFFECTS | Event → Aggregate | 이벤트가 어그리게이트 상태 변경 |
| DERIVED_FROM | Any → DocFrag | 원문 추적성 |

## API 엔드포인트

### 문서 관리
- `POST /api/docs/upload` - 문서 업로드
  - Input: multipart/form-data (file)
  - Output: {doc_id, filename, pages, fragments}

### 추출
- `POST /api/extract/run` - 추출 작업 시작
  - Input: {doc_id}
  - Output: {job_id, doc_id, status}
- `GET /api/extract/status?job_id=xxx` - 작업 상태 조회
  - Output: {job_id, status, progress, message}

### 그래프
- `GET /api/graph?doc_id=xxx` - 그래프 데이터 조회
  - Output: {nodes, edges, doc_frags}
- `POST /api/graph/nodes` - 노드 생성/수정
  - Input: {nodes: [...]}
- `POST /api/graph/edges` - 엣지 생성/수정
  - Input: {edges: [...]}
- `DELETE /api/graph/nodes/:id` - 노드 삭제
- `DELETE /api/graph/edges/:id` - 엣지 삭제
- `GET /api/graph/recommend/ms-candidates?doc_id=xxx` - MS 후보 추천
  - Output: {clusters: [{aggregates, rationale, confidence}]}

## 확장 가능성

### 단기 개선
1. **실시간 협업**: WebSocket 기반 멀티유저 편집
2. **버전 관리**: 그래프 스냅샷 및 비교
3. **고급 레이아웃**: 자동 레이아웃 알고리즘 (Dagre, ELK)
4. **근거 뷰어**: 문서 원문 하이라이트 패널

### 장기 개선
1. **코드 생성**: 그래프 → Spring Boot/NestJS 스켈레톤
2. **DMN 통합**: Policy → DMN 규칙 자동 변환
3. **시뮬레이션**: 이벤트 흐름 시뮬레이션
4. **멀티 모달**: 이미지, 다이어그램 인식

## 성능 고려사항

- **청킹**: 문서를 800-1200자 단위로 분할하여 LLM 처리
- **배치 처리**: 여러 fragment를 병렬로 처리 (asyncio)
- **캐싱**: Redis를 통한 추출 결과 캐싱
- **인덱스**: Neo4j에 id, doc_id 기반 인덱스
- **페이지네이션**: 대규모 그래프의 경우 뷰포트 기반 로딩

## 보안

- **CORS**: 프론트엔드 origin만 허용
- **파일 검증**: 파일 타입, 크기 제한
- **환경변수**: API 키는 .env로 관리
- **입력 검증**: Pydantic 스키마 검증



