"""
코인 대시보드 API 서버
FastAPI를 사용하여 업비트와 바이낸스 데이터를 제공합니다.
"""
import sys
import os
from anyio import to_thread
import pyupbit

# 상위 디렉토리를 path에 추가하여 기존 모듈 import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 기존 API 모듈 import (Async versions from backend.services)
from backend.services.upbit_api import (
    get_upbit_balance,
    get_upbit_holdings,
    get_upbit_top_volume_coins
)
from backend.services.binance_api import (
    get_binance_balance,
    get_binance_holdings,
    get_binance_top_volume_coins
)
from backend.services.stock_api import (
    get_kospi_top_volume, get_kosdaq_top_volume, get_us_top_volume,
    get_major_indices, get_sector_performance, get_stock_news,
    get_crypto_fear_greed, get_whale_alerts, get_etf_top_volume
)


# === 환율 조회 함수 ===

def _get_usdt_krw_rate_sync() -> float:
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

async def get_usdt_krw_rate() -> float:
    return await to_thread.run_sync(_get_usdt_krw_rate_sync)

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
    coin: str = Field(alias="currency") # Frontend defines it as 'currency', backend generates 'coin' in upbit_api.py. mapping needed or change api.
    # upbit_api.py returns 'coin' key. Frontend types/api.ts UpbitHolding has 'currency'.
    # We should match frontend expectation.
    # In upbit_api.py: "coin": currency
    # Let's alias 'coin' to 'currency' via validator or just alias.
    # Pydantic input is the dict from api.
    # If dict has 'coin', and model has 'currency', we need alias='coin' on 'currency' field.
    currency: str = Field(alias="coin") 
    
    # Wait, frontend interface UpbitHolding:
    # currency: string; balance: number; locked: number; total: number; avg_buy_price: number; current_price: number | null; eval_amount: number; profit_rate: number;
    # upbit_api.py produces: 
    # coin, total, avg_buy_price, current_price, eval_amount, buy_amount, profit_loss, profit_loss_percent
    # There is mismatch.
    # Frontend expects: balance, locked, total...
    # upbit_api.py only gives total.
    # We need to map 'profit_loss_percent' to 'profit_rate'.
    # 'coin' to 'currency'.
    
    total: float
    avg_buy_price: float
    current_price: float
    eval_amount: float
    profit_rate: float = Field(alias="profit_loss_percent")
    
    # Missing in upbit_api.py output but in frontend interface: 
    # balance, locked (optional?)
    # upbit_api.py calculates total but doesn't return balance/locked separate in the dict.
    # Frontend might use them? frontend/components/HoldingsTable.tsx uses item.total.
    # Does it use balance/locked?
    # Let's try to satisfy what we have.
    
    class Config:
        populate_by_name = True


class BinanceBalance(BaseModel):
    total_usdt: float
    available_usdt: float
    locked_usdt: float


class BinanceHolding(BaseModel):
    asset: str
    symbol: str
    total: float
    current_price: float
    eval_amount: float


class UpbitTopCoin(BaseModel):
    market: str
    korean_name: str 
    english_name: str
    trade_volume: float
    trade_price: float
    current_price: float
    change_rate: float
    
    class Config:
        populate_by_name = True

class BinanceTopCoin(BaseModel):
    symbol: str
    base_asset: str
    current_price: float
    change_rate: float = Field(alias="price_change_percent")
    quote_volume: float
    current_price_krw: float
    quote_volume_krw: float
    
    class Config:
        populate_by_name = True

class CryptoFearGreed(BaseModel):
    value: int
    value_classification: str
    timestamp: int

class WhaleAlert(BaseModel):
    coin: str
    amount: float
    sender: str = Field(alias="from")
    receiver: str = Field(alias="to")
    value_usd: float
    timestamp: str = Field(alias="time")
    
    class Config:
        populate_by_name = True

class DashboardData(BaseModel):
    upbit_balance: Optional[UpbitBalance]
    upbit_holdings: Optional[List[UpbitHolding]]
    upbit_top_volume: Optional[List[UpbitTopCoin]]
    binance_balance: Optional[BinanceBalance]
    binance_holdings: Optional[List[BinanceHolding]]
    binance_top_volume: Optional[List[BinanceTopCoin]]
    fear_greed: Optional[CryptoFearGreed]
    whale_alerts: Optional[List[WhaleAlert]]
    last_updated: str


# Stock Models (Reused/Adapted)
class KoreaStock(BaseModel):
    code: str
    name: str
    current_price: int
    change_rate: float
    trade_volume: int
    trade_value: int

class USStock(BaseModel):
    symbol: str
    name: str
    current_price: float
    change_rate: float
    trade_volume: int
    trade_value: float
    current_price_krw: float
    trade_value_krw: float

class StockIndex(BaseModel):
    name: str
    current_price: float
    change_rate: float
    change: float
    current_price_krw: float

class SectorInfo(BaseModel):
    name: str
    change_rate: float
    volume: str

class ETFItem(BaseModel):
    symbol: str
    name: str
    current_price: float
    change_rate: float
    trade_volume: int

class StockDashboardData(BaseModel):
    kospi_top: Optional[List[KoreaStock]]
    kosdaq_top: Optional[List[KoreaStock]]
    us_top: Optional[List[USStock]]
    indices: Optional[List[StockIndex]]
    sectors: Optional[List[SectorInfo]]
    etf_ranking: Optional[List[ETFItem]]
    last_updated: str
    
class NewsItem(BaseModel):
    title: str
    link: str
    date: str
    source: str


# === API 엔드포인트 ===

@app.get("/")
async def root():
    return {"message": "Coin Dashboard API is running"}


@app.get("/api/dashboard", response_model=DashboardData)
async def dashboard():
    """암호화폐 대시보드 전체 데이터 조회 (Crypto)"""
    try:
        # Parallel execution could be better, but consecutive await is fine for now
        # Ideally: await asyncio.gather(...)
        import asyncio
        
        # Balance & Holdings & Rate
        # We need rate for Binance Top Volume calculation
        usdt_krw = await get_usdt_krw_rate()

        future_up_bal = asyncio.create_task(get_upbit_balance())
        future_up_hold = asyncio.create_task(get_upbit_holdings())
        future_bn_bal = asyncio.create_task(get_binance_balance())
        future_bn_hold = asyncio.create_task(get_binance_holdings())
        
        # Top Volume
        future_up_top = asyncio.create_task(get_upbit_top_volume_coins(10)) 
        future_bn_top = asyncio.create_task(get_binance_top_volume_coins(10, usdt_krw))
        
        # Others
        future_fg = asyncio.create_task(get_crypto_fear_greed())
        future_whale = asyncio.create_task(get_whale_alerts(5))
        
        up_bal = await future_up_bal
        up_hold = await future_up_hold
        bn_bal = await future_bn_bal
        bn_hold = await future_bn_hold
        up_top = await future_up_top
        bn_top = await future_bn_top
        fg = await future_fg
        whale = await future_whale
        
        return DashboardData(
            upbit_balance=UpbitBalance(**up_bal) if up_bal else None,
            upbit_holdings=[UpbitHolding(**h) for h in up_hold] if up_hold else None,
            upbit_top_volume=[UpbitTopCoin(**c) for c in up_top] if up_top else None,
            binance_balance=BinanceBalance(**bn_bal) if bn_bal else None,
            binance_holdings=[BinanceHolding(**h) for h in bn_hold] if bn_hold else None,
            binance_top_volume=[BinanceTopCoin(**c) for c in bn_top] if bn_top else None,
            fear_greed=CryptoFearGreed(**fg) if fg else None,
            whale_alerts=[WhaleAlert(**w) for w in whale] if whale else None,
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        print(f"Error in dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/dashboard", response_model=StockDashboardData)
async def stock_dashboard():
    """주식 대시보드 전체 데이터 조회"""
    try:
        kospi = await get_kospi_top_volume(10)
        kosdaq = await get_kosdaq_top_volume(10)
        us = await get_us_top_volume(10)
        indices = await get_major_indices()
        sectors = await get_sector_performance()
        etfs = await get_etf_top_volume("us", 10) 
        
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
        print(f"Error in stock_dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/news/{query}", response_model=List[NewsItem])
async def stock_news_search(query: str):
    """주식 뉴스 검색"""
    try:
        data = await get_stock_news(query)
        return [NewsItem(**item) for item in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # reload=True is useful for dev
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
