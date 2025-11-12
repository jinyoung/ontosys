# Event-Storming → GraphDB(Neo4j) → VueFlow Prototype

자연어 문서에서 DDD/이벤트스토밍 개념을 자동 추출하고 그래프로 시각화하는 프로토타입입니다.

## 기술 스택

- **Backend**: Python 3.11+, FastAPI, LangChain, Neo4j
- **Frontend**: Vue 3, VueFlow, Pinia
- **Database**: Neo4j 5.x
- **Cache/Queue**: Redis

## 시작하기

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env
# .env 파일을 편집하여 OPENAI_API_KEY 등을 설정하세요
```

### 2. Docker 컨테이너 시작

```bash
docker-compose up -d
```

Neo4j 브라우저: http://localhost:7474

### 3. Backend 설정

```bash
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync
```

### 4. Backend 실행

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서: http://localhost:8000/docs

### 5. Frontend 설정 및 실행

```bash
cd frontend
npm install
npm run dev
```

앱: http://localhost:5173

## 주요 기능

1. **문서 업로드**: PDF/DOCX/TXT 문서 업로드
2. **자동 추출**: LangChain을 통한 Aggregate/Command/Event/Policy 추출
3. **그래프 시각화**: VueFlow 기반 인터랙티브 캔버스
4. **편집 및 저장**: 노드/엣지 편집 후 Neo4j 동기화
5. **근거 추적**: 원문 문장/페이지 하이라이트
6. **MS 후보 추천**: 그래프 기반 마이크로서비스 경계 추천

## 아키텍처

```
User → Vue3/VueFlow → FastAPI → Neo4j
                    ↓
                LangChain Pipeline
```

## 개발 로드맵

- [x] 프로젝트 구조 및 기본 설정
- [ ] Backend API 스켈레톤
- [ ] Neo4j 스키마 및 연결
- [ ] 문서 처리 파이프라인
- [ ] LangChain 추출 파이프라인
- [ ] Frontend VueFlow 캔버스
- [ ] 편집 및 저장 기능
- [ ] MS 후보 추천

## 라이선스

MIT



