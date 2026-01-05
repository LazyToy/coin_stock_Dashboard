"""
바이낸스(Binance) API 모듈
잔액 조회, 보유 코인 조회, 거래량 상위 코인 조회 기능 제공
"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
from typing import Optional
from config import BINANCE_ACCESS_KEY, BINANCE_SECRET_KEY, validate_binance_keys


def get_binance_client() -> Optional[Client]:
    """
    Binance 클라이언트를 생성하여 반환합니다.
    
    Returns:
        Client: Binance 클라이언트 객체 또는 None
    """
    if not validate_binance_keys():
        return None
    
    try:
        client = Client(BINANCE_ACCESS_KEY, BINANCE_SECRET_KEY)
        return client
    except Exception as e:
        print(f"❌ Binance 클라이언트 생성 실패: {e}")
        return None


def get_binance_balance() -> Optional[dict]:
    """
    바이낸스 계정의 총 잔액(USDT 기준)을 조회합니다.
    
    Returns:
        dict: USDT 잔액 정보 또는 None
            - total_usdt: 총 USDT
            - available_usdt: 사용 가능한 USDT
            - locked_usdt: 주문에 묶인 USDT
    """
    client = get_binance_client()
    if not client:
        return None
    
    try:
        account = client.get_account()
        balances = account['balances']
        
        usdt_balance = {
            "total_usdt": 0,
            "available_usdt": 0,
            "locked_usdt": 0
        }
        
        for balance in balances:
            if balance['asset'] == 'USDT':
                usdt_balance['available_usdt'] = float(balance['free'])
                usdt_balance['locked_usdt'] = float(balance['locked'])
                usdt_balance['total_usdt'] = usdt_balance['available_usdt'] + usdt_balance['locked_usdt']
                break
        
        return usdt_balance
    
    except BinanceAPIException as e:
        print(f"❌ 잔액 조회 실패 (API 오류): {e.message}")
        return None
    except Exception as e:
        print(f"❌ 잔액 조회 실패: {e}")
        return None


def get_binance_holdings() -> Optional[list]:
    """
    바이낸스 계정에서 보유 중인 코인 목록과 수량을 조회합니다.
    
    Returns:
        list: 보유 코인 정보 리스트 또는 None
            각 항목: {
                'asset': 코인 심볼,
                'free': 사용 가능 수량,
                'locked': 거래 중인 수량,
                'total': 총 보유 수량,
                'current_price': 현재가 (USDT),
                'eval_amount': 평가 금액 (USDT)
            }
    """
    client = get_binance_client()
    if not client:
        return None
    
    try:
        account = client.get_account()
        balances = account['balances']
        
        # 현재가 정보 조회
        all_tickers = client.get_all_tickers()
        price_map = {ticker['symbol']: float(ticker['price']) for ticker in all_tickers}
        
        holdings = []
        
        for balance in balances:
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            
            # 잔액이 0인 코인은 제외
            if total <= 0:
                continue
            
            # USDT 현재가 조회
            current_price = 0
            eval_amount = 0
            
            if asset == 'USDT':
                current_price = 1
                eval_amount = total
            else:
                symbol = f"{asset}USDT"
                if symbol in price_map:
                    current_price = price_map[symbol]
                    eval_amount = total * current_price
            
            holdings.append({
                'asset': asset,
                'free': free,
                'locked': locked,
                'total': total,
                'current_price': current_price,
                'eval_amount': eval_amount
            })
        
        # 평가 금액 기준 정렬
        holdings.sort(key=lambda x: x['eval_amount'], reverse=True)
        
        return holdings
    
    except BinanceAPIException as e:
        print(f"❌ 보유 코인 조회 실패 (API 오류): {e.message}")
        return None
    except Exception as e:
        print(f"❌ 보유 코인 조회 실패: {e}")
        return None


def get_binance_top_volume_coins(limit: int = 10) -> Optional[list]:
    """
    바이낸스에서 24시간 거래량 상위 코인을 조회합니다 (USDT 페어).
    
    Args:
        limit: 조회할 코인 수 (기본값: 10)
    
    Returns:
        list: 거래량 상위 코인 정보 리스트 또는 None
            각 항목: {
                'symbol': 심볼 (예: BTCUSDT),
                'base_asset': 기본 자산 (예: BTC),
                'quote_volume': 거래대금 (USDT),
                'volume': 거래량,
                'current_price': 현재가,
                'price_change_percent': 변동률(%)
            }
    """
    try:
        client = Client()  # 공개 API는 인증 없이 사용 가능
        
        # 24시간 티커 정보 조회
        tickers = client.get_ticker()
        
        # USDT 페어만 필터링
        usdt_tickers = [t for t in tickers if t['symbol'].endswith('USDT')]
        
        # 스테이블코인 및 레버리지 토큰 제외
        excluded_bases = ['BUSD', 'USDC', 'DAI', 'TUSD', 'PAX', 'USDP']
        filtered_tickers = []
        
        for t in usdt_tickers:
            symbol = t['symbol']
            base_asset = symbol.replace('USDT', '')
            
            # 레버리지 토큰 제외 (UP, DOWN, BULL, BEAR 등)
            if any(x in base_asset for x in ['UP', 'DOWN', 'BULL', 'BEAR', '3L', '3S']):
                continue
            
            # 스테이블코인 제외
            if base_asset in excluded_bases:
                continue
            
            filtered_tickers.append(t)
        
        # 거래대금(quoteVolume) 기준 정렬
        sorted_tickers = sorted(
            filtered_tickers, 
            key=lambda x: float(x['quoteVolume']), 
            reverse=True
        )
        
        result = []
        for ticker in sorted_tickers[:limit]:
            symbol = ticker['symbol']
            base_asset = symbol.replace('USDT', '')
            
            result.append({
                'symbol': symbol,
                'base_asset': base_asset,
                'quote_volume': float(ticker['quoteVolume']),
                'volume': float(ticker['volume']),
                'current_price': float(ticker['lastPrice']),
                'price_change_percent': float(ticker['priceChangePercent'])
            })
        
        return result
    
    except BinanceAPIException as e:
        print(f"❌ 거래량 상위 코인 조회 실패 (API 오류): {e.message}")
        return None
    except Exception as e:
        print(f"❌ 거래량 상위 코인 조회 실패: {e}")
        return None


# === 출력 헬퍼 함수 ===

def print_binance_balance():
    """바이낸스 USDT 잔액을 보기 좋게 출력합니다."""
    print("\n" + "="*50)
    print("💰 [바이낸스] USDT 잔액 조회")
    print("="*50)
    
    balance = get_binance_balance()
    if balance:
        print(f"  총 보유 USDT: {balance['total_usdt']:,.4f} USDT")
        print(f"  사용 가능:    {balance['available_usdt']:,.4f} USDT")
        print(f"  거래 중:      {balance['locked_usdt']:,.4f} USDT")
    else:
        print("  잔액 정보를 가져올 수 없습니다.")


def print_binance_holdings():
    """바이낸스 보유 코인을 보기 좋게 출력합니다."""
    print("\n" + "="*50)
    print("📦 [바이낸스] 보유 코인 목록")
    print("="*50)
    
    holdings = get_binance_holdings()
    if holdings:
        if len(holdings) == 0:
            print("  보유 중인 코인이 없습니다.")
        else:
            total_eval = 0
            for coin in holdings:
                print(f"\n  [{coin['asset']}]")
                print(f"    보유 수량: {coin['total']:.8f}")
                if coin['current_price'] > 0:
                    print(f"    현재가: {coin['current_price']:,.4f} USDT")
                    print(f"    평가 금액: {coin['eval_amount']:,.4f} USDT")
                    total_eval += coin['eval_amount']
                else:
                    print(f"    현재가: 조회 불가")
            
            print(f"\n  ─────────────────────────────")
            print(f"  💎 총 평가 금액: {total_eval:,.4f} USDT")
    else:
        print("  보유 코인 정보를 가져올 수 없습니다.")


def print_binance_top_volume(limit: int = 10):
    """바이낸스 거래량 상위 코인을 보기 좋게 출력합니다."""
    print("\n" + "="*50)
    print(f"🔥 [바이낸스] 거래량 상위 {limit}개 코인 (USDT 마켓)")
    print("="*50)
    
    top_coins = get_binance_top_volume_coins(limit)
    if top_coins:
        for i, coin in enumerate(top_coins, 1):
            change_indicator = "🔴" if coin['price_change_percent'] < 0 else "🟢"
            print(f"\n  {i}. {coin['base_asset']} ({coin['symbol']})")
            print(f"     현재가: {coin['current_price']:,.4f} USDT")
            print(f"     변동률: {change_indicator} {coin['price_change_percent']:+.2f}%")
            print(f"     거래대금: {coin['quote_volume']/1000000:,.2f}M USDT")
    else:
        print("  거래량 정보를 가져올 수 없습니다.")


if __name__ == "__main__":
    # 테스트 실행
    print_binance_balance()
    print_binance_holdings()
    print_binance_top_volume(10)
