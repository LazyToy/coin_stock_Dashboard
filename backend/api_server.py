"""
코인 대시보드 API 서버
FastAPI를 사용하여 업비트와 바이낸스 데이터를 제공합니다.
"""
import sys
import os

# 상위 디렉토리를 path에 추가하여 기존 모듈 import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import pyupbit

# 기존 API 모듈 import
from upbit_api import (
    get_upbit_balance,
    get_upbit_holdings,
    get_upbit_top_volume_coins
)
from binance_api import (
    get_binance_balance,
    get_binance_holdings,
    get_binance_top_volume_coins
)
from stock_api import (
    get_kospi_top_volume, get_kosdaq_top_volume, get_us_top_volume,
    get_major_indices, get_sector_performance, get_stock_news,
    get_crypto_fear_greed, get_whale_alerts, get_etf_top_volume
)


# === 환율 조회 함수 ===

def get_usdt_krw_rate() -> float:
    """
    업비트에서 USDT/KRW 환율을 조회합니다.
    조회 실패 시 기본값 1,450원을 반환합니다.
    """
    try:
        rate = pyupbit.get_current_price("KRW-USDT")
        if rate:
            return float(rate)
    except Exception as e:
        print(f"환율 조회 실패: {e}")
    return 1450.0  # 기본값

app = FastAPI(
    title="Coin Dashboard API",
    description="암호화폐 포트폴리오 대시보드 API",
    version="1.0.0"
)

# CORS 설정 - Next.js 프론트엔드 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Pydantic 모델 정의 ===

class UpbitBalance(BaseModel):
    total_krw: float
    available_krw: float
    locked_krw: float


class UpbitHolding(BaseModel):
    currency: str
    balance: float
    locked: float
    total: float
    avg_buy_price: float
    current_price: Optional[float]
    eval_amount: float
    profit_rate: float


class UpbitTopCoin(BaseModel):
    market: str
    korean_name: str
    english_name: str
    trade_volume: float
    trade_price: float
    current_price: float
    change_rate: float


class BinanceBalance(BaseModel):
    total_usdt: float
    available_usdt: float
    locked_usdt: float


class BinanceHolding(BaseModel):
    asset: str
    free: float
    locked: float
    total: float
    current_price: float
    eval_amount: float


class BinanceTopCoin(BaseModel):
    symbol: str
    base_asset: str
    quote_volume: float
    volume: float
    current_price: float
    price_change_percent: float
    # KRW 변환 필드
    current_price_krw: float
    quote_volume_krw: float


class FearGreedIndex(BaseModel):
    value: int
    value_classification: str
    timestamp: int

class WhaleAlert(BaseModel):
    coin: str
    amount: float
    sender: str
    receiver: str
    value_usd: float
    timestamp: str

class DashboardData(BaseModel):
    upbit_balance: Optional[UpbitBalance]
    upbit_holdings: Optional[List[UpbitHolding]]
    upbit_top_volume: Optional[List[UpbitTopCoin]]
    binance_balance: Optional[BinanceBalance]
    binance_holdings: Optional[List[BinanceHolding]]
    binance_top_volume: Optional[List[BinanceTopCoin]]
    fear_greed: Optional[FearGreedIndex]
    whale_alerts: Optional[List[WhaleAlert]]
    last_updated: str


# === 주식 Pydantic 모델 ===

class KoreaStock(BaseModel):
    code: str
    name: str
    current_price: int
    change_rate: float
    trade_volume: int
    trade_value: int  # KRW


class ETFItem(BaseModel):
    symbol: Optional[str] = None
    code: Optional[str] = None
    name: str 
    current_price: float
    change_rate: float
    trade_volume: int
    trade_value: float
    current_price_krw: Optional[float] = None
    trade_value_krw: Optional[float] = None

class USStock(BaseModel):
    symbol: str
    name: str
    current_price: float  # USD
    change_rate: float
    trade_volume: int
    trade_value: float  # USD
    current_price_krw: float
    trade_value_krw: float


class StockIndex(BaseModel):
    name: str
    symbol: str
    current_price: float
    change: float
    change_rate: float


class SectorInfo(BaseModel):
    name: str
    change_rate: float
    volume: str


class NewsItem(BaseModel):
    title: str
    link: str
    date: str
    source: str


class StockDashboardData(BaseModel):
    kospi_top: Optional[List[KoreaStock]]
    kosdaq_top: Optional[List[KoreaStock]]
    us_top: Optional[List[USStock]]
    indices: Optional[List[StockIndex]]
    sectors: Optional[List[SectorInfo]]
    etf_ranking: Optional[List[ETFItem]]
    last_updated: str


# === API 엔드포인트 ===

@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Coin Dashboard API",
        "version": "1.0.0",
        "endpoints": [
            "/api/upbit/balance",
            "/api/upbit/holdings",
            "/api/upbit/top-volume",
            "/api/binance/balance",
            "/api/binance/holdings",
            "/api/binance/top-volume",
            "/api/dashboard"
        ]
    }


@app.get("/api/upbit/balance", response_model=Optional[UpbitBalance])
async def upbit_balance():
    """업비트 잔액 조회"""
    try:
        balance = get_upbit_balance()
        if balance:
            return UpbitBalance(**balance)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/upbit/holdings", response_model=Optional[List[UpbitHolding]])
async def upbit_holdings():
    """업비트 보유 코인 조회"""
    try:
        holdings = get_upbit_holdings()
        if holdings:
            return [UpbitHolding(**h) for h in holdings]
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/upbit/top-volume", response_model=Optional[List[UpbitTopCoin]])
async def upbit_top_volume(limit: int = 10):
    """업비트 거래량 상위 코인 조회"""
    try:
        top_coins = get_upbit_top_volume_coins(limit)
        if top_coins:
            return [UpbitTopCoin(**c) for c in top_coins]
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/binance/balance", response_model=Optional[BinanceBalance])
async def binance_balance():
    """바이낸스 잔액 조회"""
    try:
        balance = get_binance_balance()
        if balance:
            return BinanceBalance(**balance)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/binance/holdings", response_model=Optional[List[BinanceHolding]])
async def binance_holdings():
    """바이낸스 보유 코인 조회"""
    try:
        holdings = get_binance_holdings()
        if holdings:
            return [BinanceHolding(**h) for h in holdings]
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/binance/top-volume", response_model=Optional[List[BinanceTopCoin]])
async def binance_top_volume(limit: int = 10):
    """바이낸스 거래량 상위 코인 조회"""
    try:
        top_coins = get_binance_top_volume_coins(limit)
        if top_coins:
            # USDT/KRW 환율 조회
            usdt_krw_rate = get_usdt_krw_rate()
            
            result = []
            for c in top_coins:
                c['current_price_krw'] = c['current_price'] * usdt_krw_rate
                c['quote_volume_krw'] = c['quote_volume'] * usdt_krw_rate
                result.append(BinanceTopCoin(**c))
            return result
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard", response_model=DashboardData)
async def dashboard():
    """대시보드 전체 데이터 조회 (새로고침용)"""
    try:
        # 업비트 데이터
        upbit_bal = get_upbit_balance()
        upbit_hold = get_upbit_holdings()
        upbit_top = get_upbit_top_volume_coins(10)
        
        # 바이낸스 데이터
        binance_bal = get_binance_balance()
        binance_hold = get_binance_holdings()
        binance_top = get_binance_top_volume_coins(10)
        
        # USDT/KRW 환율 조회
        usdt_krw_rate = get_usdt_krw_rate()
        
        # 바이낸스 거래량 데이터에 KRW 변환 적용
        if binance_top:
            for c in binance_top:
                c['current_price_krw'] = c['current_price'] * usdt_krw_rate
                c['quote_volume_krw'] = c['quote_volume'] * usdt_krw_rate
        
        # Crypto 전용 데이터 추가 호출
        fear_greed = get_crypto_fear_greed()
        whale = get_whale_alerts(5)

        return DashboardData(
            upbit_balance=UpbitBalance(**upbit_bal) if upbit_bal else None,
            upbit_holdings=[UpbitHolding(**h) for h in upbit_hold] if upbit_hold else None,
            upbit_top_volume=[UpbitTopCoin(**c) for c in upbit_top] if upbit_top else None,
            binance_balance=BinanceBalance(**binance_bal) if binance_bal else None,
            binance_holdings=[BinanceHolding(**h) for h in binance_hold] if binance_hold else None,
            binance_top_volume=[BinanceTopCoin(**c) for c in binance_top] if binance_top else None,
            fear_greed=FearGreedIndex(**fear_greed) if fear_greed else None,
            whale_alerts=[WhaleAlert(**w) for w in whale] if whale else None,
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === 주식 API 엔드포인트 ===

@app.get("/api/stock/kospi", response_model=Optional[List[KoreaStock]])
async def kospi_top_volume(limit: int = 10):
    """코스피 거래량 상위 종목 조회"""
    try:
        stocks = get_kospi_top_volume(limit)
        if stocks:
            return [KoreaStock(**s) for s in stocks]
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/kosdaq", response_model=Optional[List[KoreaStock]])
async def kosdaq_top_volume(limit: int = 10):
    """코스닥 거래량 상위 종목 조회"""
    try:
        stocks = get_kosdaq_top_volume(limit)
        if stocks:
            return [KoreaStock(**s) for s in stocks]
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/us", response_model=Optional[List[USStock]])
async def us_top_volume(limit: int = 10):
    """미국 주식 거래량 상위 종목 조회"""
    try:
        stocks = get_us_top_volume(limit)
        if stocks:
            return [USStock(**s) for s in stocks]
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/indices", response_model=List[StockIndex])
async def stock_indices():
    """주요 지수 조회"""
    try:
        data = get_major_indices()
        return [StockIndex(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/sectors", response_model=List[SectorInfo])
async def stock_sectors():
    """섹터별 등락률 조회"""
    try:
        data = get_sector_performance()
        return [SectorInfo(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/news/{query}", response_model=List[NewsItem])
async def stock_news_search(query: str):
    """주식 뉴스 검색"""
    try:
        data = get_stock_news(query)
        return [NewsItem(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/dashboard", response_model=StockDashboardData)
async def stock_dashboard():
    """주식 대시보드 전체 데이터 조회"""
    try:
        kospi = get_kospi_top_volume(10)
        kosdaq = get_kosdaq_top_volume(10)
        us = get_us_top_volume(10)
        indices = get_major_indices()
        sectors = get_sector_performance()
        etfs = get_etf_top_volume("us", 10) # 일단 US ETF만 표시하거나 합쳐서 표시
        
        return StockDashboardData(
            kospi_top=[KoreaStock(**s) for s in kospi] if kospi else None,
            kosdaq_top=[KoreaStock(**s) for s in kosdaq] if kosdaq else None,
            us_top=[USStock(**s) for s in us] if us else None,
            indices=[StockIndex(**i) for i in indices] if indices else None,
            sectors=[SectorInfo(**s) for s in sectors] if sectors else None,
            etf_ranking=[ETFItem(**e) for e in etfs] if etfs else None,
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
