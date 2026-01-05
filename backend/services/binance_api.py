"""
바이낸스(Binance) API 모듈
잔액 조회, 보유 코인 조회, 거래량 상위 코인 조회 기능 제공 (Async with anyio)
"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
from typing import Optional
from backend.services.config import BINANCE_ACCESS_KEY, BINANCE_SECRET_KEY, validate_binance_keys
from anyio import to_thread

def _get_binance_client_sync() -> Optional[Client]:
    if not validate_binance_keys():
        return None
    try:
        return Client(BINANCE_ACCESS_KEY, BINANCE_SECRET_KEY)
    except Exception as e:
        print(f"❌ Binance 클라이언트 생성 실패: {e}")
        return None

def _get_binance_balance_sync() -> Optional[dict]:
    client = _get_binance_client_sync()
    if not client:
        return None
    try:
        account = client.get_account()
        balances = account['balances']
        usdt_balance = {"total_usdt": 0, "available_usdt": 0, "locked_usdt": 0}
        for balance in balances:
            if balance['asset'] == 'USDT':
                usdt_balance['available_usdt'] = float(balance['free'])
                usdt_balance['locked_usdt'] = float(balance['locked'])
                usdt_balance['total_usdt'] = usdt_balance['available_usdt'] + usdt_balance['locked_usdt']
                break
        return usdt_balance
    except Exception as e:
        print(f"❌ 잔액 조회 실패: {e}")
        return None

async def get_binance_balance() -> Optional[dict]:
    return await to_thread.run_sync(_get_binance_balance_sync)

def _get_binance_holdings_sync() -> Optional[list]:
    client = _get_binance_client_sync()
    if not client:
        return None
    try:
        account = client.get_account()
        balances = account['balances']
        holdings = []
        
        # Get all prices efficiently
        # get_all_tickers returns list of dicts [{'symbol': 'BTCUSDT', 'price': '...'}]
        tickers = client.get_all_tickers()
        price_map = {t['symbol']: float(t['price']) for t in tickers}
        
        for balance in balances:
            asset = balance['asset']
            if asset == 'USDT':
                continue
                
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            
            if total > 0:
                # Estimate price in USDT
                symbol = f"{asset}USDT"
                current_price = price_map.get(symbol, 0.0)
                
                # Filter small dust
                eval_amount = total * current_price
                if eval_amount < 1: # Skip dust < 1 USDT
                    continue
                    
                holdings.append({
                    "asset": asset,
                    "symbol": symbol,
                    "total": total,
                    "current_price": current_price,
                    "eval_amount": eval_amount
                })
        
        holdings.sort(key=lambda x: x['eval_amount'], reverse=True)
        return holdings
    except Exception as e:
        print(f"❌ 보유 코인 조회 실패: {e}")
        return None

async def get_binance_holdings() -> Optional[list]:
    return await to_thread.run_sync(_get_binance_holdings_sync)

def _get_binance_top_volume_coins_sync(limit: int = 10) -> Optional[list]:
    try:
        import requests
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return None
            
        tickers = response.json()
        
        # Filter USDT pairs only
        usdt_tickers = [t for t in tickers if t['symbol'].endswith('USDT')]
        
        # Sort by quoteVolume (USDT volume)
        sorted_tickers = sorted(usdt_tickers, key=lambda x: float(x['quoteVolume']), reverse=True)
        
        top_coins = []
        for t in sorted_tickers[:limit]:
            symbol = t['symbol']
            base_asset = symbol.replace("USDT", "")
            current_price = float(t['lastPrice'])
            price_change_percent = float(t['priceChangePercent'])
            quote_volume = float(t['quoteVolume'])
            
            top_coins.append({
                "symbol": symbol,
                "base_asset": base_asset,
                "current_price": current_price,
                "price_change_percent": price_change_percent,
                "quote_volume": quote_volume,
                "trade_volume": quote_volume,
                "trade_price": quote_volume
            })
        return top_coins
    except Exception as e:
        print(f"❌ 상위 코인 조회 실패: {e}")
        return None

# Async Wrappers using loop.run_in_executor as requested
import asyncio
from functools import partial

async def get_binance_balance() -> Optional[dict]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_binance_balance_sync)

async def get_binance_holdings() -> Optional[list]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_binance_holdings_sync)

def _get_binance_top_volume_coins_sync(limit: int = 10, usdt_krw: float = 1450.0) -> Optional[list]:
    try:
        import requests
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return None
            
        tickers = response.json()
        
        # Filter USDT pairs only
        usdt_tickers = [t for t in tickers if t['symbol'].endswith('USDT')]
        
        # Sort by quoteVolume (USDT volume)
        sorted_tickers = sorted(usdt_tickers, key=lambda x: float(x['quoteVolume']), reverse=True)
        
        top_coins = []
        for t in sorted_tickers[:limit]:
            symbol = t['symbol']
            base_asset = symbol.replace("USDT", "")
            current_price = float(t['lastPrice'])
            price_change_percent = float(t['priceChangePercent'])
            quote_volume = float(t['quoteVolume'])
            
            top_coins.append({
                "symbol": symbol,
                "base_asset": base_asset,
                "current_price": current_price,
                "price_change_percent": price_change_percent,
                "quote_volume": quote_volume,
                "current_price_krw": current_price * usdt_krw,
                "quote_volume_krw": quote_volume * usdt_krw
            })
        return top_coins
    except Exception as e:
        print(f"❌ 상위 코인 조회 실패: {e}")
        return None

# Async Wrappers using loop.run_in_executor as requested
import asyncio
from functools import partial

async def get_binance_balance() -> Optional[dict]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_binance_balance_sync)

async def get_binance_holdings() -> Optional[list]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_binance_holdings_sync)

async def get_binance_top_volume_coins(limit: int = 10, usdt_krw: float = 1450.0):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_get_binance_top_volume_coins_sync, limit, usdt_krw))
