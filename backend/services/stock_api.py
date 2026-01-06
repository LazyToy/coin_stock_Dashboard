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
from bs4 import BeautifulSoup

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
    """
    네이버 금융 거래상위 페이지 크롤링하여 실시간 거래량 상위 종목 조회
    market: "kospi" or "kosdaq"
    """
    try:
        sosok = "0" if market == "kospi" else "1"
        url = f"https://finance.naver.com/sise/sise_quant.naver?sosok={sosok}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return []
            
        # Naver Finance uses EUC-KR
        soup = BeautifulSoup(response.content.decode('euc-kr', 'replace'), 'html.parser')
        
        table = soup.select_one('table.type_2')
        if not table:
            return []
            
        rows = table.find_all('tr')
        data_list = []
        
        count = 0
        for row in rows:
            if count >= limit:
                break
                
            cols = row.find_all('td')
            # Valid rows have 'no' class in first column and enough columns
            if len(cols) < 10 or not cols[0].text.strip().isdigit():
                continue
                
            try:
                # Column check:
                # 0: no, 1: name(a tag), 2: current_price, 3: diff(icon/span), 4: change rate, 5: volume, 6: trade value estimate...
                
                name_tag = cols[1].find('a')
                if not name_tag:
                    continue
                    
                name_kor = name_tag.text.strip()
                code = name_tag['href'].split('code=')[-1].strip()
                
                price_text = cols[2].text.strip().replace(',', '')
                if not price_text.isdigit(): continue
                current_price = int(price_text)
                
                # Check previous price to calculate real change rate if needed, or use the one in table
                # Table Col 4 (index 4) is Change Rate (e.g. +1.23%)
                rate_text = cols[4].text.strip().replace('%', '').replace('+', '')
                change_rate = float(rate_text)
                
                volume_text = cols[5].text.strip().replace(',', '')
                trade_volume = int(volume_text)
                
                # Trade Value: Naver gives it in Millions usually. 
                # Let's calculate: price * volume for consistency with previous logic, 
                # or use column 6 (check unit). Column 6 is 'Transaction Amount (Million)'.
                trade_value = current_price * trade_volume
                
                data_list.append({
                    "code": code,
                    "name": name_kor,
                    "current_price": current_price,
                    "change_rate": change_rate,
                    "trade_volume": trade_volume,
                    "trade_value": trade_value
                })
                count += 1
            except Exception as e:
                continue
                
        return data_list
        
    except Exception as e:
        print(f"Korean stock fetch error: {e}")
        return []


def _get_us_top_volume_sync(limit: int = 10) -> Optional[List[dict]]:
    try:
        usd_krw_rate = _get_usd_krw_rate_sync()
        
        # Yahoo Finance Screener/Most Actives API is unstable (502/Blocked).
        # Alternative: Scan a comprehensive list of popular active stocks/ETFs.
        # This ensures reliability while still providing "Real-time" volume ranking.
        target_symbols = [
            # Mag 7 & Tech
            "NVDA", "TSLA", "AAPL", "AMD", "AMZN", "MSFT", "GOOGL", "META", "NFLX", "INTC", "AVGO", "QCOM", "ARM", "MU",
            # Popular ETFs (Leveraged/Inverse often high volume)
            "SQQQ", "TQQQ", "SOXL", "SOXS", "QQQ", "SPY", "IWM", "ARKK", "JEPI", "SCHD", "TLT", "HYG", "XLF", "LABU",
            # Crypto/Meme/Retail
            "COIN", "MSTR", "MARA", "RIOT", "CLSK", "HOOD", "GME", "AMC", "PLTR", "SOFI", "AFRM", "UPST",
            # Major Autos & Industrials
            "F", "GM", "BA", "GE", "CAT",
            # Banking
            "BAC", "JPM", "WFC", "C",
            # Energy/Pharma
            "XOM", "CVX", "PFE", "MRK", "LLY"
        ]
        
        # Add more logic to fetch data using yf.Tickers
        tickers = yf.Tickers(" ".join(target_symbols))
        stocks_data = []
        
        for symbol in target_symbols:
            try:
                t = tickers.tickers[symbol]
                
                # Fast info access
                current_price = None
                volume = None
                prev_close = None
                name = symbol # fallback
                
                if hasattr(t, 'fast_info'):
                     try:
                         current_price = t.fast_info.last_price
                         volume = t.fast_info.last_volume
                         prev_close = t.fast_info.previous_close
                     except:
                         pass
                
                if current_price is None:
                    # History fallback
                    hist = t.history(period="1d")
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        volume = hist['Volume'].iloc[-1]
                        prev_close = hist['Open'].iloc[-1] # Approx or fetch previous
                
                if current_price is not None and volume is not None:
                     change_rate = 0.0
                     if prev_close:
                         change_rate = ((current_price - prev_close) / prev_close) * 100
                         
                     trade_value = current_price * volume
                     
                     stocks_data.append({
                        'symbol': symbol,
                        'name': name,
                        'current_price': round(float(current_price), 2),
                        'change_rate': round(float(change_rate), 2),
                        'trade_volume': int(volume),
                        'trade_value': round(trade_value, 2),
                        'current_price_krw': round(float(current_price) * usd_krw_rate),
                        'trade_value_krw': round(trade_value * usd_krw_rate)
                    })
            except:
                continue
                
        # Sort by Volume (Most Active)
        stocks_data.sort(key=lambda x: x['trade_volume'], reverse=True)
        return stocks_data[:limit]

    except Exception as e:
        print(f"❌ 미국 주식 거래량 조회 실패: {e}")
        return []


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
    """
    네이버 금융 섹터별 시세 (업종별 시세) 크롤링
    """
    try:
        url = "https://finance.naver.com/sise/sise_group.naver?type=upjong"
        # Naver requires headers
        headers = {
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code != 200:
             return []
             
        # EUC-KR decode
        soup = BeautifulSoup(res.content.decode('euc-kr', 'replace'), 'html.parser')
        
        table = soup.select_one('table.type_1')
        if not table:
            return []
            
        rows = table.find_all('tr')
        sectors = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 2: 
                continue
            
            # Col 0: Name (with Link)
            # Col 1: Change Rate (span)
            
            name_tag = cols[0].find('a')
            if not name_tag:
                continue
                
            name = name_tag.text.strip()
            
            change_tag = cols[1].find('span')
            if not change_tag:
                continue
                
            change_text = change_tag.text.strip().replace('%', '').replace('+', '')
            try:
                change_rate = float(change_text)
            except:
                change_rate = 0.0
            
            # Naver format: 
            # If + : red, If -: blue.
            # We just need the float.
            
            volume_label = "강세" if change_rate > 1.0 else ("약세" if change_rate < -1.0 else "보합")
            
            sectors.append({
                "name": name,
                "change_rate": change_rate,
                "volume": volume_label # reusing 'volume' field for trend label
            })
            
        # Optional: return top 3 and bottom 3? Or just top 10?
        # User asked for "Sector fluctuation status".
        # Let's return Top 5 and Bottom 5 wrapped or just list sorted by change?
        # Typically "Performance" implies ranking.
        # Let's sort by change rate descending.
        sectors.sort(key=lambda x: x['change_rate'], reverse=True)
        
        return sectors[:10] # Return Top 10 hottest sectors
        
    except Exception as e:
        print(f"Sector scraping failed: {e}")
        return []


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
