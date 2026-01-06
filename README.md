# 🚀 All-in-One Investment Dashboard (Crypto + Stock)

Next.js + Mantine UI + FastAPI를 활용한 **암호화폐 & 주식 통합 포트폴리오 대시보드**입니다.

![Dashboard Preview](https://via.placeholder.com/800x400?text=Investment+Dashboard)

## ✨ 특징

### 💰 암호화폐 (Crypto)
- **통합 자산 관리**: 업비트(Upbit) & 바이낸스(Binance) 잔액 및 보유 자산 실시간 조회
- **실시간 랭킹**: 
    - 업비트 원화 마켓 거래량 상위
    - 바이낸스 USDT 마켓 거래량 상위 (KRW 환산 포함)
- **시장 지표**: 공포/탐욕 지수(Fear & Greed Index), 고래 송금 알림(Whale Alert)

### 📈 주식 (Stock)
- **국내 주식 (KOSPI & KOSDAQ)**:
    - **실시간 Crawling**: 네이버 금융(Naver Finance)을 크롤링하여 **실시간 거래대금 상위** 종목 제공
    - **섹터/업종 분석**: 실시간 가장 강세인 업종 Top 10 제공
- **미국 주식 (US Stocks)**:
    - **실시간 Scanning**: 주요 미국 주식/ETF 50+ 종목(Mag 7, 테크, 반도체, 주요 ETF) 실시간 스캔
    - **Volume Ranking**: Yahoo Finance 실시간 데이터를 기반으로 거래량 상위 종목 자동 정렬
    - Yahoo API 차단 시에도 작동하는 견고한 Fallback 로직 구현
- **뉴스 검색**: 관련 키워드 주식 뉴스 검색 기능

### 🎨 UI/UX
- **모던 디자인**: 다크 모드 기반의 프리미엄 디자인, Glassmorphism, 인터랙티브 애니메이션
- **반응형**: 모바일, 태블릿, 데스크톱 완벽 지원

---

## 📁 프로젝트 구조

```
coin/
├── backend/                  # FastAPI 백엔드
│   ├── services/             # 비즈니스 로직 모듈
│   │   ├── stock_api.py      # 주식 데이터 (크롤링/스캐닝)
│   │   ├── upbit_api.py      # 업비트 API
│   │   ├── binance_api.py    # 바이낸스 API
│   │   └── config.py         # 설정
│   ├── api_server.py         # 메인 API 서버 (Asyncio Gather 적용)
│   └── requirements.txt      # Python 의존성
├── frontend/                 # Next.js 프론트엔드
│   ├── app/                  # App Router 페이지
│   ├── components/           # UI 컴포넌트
│   │   ├── StockDashboard.tsx # 주식 대시보드 컴포넌트
│   │   ├── CryptoDashboard.tsx# 코인 대시보드 컴포넌트
│   │   └── ...
│   └── ...
└── .env                      # 환경 변수 (API 키)
```

## 🛠️ 설치 및 실행

### 1. 환경 변수 설정
`.env` 파일을 생성하고 API 키를 설정하세요:

```env
UPBIT_ACCESS_KEY=your_upbit_access_key
UPBIT_SECRET_KEY=your_upbit_secret_key
BINANCE_ACCESS_KEY=your_binance_access_key
BINANCE_SECRET_KEY=your_binance_secret_key
```

### 2. 백엔드 (Python/FastAPI)

```bash
# 가상환경 활성화 (Windows)
.\.venv\Scripts\activate

# 의존성 설치
pip install -r backend/requirements.txt
# (beautifulsoup4, yfinance, fastapi, uvicorn 등 포함)

# 서버 실행
cd backend
python api_server.py
```
> 백엔드 주소: `http://localhost:8000`

### 3. 프론트엔드 (Next.js)

```bash
cd frontend
npm install
npm run dev
```
> 프론트엔드 주소: `http://localhost:3000`

---

## 📚 기술 스택

### Backend
- **Framework**: FastAPI (Async)
- **Crawling**: BeautifulSoup4 (네이버 금융 크롤링)
- **Data Fetch**: yfinance (미국 주식, 환율), pyupbit, python-binance
- **Concurrency**: asyncio (병렬 데이터 처리)

### Frontend
- **Framework**: Next.js 16 (App Router)
- **UI Library**: Mantine UI v8
- **Language**: TypeScript

---

## 📝 API 엔드포인트

| 구분 | 메서드 | 엔드포인트 | 설명 |
|---|---|---|---|
| **Crypto** | GET | `/api/dashboard` | 암호화폐 전체 대시보드 (통합 데이터) |
| **Stock** | GET | `/api/stock/dashboard` | 주식 전체 대시보드 (국내/미국/섹터) |
| **News** | GET | `/api/stock/news/{query}` | 주식 뉴스 검색 |

---

## 💡 주요 구현 로직

1. **하드코딩 제거**:
    - 기존의 고정된 종목 리스트 대신, **실시간 크롤링(Naver)** 및 **광범위 스캐닝(Yahoo)** 방식을 도입하여 시장 상황에 맞는 살아있는 데이터를 제공합니다.
2. **병렬 처리**:
    - `asyncio.gather`를 사용하여 국내 주식, 미국 주식, 업비트, 바이낸스 데이터를 동시에 병렬로 조회, 응답 속도를 최대화했습니다.
3. **Fallback 전략**:
    - 외부 API(Yahoo Finance 등) 장애 시에도 서비스가 중단되지 않도록 예외 처리 및 대체 로직을 적용했습니다.

---

## 📄 라이선스
MIT License
