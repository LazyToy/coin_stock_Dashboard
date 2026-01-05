"""
업비트(Upbit) API 모듈
잔액 조회, 보유 코인 조회, 거래량 상위 코인 조회 기능 제공 (Async with anyio)
"""
import pyupbit
from typing import Optional
from backend.services.config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, validate_upbit_keys
from anyio import to_thread

def _get_upbit_client_sync() -> Optional[pyupbit.Upbit]:
    if not validate_upbit_keys():
        return None
    try:
        return pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
    except Exception as e:
        print(f"❌ Upbit 클라이언트 생성 실패: {e}")
        return None

def _get_upbit_balance_sync() -> Optional[dict]:
    upbit = _get_upbit_client_sync()
    if not upbit:
        return None
    try:
        balances = upbit.get_balances()
        krw_balance = {"total_krw": 0, "available_krw": 0, "locked_krw": 0}
        for balance in balances:
            if balance['currency'] == 'KRW':
                krw_balance['available_krw'] = float(balance['balance'])
                krw_balance['locked_krw'] = float(balance['locked'])
                krw_balance['total_krw'] = krw_balance['available_krw'] + krw_balance['locked_krw']
                break
        return krw_balance
    except Exception as e:
        print(f"❌ 잔액 조회 실패: {e}")
        return None

async def get_upbit_balance() -> Optional[dict]:
    return await to_thread.run_sync(_get_upbit_balance_sync)

def _get_upbit_holdings_sync() -> Optional[list]:
    upbit = _get_upbit_client_sync()
    if not upbit:
        return None
    try:
        balances = upbit.get_balances()
        holdings = []
        for balance in balances:
            currency = balance['currency']
            if currency == 'KRW':
                continue
            
            total = float(balance['balance']) + float(balance['locked'])
            avg_buy_price = float(balance['avg_buy_price'])
            current_price = pyupbit.get_current_price(f"KRW-{currency}") or 0.0
            
            if total > 0:
                eval_amount = total * current_price
                buy_amount = total * avg_buy_price
                profit_loss = eval_amount - buy_amount
                profit_loss_percent = (profit_loss / buy_amount * 100) if buy_amount > 0 else 0
                
                holdings.append({
                    "coin": currency,
                    "total": total,
                    "avg_buy_price": avg_buy_price,
                    "current_price": current_price,
                    "eval_amount": eval_amount,
                    "buy_amount": buy_amount,
                    "profit_loss": profit_loss,
                    "profit_loss_percent": profit_loss_percent
                })
        holdings.sort(key=lambda x: x['eval_amount'], reverse=True)
        return holdings
    except Exception as e:
        print(f"❌ 보유 코인 조회 실패: {e}")
        return None

async def get_upbit_holdings() -> Optional[list]:
    return await to_thread.run_sync(_get_upbit_holdings_sync)

_UPBIT_MARKET_NAMES = {}

def _get_market_names():
    global _UPBIT_MARKET_NAMES
    if _UPBIT_MARKET_NAMES:
        return _UPBIT_MARKET_NAMES
    try:
        import requests
        market_url = "https://api.upbit.com/v1/market/all?isDetails=false"
        market_response = requests.get(market_url, timeout=5)
        if market_response.status_code == 200:
            markets_data = market_response.json()
            for m in markets_data:
                if m['market'].startswith('KRW-'):
                     _UPBIT_MARKET_NAMES[m['market']] = {
                         "korean_name": m['korean_name'],
                         "english_name": m['english_name']
                     }
    except Exception as e:
        print(f"Market name fetch failed: {e}")
    return _UPBIT_MARKET_NAMES

def _get_upbit_top_volume_coins_sync(limit: int = 10) -> Optional[list]:
    try:
        # 1. Fetch Market Codes for Korean Names (Cached)
        name_map = _get_market_names()

        # 2. Fetch Tickers for Volume
        tickers = pyupbit.get_tickers(fiat="KRW")
        if not tickers:
            return None
            
        url = "https://api.upbit.com/v1/ticker"
        # Split tickers into chunks if too many? typical is ~110, URI length limit might be hit?
        # Standard Upbit API Ticker usually handles ~100.
        # Let's split if length > 100 just in case or try all. 
        # Actually join all might be too long. 
        # Safe to fetch top volume? We don't know top volume without fetching ticker.
        # Try all. If error, fallback/chunk.
        markets_str = ",".join(tickers)
        
        response = requests.get(url, params={"markets": markets_str}, timeout=5)
        data = response.json()
        
        sorted_data = sorted(data, key=lambda x: x['acc_trade_price_24h'], reverse=True)
        top_coins = []
        
        for item in sorted_data[:limit]:
            # map contains tuple or dict? let's change map to store dict
            # or just (ko, en)
            names = name_map.get(code, {"korean_name": symbol, "english_name": symbol})
            korean_name = names["korean_name"]
            english_name = names["english_name"]
            
            current_price = item['trade_price']
            prev_close = item['prev_closing_price']
            change_rate = ((current_price - prev_close) / prev_close) * 100
            volume_24h = item['acc_trade_volume_24h']
            value_24h = item['acc_trade_price_24h']
            
            top_coins.append({
                "market": code,
                "korean_name": korean_name,
                "english_name": english_name, 
                "current_price": current_price,
                "change_rate": change_rate,
                "trade_volume": volume_24h, # standardized key
                "trade_price": value_24h   # standardized key
            })
            
        return top_coins

    except Exception as e:
        print(f"❌ 상위 코인 조회 실패: {e}")
        return None

# Async Wrappers using loop.run_in_executor as requested
import asyncio
from functools import partial

async def get_upbit_balance() -> Optional[dict]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_upbit_balance_sync)

async def get_upbit_holdings() -> Optional[list]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_upbit_holdings_sync)

async def get_upbit_top_volume_coins(limit: int = 10):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_get_upbit_top_volume_coins_sync, limit))
