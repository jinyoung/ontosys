# 서버 시작 가이드

## 현재 상태
✅ 백엔드와 프론트엔드 서버가 실행 중입니다!

## 접속 정보

### 프론트엔드
- URL: http://localhost:5173
- 브라우저에서 접속하여 UI를 확인할 수 있습니다

### 백엔드
- URL: http://localhost:8000
- API 문서: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## ⚠️ 중요: Docker 시작 필요

백엔드가 Neo4j에 연결하려면 Docker를 시작해야 합니다:

### 1. Docker Desktop 실행
- macOS: Applications에서 Docker Desktop 실행
- 상단 메뉴 바에 Docker 아이콘이 나타날 때까지 대기

### 2. Neo4j & Redis 컨테이너 시작
```bash
cd /Users/uengine/Documents/ontosys
docker-compose up -d
```

### 3. 상태 확인
```bash
docker ps
```

다음이 표시되어야 합니다:
- ontosys-neo4j
- ontosys-redis

### 4. Neo4j 브라우저 접속
- URL: http://localhost:7474
- Username: neo4j
- Password: ontosys123

## 서버 중지

### 현재 실행 중인 서버 중지
```bash
# 프로세스 ID 확인
ps aux | grep -E "(uvicorn|vite)" | grep -v grep

# 종료 (Ctrl+C 또는 kill 명령어)
kill 59572  # uvicorn
kill 60192  # vite
```

### Docker 중지
```bash
docker-compose down
```

## 재시작

전체 시스템 재시작:
```bash
cd /Users/uengine/Documents/ontosys

# 1. Docker 시작
docker-compose up -d

# 2. 백엔드 시작 (새 터미널)
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 프론트엔드 시작 (또 다른 터미널)
cd frontend
npm run dev
```

## 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# 8000 포트 사용 프로세스 확인
lsof -i :8000

# 5173 포트 사용 프로세스 확인
lsof -i :5173

# 프로세스 종료
kill -9 <PID>
```

### Neo4j 연결 오류
1. Docker Desktop이 실행 중인지 확인
2. `docker ps`로 컨테이너 상태 확인
3. `docker logs ontosys-neo4j`로 로그 확인



