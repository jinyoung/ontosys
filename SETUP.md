# 설정 및 실행 가이드

## 필수 요구사항

1. **Docker Desktop** (Neo4j, Redis 실행용)
2. **Python 3.11+**
3. **Node.js 18+** (npm 포함)
4. **uv** (Python 패키지 매니저)

## 빠른 시작

### 1. 자동 시작 (권장)

```bash
./start.sh
```

이 스크립트는 자동으로:
- Docker 컨테이너 시작 (Neo4j, Redis)
- 백엔드 환경 설정 및 시작
- 프론트엔드 의존성 설치 및 시작

### 2. 수동 시작

#### 2.1 Docker 컨테이너 시작

```bash
docker-compose up -d
```

#### 2.2 백엔드 설정 및 시작

```bash
cd backend

# uv 설치 (아직 없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 가상환경 생성 및 패키지 설치
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync

# 환경변수 설정 (선택사항)
# .env 파일을 생성하고 필요한 값을 설정하세요
# cp .env.example .env

# 서버 시작
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2.3 프론트엔드 설정 및 시작

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 시작
npm run dev
```

## 접속 주소

- **프론트엔드**: http://localhost:5173
- **백엔드 API**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **Neo4j 브라우저**: http://localhost:7474
  - Username: `neo4j`
  - Password: `ontosys123`

## OpenAI API 키 설정 (선택사항)

실제 LLM 추출 기능을 사용하려면:

1. `backend/.env` 파일 생성
2. OpenAI API 키 추가:

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4
```

API 키가 없으면 모의 데이터로 동작합니다.

## 사용 방법

1. **문서 업로드**: 좌측 패널에서 PDF/DOCX/TXT 파일 업로드
2. **추출 시작**: "Start Extraction" 버튼 클릭
3. **그래프 확인**: 자동으로 추출된 도메인 개념이 그래프로 표시됨
4. **편집**: 노드를 드래그하여 위치 조정
5. **저장**: 변경사항이 있으면 "Save" 버튼으로 저장

## 문제 해결

### Neo4j 연결 실패

```bash
# Neo4j 컨테이너 상태 확인
docker ps | grep neo4j

# 로그 확인
docker logs ontosys-neo4j

# 재시작
docker-compose restart neo4j
```

### 포트 충돌

다른 서비스가 포트를 사용 중이면:
- 백엔드 포트 변경: `backend/.env`의 `APP_PORT`
- 프론트엔드 포트 변경: `frontend/vite.config.js`의 `server.port`
- Neo4j 포트 변경: `docker-compose.yml`

### Node 버전 문제

Node 18 미만 버전에서는 Vite 5가 동작하지 않을 수 있습니다.
- Node 18+ 설치 또는
- nvm 사용: `nvm install 18 && nvm use 18`

## 서비스 중지

```bash
# Docker 컨테이너 중지
docker-compose down

# 백엔드/프론트엔드 프로세스 종료 (Ctrl+C)
```

## 개발

### 백엔드 테스트

```bash
cd backend
source .venv/bin/activate
pytest
```

### 프론트엔드 빌드

```bash
cd frontend
npm run build
```

빌드된 파일은 `frontend/dist/`에 생성됩니다.

## 다음 단계

- 실제 RFP 문서로 테스트
- OpenAI API 키 설정하여 실제 추출 테스트
- Neo4j 브라우저에서 그래프 구조 확인
- 노드/엣지 편집 및 저장 테스트



