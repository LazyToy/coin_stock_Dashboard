# 🚀 Crypto Dashboard

Next.js + Mantine UI를 활용한 세련된 암호화폐 포트폴리오 대시보드

![Dashboard Preview](https://via.placeholder.com/800x400?text=Crypto+Dashboard)

## ✨ 특징

- **실시간 데이터 조회**: 업비트 & 바이낸스 통합
- **세련된 UI**: 다크 테마, Glassmorphism, 부드러운 애니메이션
- **새로고침 기능**: 수동 및 자동 새로고침 지원
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원

## 📁 프로젝트 구조

```
coin/
├── backend/               # FastAPI 백엔드
│   ├── api_server.py     # API 서버
│   └── requirements.txt  # Python 의존성
├── frontend/             # Next.js 프론트엔드
│   ├── app/              # App Router 페이지
│   ├── components/       # React 컴포넌트
│   ├── types/            # TypeScript 타입
│   └── utils/            # 유틸리티 함수
├── binance_api.py        # 바이낸스 API 모듈
├── upbit_api.py          # 업비트 API 모듈
├── config.py             # 설정 모듈
└── .env                  # 환경 변수 (API 키)
```

## 🛠️ 설치 및 실행

### 1. 환경 변수 설정

`.env` 파일에 API 키 설정:

```env
UPBIT_ACCESS_KEY=your_upbit_access_key
UPBIT_SECRET_KEY=your_upbit_secret_key
BINANCE_ACCESS_KEY=your_binance_access_key
BINANCE_SECRET_KEY=your_binance_secret_key
```

### 2. 백엔드 실행

```bash
# Python 가상환경 활성화
.\.venv\Scripts\activate

# 의존성 설치
pip install -r backend/requirements.txt

# 백엔드 서버 실행
cd backend
python api_server.py
```

백엔드는 http://localhost:8000 에서 실행됩니다.

### 3. 프론트엔드 실행

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 설치 (최초 1회)
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드는 http://localhost:3000 에서 실행됩니다.

## 🎨 기능 설명

### 잔액 카드
- 업비트/바이낸스 총 잔액 표시
- 사용 가능/거래 중 금액 구분
- 시각적 진행률 표시

### 보유 코인 테이블
- 보유 수량, 현재가, 평가금액
- 업비트: 평균 매수가 및 수익률 표시
- 녹색/빨간색 수익률 색상 구분

### 거래량 TOP 10
- 24시간 거래량 상위 코인
- 실시간 가격 및 변동률
- 거래대금 표시

### 새로고침 버튼
- 수동 새로고침 (5초 쿨다운)
- 자동 새로고침 (30초/1분/5분)
- 마지막 업데이트 시간 표시

## 📚 기술 스택

### 백엔드
- Python 3.10+
- FastAPI
- pyupbit
- python-binance

### 프론트엔드
- Next.js 16 (App Router)
- Mantine UI v8
- TypeScript
- Tabler Icons

## 📝 API 엔드포인트

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /api/dashboard` | 전체 대시보드 데이터 |
| `GET /api/upbit/balance` | 업비트 잔액 |
| `GET /api/upbit/holdings` | 업비트 보유 코인 |
| `GET /api/upbit/top-volume` | 업비트 거래량 상위 |
| `GET /api/binance/balance` | 바이낸스 잔액 |
| `GET /api/binance/holdings` | 바이낸스 보유 코인 |
| `GET /api/binance/top-volume` | 바이낸스 거래량 상위 |

## 🔒 보안 참고사항

- API 키는 절대 Git에 커밋하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있습니다
- 프로덕션 환경에서는 환경 변수로 관리하세요

## 📄 라이선스

MIT License
