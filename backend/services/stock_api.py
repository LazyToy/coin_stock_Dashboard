"""
주식 API 모듈
국내주식(코스피/코스닥)과 해외주식(미국) 데이터를 제공합니다. (Async with anyio)
"""
from datetime import datetime, timedelta
from typing import Optional, List
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from anyio import to_thread
import yfinance as yf
import asyncio
from functools import partial

# 한국 주식 (Legcay pykrx support removed or kept minimal if needed, but we use yfinance now)
# 미국 주식
YFINANCE_AVAILABLE = True

def _get_usd_krw_rate_sync() -> float:
    """
    USD/KRW 환율을 조회합니다 (Sync).
    yfinance를 이용해 조회합니다.
    """
    try:
        # pyupbit dependency usage for rate reduced to minimize mixed logic, 
        # or use yfinance for rate "KRW=X" 
        ticker = yf.Ticker("KRW=X")
        price = ticker.fast_info.last_price
        if price:
            return float(price)
    except Exception as e:
        print(f"환율 조회 실패: {e}")
    return 1450.0  # 기본값

async def get_usd_krw_rate() -> float:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_usd_krw_rate_sync)


def get_recent_trading_dates(days: int = 7) -> List[str]:
    """
    최근 거래일 후보 목록을 반환합니다 (YYYYMMDD 형식).
    """
    dates = []
    today = datetime.now()
    for i in range(days):
        check_date = today - timedelta(days=i)
        if check_date.weekday() < 5:  # 월~금
            dates.append(check_date.strftime("%Y%m%d"))
    return dates


def _get_real_korea_stock_data_sync(market="kospi", limit=10):
    kospi_symbols = [
        "005930.KS", "000660.KS", "373220.KS", "207940.KS", "005380.KS", 
        "000270.KS", "068270.KS", "005490.KS", "105560.KS", "035420.KS",
        "051910.KS", "035720.KS", "006400.KS", "003550.KS", "012330.KS",
        "028260.KS", "032830.KS", "086790.KS", "011200.KS", "055550.KS",
        "034020.KS", "003670.KS", "010130.KS", "009150.KS", "015760.KS"
    ]
    kosdaq_symbols = [
         "247540.KQ", "086520.KQ", "196170.KQ", "022100.KQ", "066970.KQ",
         "028300.KQ", "277810.KQ", "263750.KQ", "293490.KQ", "035900.KQ",
         "041510.KQ", "393890.KQ", "403870.KQ", "214150.KQ", "005290.KQ",
         "091990.KQ", "039030.KQ", "145020.KQ", "036930.KQ", "000250.KQ"
    ]
    symbols = kospi_symbols if market == "kospi" else kosdaq_symbols
    
    name_map = {
        "005930.KS": "삼성전자", "000660.KS": "SK하이닉스", "373220.KS": "LG에너지솔루션",
        "207940.KS": "삼성바이오로직스", "005380.KS": "현대차", "000270.KS": "기아",
        "068270.KS": "셀트리온", "005490.KS": "POSCO홀딩스", "105560.KS": "KB금융",
        "035420.KS": "NAVER", "051910.KS": "LG화학", "035720.KS": "카카오",
        "006400.KS": "삼성SDI", "003550.KS": "LG", "012330.KS": "현대모비스",
        "028260.KS": "삼성물산", "032830.KS": "삼성생명", "086790.KS": "하나금융지주",
        "011200.KS": "HMM", "055550.KS": "신한지주",
        "247540.KQ": "에코프로비엠", "086520.KQ": "에코프로", "196170.KQ": "알테오젠",
        "022100.KQ": "포스코DX", "066970.KQ": "엘앤에프", "028300.KQ": "HLB",
        "277810.KQ": "휴젤", "263750.KQ": "펄어비스", "293490.KQ": "카카오게임즈",
        "041510.KQ": "에스엠", "393890.KQ": "더블유씨피", "403870.KQ": "HPSP",
        "214150.KQ": "클래시스", "005290.KQ": "동진쎄미켐",
        "091990.KQ": "셀트리온제약", "039030.KQ": "이오테크닉스"
    }

    try:
        tickers = yf.Tickers(" ".join(symbols))
        data_list = []
        for sym in symbols:
            try:
                t = tickers.tickers[sym]
                price = None
                volume = None
                prev = None

                # fast_info access
                if hasattr(t, 'fast_info'):
                    try:
                        price = t.fast_info.last_price
                        prev = t.fast_info.previous_close
                        volume = t.fast_info.last_volume
                    except:
                        pass
                
                # Fallback to history
                if price is None:
                     hist = t.history(period='1d')
                     if not hist.empty:
                         price = hist['Close'].iloc[-1]
                         volume = hist['Volume'].iloc[-1]
                         if len(hist) > 1:
                             prev = hist['Close'].iloc[-2]
                         else:
                             prev = price 

                if price is None:
                    continue

                change_rate = 0.0
                if prev and prev > 0:
                    change_rate = ((price - prev) / prev) * 100
                
                trade_value = price * volume if volume else 0
                code_pure = sym.split('.')[0]
                name_kor = name_map.get(sym, sym)
                
                data_list.append({
                    "code": code_pure,
                    "name": name_kor,
                    "current_price": int(price),
                    "change_rate": round(change_rate, 2),
                    "trade_volume": int(volume) if volume else 0,
                    "trade_value": int(trade_value)
                })
            except:
                continue
                
        data_list.sort(key=lambda x: x['trade_value'], reverse=True)
        return data_list[:limit]
    except Exception as e:
        print(f"yfinance fetch error: {e}")
        return []


def _get_us_top_volume_sync(limit: int = 10) -> Optional[List[dict]]:
    try:
        major_symbols = [
            "NVDA", "TSLA", "AAPL", "AMD", "AMZN", 
            "META", "MSFT", "GOOGL", "NFLX", "INTC",
            "PLTR", "COIN", "MARA", "RIOT", "BA",
            "JPM", "BAC", "WFC", "C", "GS",
            "XOM", "CVX", "PFE", "JNJ", "UNH"
        ]
        
        usd_krw_rate = _get_usd_krw_rate_sync()
        stocks_data = []
        
        tickers = yf.Tickers(" ".join(major_symbols))
        
        for symbol in major_symbols:
            try:
                ticker = tickers.tickers[symbol]
                
                # using fast_info for speed
                current_price = None
                prev_close = None
                volume = None
                name = symbol
                
                if hasattr(ticker, 'fast_info'):
                    try:
                        current_price = ticker.fast_info.last_price
                        prev_close = ticker.fast_info.previous_close
                        volume = ticker.fast_info.last_volume
                    except:
                         pass

                if current_price is None:
                    # Fallback
                    info = ticker.info
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                    prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
                    volume = info.get('volume') or info.get('regularMarketVolume')
                    name = info.get('shortName') or info.get('longName', symbol)

                if current_price and prev_close and volume:
                    change_rate = ((current_price - prev_close) / prev_close) * 100
                    trade_value = current_price * volume
                    
                    stocks_data.append({
                        'symbol': symbol,
                        'name': name,
                        'current_price': round(current_price, 2),
                        'change_rate': round(change_rate, 2),
                        'trade_volume': int(volume),
                        'trade_value': round(trade_value, 2),
                        'current_price_krw': round(current_price * usd_krw_rate),
                        'trade_value_krw': round(trade_value * usd_krw_rate)
                    })
            except:
                continue
        
        stocks_data.sort(key=lambda x: x['trade_value'], reverse=True)
        return stocks_data[:limit]
    except Exception as e:
        print(f"❌ 미국 주식 거래량 조회 실패: {e}")
        return None


def _get_major_indices_sync() -> List[dict]:
    indices = [
        {"name": "KOSPI", "symbol": "^KS11"},
        {"name": "KOSDAQ", "symbol": "^KQ11"},
        {"name": "Dow Jones", "symbol": "^DJI"},
        {"name": "Nasdaq", "symbol": "^IXIC"},
        {"name": "S&P 500", "symbol": "^GSPC"}
    ]
    result = []
    try:
        usd_krw = _get_usd_krw_rate_sync()
        for idx in indices:
            try:
                ticker = yf.Ticker(idx['symbol'])
                hist = ticker.history(period="5d")
                if len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2]
                    change = current - prev
                    change_rate = (change / prev) * 100
                    result.append({
                        "name": idx['name'],
                        "current_price": round(current, 2),
                        "change_rate": round(change_rate, 2),
                        "change": round(change, 2),
                        "current_price_krw": round(current * usd_krw) if "Dow" in idx['name'] or "Nas" in idx['name'] or "S&P" in idx['name'] else round(current)
                    })
            except:
                continue
    except:
        pass
    return result


def _get_sector_performance_sync() -> List[dict]:
    # Dummy implementation for sectors as crawling is hard
    return [
        {"name": "반도체", "change_rate": 2.5, "volume": "강세"},
        {"name": "2차전지", "change_rate": -1.2, "volume": "약세"},
        {"name": "자동차", "change_rate": 1.8, "volume": "강세"},
        {"name": "헬스케어", "change_rate": -0.5, "volume": "보합"},
        {"name": "인터넷/게임", "change_rate": 0.3, "volume": "보합"},
        {"name": "은행/금융", "change_rate": 1.1, "volume": "강세"},
    ]


def _get_stock_news_sync(query: str, limit: int = 5) -> List[dict]:
    try:
        encoded_query = quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            news_list = []
            for item in items[:limit]:
                title = item.find('title').text if item.find('title') is not None else "No Title"
                link = item.find('link').text if item.find('link') is not None else "#"
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
                source = item.find('source').text if item.find('source') is not None else "Google News"
                news_list.append({
                    "title": title,
                    "link": link,
                    "date": pubDate,
                    "source": source
                })
            return news_list
    except Exception as e:
        print(f"뉴스 조회 실패: {e}")
    return []


def _get_crypto_fear_greed_sync() -> dict:
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                item = data['data'][0]
                return {
                    "value": int(item['value']),
                    "value_classification": item['value_classification'],
                    "timestamp": int(item['timestamp'])
                }
    except:
        pass
    return {"value": 50, "value_classification": "Neutral", "timestamp": 0}


def _get_whale_alerts_sync(limit: int = 5) -> List[dict]:
    # Simulation
    import random
    coins = ["BTC", "ETH", "XRP", "USDT", "SOL", "DOGE"]
    exchanges = ["Binance", "Coinbase", "Upbit", "Kraken", "Unknown Wallet"]
    alerts = []
    current_time = datetime.now()
    for i in range(limit):
        time_offset = random.randint(1, 60)
        timestamp = (current_time - timedelta(minutes=time_offset)).isoformat()
        coin = random.choice(coins)
        amount = random.randint(1000, 100000)
        from_ex = random.choice(exchanges)
        to_ex = random.choice(exchanges)
        if from_ex == to_ex: to_ex = "Wallet"
        alerts.append({
            "key": f"{i}",
            "time": timestamp,
            "coin": coin,
            "amount": amount,
            "from": from_ex,
            "to": to_ex,
            "value_usd": amount * (50000 if coin=="BTC" else 3000 if coin=="ETH" else 1) 
        })
    return alerts


def _get_etf_top_volume_sync(market: str = "us", limit: int = 10) -> List[dict]:
    # Implementation simliar to get_real_korea_stock_data but for ETFs
    # Assuming similar implementation is needed or we use a basic list
    symbols = [
        "QQQ", "SPY", "TQQQ", "SOXL", "SQQQ", "JEPI", "SCHD", "IVV", "VTI", "VOO",
        "IWM", "EEM", "GLD", "SLV", "ARKK", "HYG", "XLF", "XLK", "SMH", "LABU"
    ]
    name_map = {
        "QQQ": "Invesco QQQ", "SPY": "SPDR S&P 500", "TQQQ": "ProShares UltraPro QQQ",
        "SOXL": "Direxion Daily Semiconductor Bull 3X", "SQQQ": "ProShares UltraPro Short QQQ",
        "JEPI": "JPMorgan Equity Premium Income", "SCHD": "Schwab US Dividend Equity",
        "IVV": "iShares Core S&P 500", "VTI": "Vanguard Total Stock Market",
        "VOO": "Vanguard S&P 500", "IWM": "iShares Russell 2000",
        "EEM": "iShares MSCI Emerging Markets", "GLD": "SPDR Gold Shares",
        "SLV": "iShares Silver Trust", "ARKK": "ARK Innovation ETF",
        "HYG": "iShares iBoxx $ High Yield Corporate Bond", "XLF": "Financial Select Sector SPDR Fund",
        "XLK": "Technology Select Sector SPDR Fund", "SMH": "VanEck Semiconductor ETF",
        "LABU": "Direxion Daily S&P Biotech Bull 3X Shares"
    }

    try:
        tickers = yf.Tickers(" ".join(symbols))
        result = []
        for sym in symbols:
            try:
                t = tickers.tickers[sym]
                # Fast info
                current = None
                volume = None
                prev = None
                
                if hasattr(t, 'fast_info'):
                    try:
                        current = t.fast_info.last_price
                        volume = t.fast_info.last_volume
                        prev = t.fast_info.previous_close
                    except:
                        pass
                
                if current is None:
                    continue
                
                change_rate = 0.0
                if prev:
                    change_rate = ((current - prev)/prev)*100
                
                result.append({
                    "symbol": sym,
                    "name": name_map.get(sym, sym),
                    "current_price": current,
                    "change_rate": change_rate,
                    "trade_volume": int(volume)
                })
            except:
                continue
        
        # Sort by volume
        result.sort(key=lambda x: x.get('trade_volume', 0), reverse=True)
        return result[:limit]

    except Exception:
        pass
    return []

# Async Wrappers using loop.run_in_executor
async def get_real_korea_stock_data(market="kospi", limit=10):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_get_real_korea_stock_data_sync, market, limit))

async def get_kospi_top_volume(limit=10):
    return await get_real_korea_stock_data("kospi", limit)

async def get_kosdaq_top_volume(limit=10):
    return await get_real_korea_stock_data("kosdaq", limit)

async def get_us_top_volume(limit=10):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_get_us_top_volume_sync, limit))

async def get_major_indices():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_major_indices_sync)

async def get_sector_performance():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_sector_performance_sync)

async def get_etf_top_volume(market="us", limit=10):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_get_etf_top_volume_sync, market, limit))
    
async def get_stock_news(query):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_get_stock_news_sync, query))

async def get_crypto_fear_greed():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_crypto_fear_greed_sync)

async def get_whale_alerts(limit=5):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_get_whale_alerts_sync, limit))
