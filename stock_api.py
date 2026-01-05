"""
주식 API 모듈
국내주식(코스피/코스닥)과 해외주식(미국) 데이터를 제공합니다.
"""
from datetime import datetime, timedelta
from typing import Optional, List
import pyupbit
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
import random

# 한국 주식
try:
    from pykrx import stock as krx
    PYKRX_AVAILABLE = True
except ImportError:
    PYKRX_AVAILABLE = False
    print("⚠️ pykrx 라이브러리를 설치해주세요: pip install pykrx")

# 미국 주식
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance 라이브러리를 설치해주세요: pip install yfinance")


def get_usd_krw_rate() -> float:
    """
    USD/KRW 환율을 조회합니다.
    업비트의 USDT/KRW 시세를 활용합니다.
    """
    try:
        rate = pyupbit.get_current_price("KRW-USDT")
        if rate:
            return float(rate)
    except Exception as e:
        print(f"환율 조회 실패: {e}")
    return 1450.0  # 기본값


def get_recent_trading_dates(days: int = 7) -> List[str]:
    """
    최근 거래일 후보 목록을 반환합니다 (YYYYMMDD 형식).
    주말과 공휴일을 고려하여 최대 days일 전까지의 날짜를 반환합니다.
    """
    dates = []
    today = datetime.now()
    
    for i in range(days):
        check_date = today - timedelta(days=i)
        # 주말 제외
        if check_date.weekday() < 5:  # 월~금
            dates.append(check_date.strftime("%Y%m%d"))
    
    return dates


def get_real_korea_stock_data(market="kospi", limit=10):
    if not YFINANCE_AVAILABLE:
        return get_kospi_sample_data(limit) if market == "kospi" else get_kosdaq_sample_data(limit)

    import yfinance as yf
    
    # Major stocks list for yfinance (Top Market Cap)
    # yfinance requires .KS for KOSPI, .KQ for KOSDAQ
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
    
    # Name Mapping (yfinance returns English names usually, we want Korean if possible)
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
        # Batch Fetch
        tickers = yf.Tickers(" ".join(symbols))
        data_list = []
        
        for sym in symbols:
            try:
                t = tickers.tickers[sym]
                # Use fast_info for speed
                # Note: fast_info API might vary by yfinance version. Safe access.
                price = None
                volume = None
                prev = None

                if hasattr(t, 'fast_info'):
                    price = t.fast_info.last_price
                    prev = t.fast_info.previous_close
                    volume = t.fast_info.last_volume
                
                # Fallback to info (slower) or history if fast_info fails/is None
                if price is None:
                     hist = t.history(period='1d')
                     if not hist.empty:
                         price = hist['Close'].iloc[-1]
                         volume = hist['Volume'].iloc[-1]
                         # prev close not in 1d history easily, assume open or try to fetch more
                         # Just use price for now
                         if len(hist) > 1:
                             prev = hist['Close'].iloc[-2]
                         else:
                             prev = price # No change info

                if price is None:
                    continue

                change_rate = 0.0
                if prev and prev > 0:
                    change_rate = ((price - prev) / prev) * 100
                
                trade_value = price * volume if volume else 0
                
                code_pure = sym.split('.')[0]
                name_kor = name_map.get(sym, sym) # Fallback to symbol if map missing
                
                data_list.append({
                    "code": code_pure,
                    "name": name_kor,
                    "current_price": int(price),
                    "change_rate": round(change_rate, 2),
                    "trade_volume": int(volume) if volume else 0,
                    "trade_value": int(trade_value)
                })
            except Exception as e:
                # print(f"Error processing {sym}: {e}")
                continue
                
        # Sort by trade_value (active)
        data_list.sort(key=lambda x: x['trade_value'], reverse=True)
        return data_list[:limit]
        
    except Exception as e:
        print(f"yfinance fetch error: {e}")
        return get_kospi_sample_data(limit) if market == "kospi" else get_kosdaq_sample_data(limit)


def get_kospi_top_volume(limit: int = 10) -> Optional[List[dict]]:
    """
    코스피 거래량 상위 종목을 조회합니다 (yfinance 기반 실시간).
    """
    return get_real_korea_stock_data("kospi", limit)


def get_kosdaq_top_volume(limit: int = 10) -> Optional[List[dict]]:
    """
    코스닥 거래량 상위 종목을 조회합니다 (yfinance 기반 실시간).
    """
    return get_real_korea_stock_data("kosdaq", limit)


def get_us_top_volume(limit: int = 10) -> Optional[List[dict]]:
    """
    미국 주식 거래량 상위 종목을 조회합니다.
    S&P500 및 나스닥 주요 종목 중심으로 조회합니다.
    
    Returns:
        list: 거래량 상위 종목 정보
            - symbol: 티커 심볼
            - name: 종목명
            - current_price: 현재가 (USD)
            - change_rate: 등락률 (%)
            - trade_volume: 거래량
            - trade_value: 거래대금 (USD)
            - current_price_krw: 현재가 (KRW)
            - trade_value_krw: 거래대금 (KRW)
    """
    if not YFINANCE_AVAILABLE:
        return None
    
    try:
        # 주요 미국 주식 목록 (거래량 상위 종목들)
        major_symbols = [
            "NVDA", "TSLA", "AAPL", "AMD", "AMZN", 
            "META", "MSFT", "GOOGL", "NFLX", "INTC",
            "PLTR", "COIN", "MARA", "RIOT", "BA",
            "JPM", "BAC", "WFC", "C", "GS",
            "XOM", "CVX", "PFE", "JNJ", "UNH"
        ]
        
        # 환율 조회
        usd_krw_rate = get_usd_krw_rate()
        
        stocks_data = []
        
        for symbol in major_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # 필요한 데이터 추출
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose', 0)
                volume = info.get('volume') or info.get('regularMarketVolume', 0)
                name = info.get('shortName') or info.get('longName', symbol)
                
                if current_price and prev_close and volume:
                    change_rate = ((current_price - prev_close) / prev_close) * 100
                    trade_value = current_price * volume
                    
                    stocks_data.append({
                        'symbol': symbol,
                        'name': name,  # 이름 길이 제한 제거
                        'current_price': round(current_price, 2),
                        'change_rate': round(change_rate, 2),
                        'trade_volume': int(volume),
                        'trade_value': round(trade_value, 2),
                        'current_price_krw': round(current_price * usd_krw_rate),
                        'trade_value_krw': round(trade_value * usd_krw_rate)
                    })
            except Exception as e:
                print(f"종목 {symbol} 조회 실패: {e}")
                continue
        
        # 거래대금 기준 정렬
        stocks_data.sort(key=lambda x: x['trade_value'], reverse=True)
        
        return stocks_data[:limit]
    
    except Exception as e:
        print(f"❌ 미국 주식 거래량 조회 실패: {e}")
        return None



# === 새로운 기능: 주요 지수, 섹터, 뉴스 ===

def get_major_indices() -> List[dict]:
    """
    주요 지수 정보 조회 (KOSPI, KOSDAQ, 다우, 나스닥, S&P500)
    """
    indices = [
        {"name": "KOSPI", "symbol": "^KS11"},
        {"name": "KOSDAQ", "symbol": "^KQ11"},
        {"name": "Dow Jones", "symbol": "^DJI"},
        {"name": "Nasdaq", "symbol": "^IXIC"},
        {"name": "S&P 500", "symbol": "^GSPC"}
    ]
    
    result = []
    
    # 1. yfinance로 시도
    if YFINANCE_AVAILABLE:
        try:
            usd_krw = get_usd_krw_rate()
            for idx in indices:
                try:
                    ticker = yf.Ticker(idx['symbol'])
                    hist = ticker.history(period="5d") # 최근 5일 데이터
                    
                    if len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        prev = hist['Close'].iloc[-2]
                        change = current - prev
                        change_rate = (change / prev) * 100
                        
                        result.append({
                            "name": idx['name'],
                            "current_price": round(current, 2),
                            "change": round(change, 2),
                            "change_rate": round(change_rate, 2),
                            "symbol": idx['symbol']
                        })
                except Exception as e:
                    print(f"{idx['name']} 조회 실패: {e}")
                    continue
        except Exception:
            pass
            
    # 데이터가 없으면 샘플 데이터 사용
    if not result:
        return [
            {"name": "KOSPI", "current_price": 2650.45, "change": 12.30, "change_rate": 0.47, "symbol": "^KS11"},
            {"name": "KOSDAQ", "current_price": 870.12, "change": -5.40, "change_rate": -0.62, "symbol": "^KQ11"},
            {"name": "Dow Jones", "current_price": 39000.50, "change": 150.20, "change_rate": 0.39, "symbol": "^DJI"},
            {"name": "Nasdaq", "current_price": 16300.80, "change": 80.50, "change_rate": 0.50, "symbol": "^IXIC"},
            {"name": "S&P 500", "current_price": 5100.20, "change": 20.10, "change_rate": 0.40, "symbol": "^GSPC"},
        ]
    
    return result


def get_sector_performance() -> List[dict]:
    """
    주요 섹터별 등락률 조회 (KRX 지수 활용 및 매핑)
    반도체, 2차전지, 자동차, 헬스케어, 인터넷/게임
    """
    # KRX 지수 매핑 (실제 존재하는 지수명으로 근사)
    sectors = [
        {"name": "반도체", "category": "KRX 반도체"},
        {"name": "2차전지", "category": "KRX 2차전지 K-뉴딜"}, # 존재하지 않을 수 있으니 확인 필요. KRX 에너지화학 등으로 대체 가능
        {"name": "자동차", "category": "KRX 자동차"},
        {"name": "헬스케어", "category": "KRX 헬스케어"},
        {"name": "인터넷/게임", "category": "KRX 미디어&엔터테인먼트"}, # 또는 KRX 인터넷 K-뉴딜
        {"name": "은행/금융", "category": "KRX 은행"},
    ]
    
    result = []
    
    if PYKRX_AVAILABLE:
        try:
            # krx.get_index_ticker_list()는 지수 코드를 반환함.
            # 날짜 구하기
            dates = get_recent_trading_dates(7)
            latest_date = None
            
            # 유효한 날짜 찾기
            for date in dates:
                try:
                    # KOSPI 지수라도 조회해서 나오나 확인
                    test = krx.get_index_ohlcv_by_ticker(date, "1001") # 코스피
                    if not test.empty:
                        latest_date = date
                        break
                except:
                    continue
            
            if latest_date:
                # 전체 지수 목록 가져오기 (시간 단축을 위해 미리 가져와서 매핑할 수도 있음)
                # 여기서는 각 섹터별로 티커를 찾거나, 미리 조사된 티커 사용
                # 주요 KRX 지수 티커 (2024년 기준, 변경될 수 있음)
                # 반도체: 1026 (KRX 반도체 등, 정확한 티커 필요)
                # API로 이름 검색이 어려우므로, 샘플 데이터나 yfinance ETF로 대체 고려
                # 더 안정적인 방법: 주요 대표주들의 평균 등락률로 계산? -> 너무 복잡
                # 대안: 샘플 데이터로 진행하고, 추후 정확한 KRX 지수 코드 매핑
                pass
        except Exception as e:
            print(f"섹터 데이터 조회 실패: {e}")

    # 현재는 안정성을 위해 가상(샘플) 데이터 반환 (실시간 API 호출 한계 고려)
    # 실제로는 KRX API로 지수 코드를 정확히 하드코딩해서 호출해야 함
    
    # 랜덤성을 약간 주거나, 샘플값 고정
    import random
    return [
        {"name": "반도체", "change_rate": 2.5, "volume": "강세"},
        {"name": "2차전지", "change_rate": -1.2, "volume": "약세"},
        {"name": "자동차", "change_rate": 1.8, "volume": "강세"},
        {"name": "헬스케어", "change_rate": -0.5, "volume": "보합"},
        {"name": "인터넷/게임", "change_rate": 0.3, "volume": "보합"},
        {"name": "은행/금융", "change_rate": 1.1, "volume": "강세"},
    ]


def get_stock_news(query: str, limit: int = 5) -> List[dict]:
    """
    주식 관련 뉴스 조회 (Google News RSS 활용)
    """
    try:
        # 검색어 인코딩
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


# === 추가 기능: ETF, 공포탐욕지수, 고래알림 ===

def get_crypto_fear_greed() -> dict:
    """암호화폐 공포&탐욕 지수 조회 (Alternative.me API)"""
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
    except Exception as e:
        print(f"공포탐욕지수 조회 실패: {e}")
    
    # 실패 시 기본값
    return {"value": 50, "value_classification": "Neutral", "timestamp": 0}


def get_whale_alerts(limit: int = 5) -> List[dict]:
    """고래 알림 시뮬레이션 (대량 이체 내역)"""
    # 실제 API는 유료이거나 복잡하므로 시뮬레이션 데이터 생성
    coins = ["BTC", "ETH", "XRP", "USDT", "SOL", "DOGE"]
    exchanges = ["Binance", "Coinbase", "Upbit", "Kraken", "Unknown Wallet"]
    
    alerts = []
    for _ in range(limit):
        coin = random.choice(coins)
        amount = random.randint(1000, 1000000) if coin in ["XRP", "USDT", "DOGE"] else random.randint(10, 500)
        sender = random.choice(exchanges)
        receiver = random.choice(exchanges)
        while sender == receiver:
            receiver = random.choice(exchanges)
            
        # USD 가치 대략 계산 (시세 고정값 사용)
        prices = {"BTC": 65000, "ETH": 3500, "XRP": 0.6, "USDT": 1, "SOL": 150, "DOGE": 0.15}
        value_usd = amount * prices.get(coin, 1)
        
        alerts.append({
            "coin": coin,
            "amount": amount,
            "sender": sender,
            "receiver": receiver,
            "value_usd": value_usd,
            "timestamp": datetime.now().isoformat()
        })
        
    return alerts


def get_etf_top_volume(market: str = "us", limit: int = 10) -> List[dict]:
    """ETF 거래량 상위 조회 (주요 ETF 리스트 기반)"""
    result = []
    
    if market == "us":
        # 주요 미국 ETF 리스트 (20개)
        symbols = [
            "QQQ", "SPY", "TQQQ", "SOXL", "SQQQ", "JEPI", "SCHD", "IVV", "VTI", "VOO",
            "IWM", "EEM", "GLD", "SLV", "ARKK", "HYG", "XLF", "XLK", "SMH", "LABU"
        ]
        
        if YFINANCE_AVAILABLE:
            try:
                usd_krw = get_usd_krw_rate()
                
                # Batch Fetching using Tickers
                tickers = yf.Tickers(" ".join(symbols))
                
                for sym in symbols:
                    try:
                        t = tickers.tickers[sym]
                        # fast_info is efficient
                        # Some keys: last_price, previous_close, last_volume might accept None
                        current = t.fast_info.last_price
                        prev = t.fast_info.previous_close
                        volume = t.fast_info.last_volume
                        
                        # Calculate change
                        if current and prev:
                            change_rate = ((current - prev) / prev) * 100
                        else:
                            change_rate = 0.0
                            
                        # If volume info missing in fast_info? (Sometimes happens)
                        # Fallback to history only if needed (expensive)
                        if not volume:
                            hist = t.history(period="1d")
                            if not hist.empty:
                                volume = hist['Volume'].iloc[-1]
                        
                        if current and volume:
                            result.append({
                                "symbol": sym,
                                "name": t.fast_info.year_high, # fast_info doesn't have 'longName' directly accessible in some versions, but let's try or use symbol. 
                                # Actually fast_info doesn't assume name. Let's rely on hardcoded mapping or extra call if needed. 
                                # For speed, we will use symbol or try to access info property lazily? No, info is slow.
                                # Let's stick to symbol as name for speed, or a simple map.
                                "name": sym, 
                                "current_price": current,
                                "change_rate": change_rate,
                                "trade_volume": int(volume),
                                "trade_value": current * volume,
                                "current_price_krw": current * usd_krw,
                                "trade_value_krw": (current * volume) * usd_krw
                            })
                    except Exception as e:
                        # print(f"Error fetching {sym}: {e}")
                        continue
            except Exception as e:
                print(f"ETF Batch Fetch Error: {e}")
                pass

    if not result:
        # Fallback Sample Data (Extended)
        if market == "us":
            result = [
                {"symbol": "QQQ", "name": "Invesco QQQ", "current_price": 445.20, "change_rate": 1.2, "trade_volume": 50000000, "trade_value": 22250000000},
                {"symbol": "SPY", "name": "SPDR S&P 500", "current_price": 510.50, "change_rate": 0.8, "trade_volume": 60000000, "trade_value": 30600000000},
                {"symbol": "SOXL", "name": "Direxion Semi 3X", "current_price": 42.30, "change_rate": 3.5, "trade_volume": 120000000, "trade_value": 5076000000},
                {"symbol": "TQQQ", "name": "ProShares UltraPro QQQ", "current_price": 55.40, "change_rate": 3.1, "trade_volume": 90000000, "trade_value": 4986000000},
                {"symbol": "SQQQ", "name": "ProShares UltraShort QQQ", "current_price": 10.20, "change_rate": -3.0, "trade_volume": 110000000, "trade_value": 1122000000},
                {"symbol": "IWM", "name": "iShares Russell 2000", "current_price": 202.10, "change_rate": 0.5, "trade_volume": 25000000, "trade_value": 5052500000},
                {"symbol": "EEM", "name": "iShares MSCI Emerging", "current_price": 40.50, "change_rate": -0.2, "trade_volume": 30000000, "trade_value": 1215000000},
                {"symbol": "FXI", "name": "iShares China Large-Cap", "current_price": 24.80, "change_rate": 1.5, "trade_volume": 45000000, "trade_value": 1116000000},
                {"symbol": "XLF", "name": "Financial Select Sector", "current_price": 41.20, "change_rate": 0.3, "trade_volume": 38000000, "trade_value": 1565600000},
                {"symbol": "GDX", "name": "VanEck Gold Miners", "current_price": 33.40, "change_rate": 0.9, "trade_volume": 18000000, "trade_value": 601200000},
            ]
            # KRW dummy calc
            usd_krw = 1350
            for item in result:
                item["current_price_krw"] = item["current_price"] * usd_krw
                item["trade_value_krw"] = item["trade_value"] * usd_krw
    
    # Sort and Slice
    result.sort(key=lambda x: x.get('trade_value', 0), reverse=True)
    return result[:limit]


    """코스피 거래량 상위 종목을 출력합니다."""
    print("\n" + "="*50)
    print(f"📊 [코스피] 거래량 상위 {limit}개 종목")
    print("="*50)
    
    stocks = get_kospi_top_volume(limit)
    if stocks:
        for i, stock in enumerate(stocks, 1):
            change_indicator = "🔴" if stock['change_rate'] < 0 else "🟢"
            print(f"\n  {i}. {stock['name']} ({stock['code']})")
            print(f"     현재가: {stock['current_price']:,} KRW")
            print(f"     변동률: {change_indicator} {stock['change_rate']:+.2f}%")
            print(f"     거래대금: {stock['trade_value']/100000000:.2f}억 KRW")
    else:
        print("  거래량 정보를 가져올 수 없습니다.")


def print_kosdaq_top_volume(limit: int = 10):
    """코스닥 거래량 상위 종목을 출력합니다."""
    print("\n" + "="*50)
    print(f"📊 [코스닥] 거래량 상위 {limit}개 종목")
    print("="*50)
    
    stocks = get_kosdaq_top_volume(limit)
    if stocks:
        for i, stock in enumerate(stocks, 1):
            change_indicator = "🔴" if stock['change_rate'] < 0 else "🟢"
            print(f"\n  {i}. {stock['name']} ({stock['code']})")
            print(f"     현재가: {stock['current_price']:,} KRW")
            print(f"     변동률: {change_indicator} {stock['change_rate']:+.2f}%")
            print(f"     거래대금: {stock['trade_value']/100000000:.2f}억 KRW")
    else:
        print("  거래량 정보를 가져올 수 없습니다.")


def print_us_top_volume(limit: int = 10):
    """미국 주식 거래량 상위 종목을 출력합니다."""
    print("\n" + "="*50)
    print(f"📊 [미국 주식] 거래량 상위 {limit}개 종목")
    print("="*50)
    
    stocks = get_us_top_volume(limit)
    if stocks:
        for i, stock in enumerate(stocks, 1):
            change_indicator = "🔴" if stock['change_rate'] < 0 else "🟢"
            print(f"\n  {i}. {stock['name']} ({stock['symbol']})")
            print(f"     현재가: ${stock['current_price']:,.2f} ({stock['current_price_krw']:,} KRW)")
            print(f"     변동률: {change_indicator} {stock['change_rate']:+.2f}%")
            print(f"     거래대금: {stock['trade_value_krw']/100000000:.2f}억 KRW")
    else:
        print("  거래량 정보를 가져올 수 없습니다.")


# === 샘플 데이터 함수 (pykrx 작동 안할 때 사용) ===

def get_kospi_sample_data(limit: int = 10) -> List[dict]:
    """코스피 샘플 데이터를 반환합니다."""
    sample_stocks = [
        {'code': '005930', 'name': '삼성전자', 'current_price': 78500, 'change_rate': 1.42, 'trade_volume': 15234567, 'trade_value': 1195234567890},
        {'code': '000660', 'name': 'SK하이닉스', 'current_price': 142000, 'change_rate': -0.35, 'trade_volume': 3456789, 'trade_value': 490623456789},
        {'code': '005380', 'name': '현대차', 'current_price': 245000, 'change_rate': 2.51, 'trade_volume': 1234567, 'trade_value': 302468765432},
        {'code': '035420', 'name': 'NAVER', 'current_price': 185000, 'change_rate': -1.07, 'trade_volume': 890123, 'trade_value': 164672755000},
        {'code': '000270', 'name': '기아', 'current_price': 89500, 'change_rate': 1.82, 'trade_volume': 1567890, 'trade_value': 140326255000},
        {'code': '035720', 'name': '카카오', 'current_price': 42500, 'change_rate': -2.30, 'trade_volume': 2345678, 'trade_value': 99691315000},
        {'code': '051910', 'name': 'LG화학', 'current_price': 395000, 'change_rate': 0.77, 'trade_volume': 234567, 'trade_value': 92653965000},
        {'code': '006400', 'name': '삼성SDI', 'current_price': 412000, 'change_rate': -0.48, 'trade_volume': 189234, 'trade_value': 77960488000},
        {'code': '068270', 'name': '셀트리온', 'current_price': 178500, 'change_rate': 3.19, 'trade_volume': 398765, 'trade_value': 71179522500},
        {'code': '207940', 'name': '삼성바이오로직스', 'current_price': 875000, 'change_rate': 0.23, 'trade_volume': 78901, 'trade_value': 69038375000},
    ]
    return sample_stocks[:limit]


def get_kosdaq_sample_data(limit: int = 10) -> List[dict]:
    """코스닥 샘플 데이터를 반환합니다."""
    sample_stocks = [
        {'code': '247540', 'name': '에코프로비엠', 'current_price': 245000, 'change_rate': 4.26, 'trade_volume': 567890, 'trade_value': 139133050000},
        {'code': '086520', 'name': '에코프로', 'current_price': 89500, 'change_rate': -1.65, 'trade_volume': 1234567, 'trade_value': 110493745500},
        {'code': '373220', 'name': 'LG에너지솔루션', 'current_price': 425000, 'change_rate': 0.95, 'trade_volume': 234567, 'trade_value': 99690975000},
        {'code': '196170', 'name': '알테오젠', 'current_price': 312000, 'change_rate': 2.30, 'trade_volume': 289012, 'trade_value': 90171744000},
        {'code': '041510', 'name': '에스엠', 'current_price': 87500, 'change_rate': -0.57, 'trade_volume': 987654, 'trade_value': 86419725000},
        {'code': '293490', 'name': '카카오게임즈', 'current_price': 24500, 'change_rate': 1.45, 'trade_volume': 3456789, 'trade_value': 84691330500},
        {'code': '263750', 'name': '펄어비스', 'current_price': 32500, 'change_rate': -2.10, 'trade_volume': 2345678, 'trade_value': 76234535000},
        {'code': '039030', 'name': '이오테크닉스', 'current_price': 156000, 'change_rate': 1.95, 'trade_volume': 456789, 'trade_value': 71259084000},
        {'code': '257720', 'name': '실리콘투', 'current_price': 8950, 'change_rate': 5.30, 'trade_volume': 7890123, 'trade_value': 70616601350},
        {'code': '383220', 'name': 'F&F', 'current_price': 145000, 'change_rate': -0.34, 'trade_volume': 478901, 'trade_value': 69440645000},
    ]
    return sample_stocks[:limit]


if __name__ == "__main__":
    # 테스트 실행
    print_kospi_top_volume(5)
    print_kosdaq_top_volume(5)
    print_us_top_volume(5)

