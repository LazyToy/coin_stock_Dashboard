"""
업비트(Upbit) API 모듈
잔액 조회, 보유 코인 조회, 거래량 상위 코인 조회 기능 제공
"""
import pyupbit
from typing import Optional
from config import UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, validate_upbit_keys


def get_upbit_client() -> Optional[pyupbit.Upbit]:
    """
    Upbit 클라이언트를 생성하여 반환합니다.
    
    Returns:
        pyupbit.Upbit: Upbit 클라이언트 객체 또는 None
    """
    if not validate_upbit_keys():
        return None
    
    try:
        upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
        return upbit
    except Exception as e:
        print(f"❌ Upbit 클라이언트 생성 실패: {e}")
        return None


def get_upbit_balance() -> Optional[dict]:
    """
    업비트 계정의 총 잔액(원화 기준)을 조회합니다.
    
    Returns:
        dict: 총 KRW 잔액 정보 또는 None
            - total_krw: 보유 원화
            - available_krw: 사용 가능한 원화
            - locked_krw: 주문에 묶인 원화
    """
    upbit = get_upbit_client()
    if not upbit:
        return None
    
    try:
        balances = upbit.get_balances()
        
        # KRW 잔액 찾기
        krw_balance = {
            "total_krw": 0,
            "available_krw": 0,
            "locked_krw": 0
        }
        
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


def get_upbit_holdings() -> Optional[list]:
    """
    업비트 계정에서 보유 중인 코인 목록과 수량을 조회합니다.
    
    Returns:
        list: 보유 코인 정보 리스트 또는 None
            각 항목: {
                'currency': 코인 심볼,
                'balance': 보유 수량,
                'locked': 거래 중인 수량,
                'avg_buy_price': 평균 매수가,
                'current_price': 현재가,
                'eval_amount': 평가 금액,
                'profit_rate': 수익률(%)
            }
    """
    upbit = get_upbit_client()
    if not upbit:
        return None
    
    try:
        balances = upbit.get_balances()
        holdings = []
        
        for balance in balances:
            currency = balance['currency']
            
            # KRW는 제외 (원화는 코인이 아님)
            if currency == 'KRW':
                continue
            
            total_balance = float(balance['balance']) + float(balance['locked'])
            
            # 잔액이 0인 코인은 제외
            if total_balance <= 0:
                continue
            
            # 현재가 조회
            ticker = f"KRW-{currency}"
            try:
                current_price = pyupbit.get_current_price(ticker)
            except:
                current_price = 0
            
            avg_buy_price = float(balance['avg_buy_price'])
            eval_amount = total_balance * current_price if current_price else 0
            
            # 수익률 계산
            profit_rate = 0
            if avg_buy_price > 0 and current_price:
                profit_rate = ((current_price - avg_buy_price) / avg_buy_price) * 100
            
            holdings.append({
                'currency': currency,
                'balance': float(balance['balance']),
                'locked': float(balance['locked']),
                'total': total_balance,
                'avg_buy_price': avg_buy_price,
                'current_price': current_price,
                'eval_amount': eval_amount,
                'profit_rate': round(profit_rate, 2)
            })
        
        return holdings
    
    except Exception as e:
        print(f"❌ 보유 코인 조회 실패: {e}")
        return None


def get_upbit_top_volume_coins(limit: int = 10) -> Optional[list]:
    """
    업비트에서 금일 거래량 상위 코인을 조회합니다.
    
    Args:
        limit: 조회할 코인 수 (기본값: 10)
    
    Returns:
        list: 거래량 상위 코인 정보 리스트 또는 None
            각 항목: {
                'market': 마켓명 (예: KRW-BTC),
                'korean_name': 한글명,
                'english_name': 영문명,
                'trade_volume': 거래량,
                'trade_price': 거래대금,
                'current_price': 현재가,
                'change_rate': 변동률(%)
            }
    """
    try:
        # 모든 KRW 마켓 조회
        tickers = pyupbit.get_tickers(fiat="KRW")
        
        if not tickers:
            print("❌ 마켓 정보를 가져올 수 없습니다.")
            return None
        
        # 티커 정보 조회 (현재가, 거래량 등)
        ticker_info = pyupbit.get_current_price(tickers)
        
        # 상세 정보 조회
        import requests
        url = "https://api.upbit.com/v1/ticker"
        params = {"markets": ",".join(tickers)}
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"❌ API 요청 실패: {response.status_code}")
            return None
        
        data = response.json()
        
        # 마켓 이름 정보 가져오기
        market_info_url = "https://api.upbit.com/v1/market/all"
        market_response = requests.get(market_info_url)
        market_names = {}
        
        if market_response.status_code == 200:
            for item in market_response.json():
                market_names[item['market']] = {
                    'korean_name': item.get('korean_name', ''),
                    'english_name': item.get('english_name', '')
                }
        
        # 거래대금 기준으로 정렬
        sorted_data = sorted(data, key=lambda x: x['acc_trade_price_24h'], reverse=True)
        
        result = []
        for item in sorted_data[:limit]:
            market = item['market']
            names = market_names.get(market, {'korean_name': '', 'english_name': ''})
            
            result.append({
                'market': market,
                'korean_name': names['korean_name'],
                'english_name': names['english_name'],
                'trade_volume': item['acc_trade_volume_24h'],
                'trade_price': item['acc_trade_price_24h'],
                'current_price': item['trade_price'],
                'change_rate': round(item['signed_change_rate'] * 100, 2)
            })
        
        return result
    
    except Exception as e:
        print(f"❌ 거래량 상위 코인 조회 실패: {e}")
        return None


# === 출력 헬퍼 함수 ===

def print_upbit_balance():
    """업비트 잔액을 보기 좋게 출력합니다."""
    print("\n" + "="*50)
    print("💰 [업비트] 원화(KRW) 잔액 조회")
    print("="*50)
    
    balance = get_upbit_balance()
    if balance:
        print(f"  총 보유 원화: {balance['total_krw']:,.0f} KRW")
        print(f"  사용 가능:    {balance['available_krw']:,.0f} KRW")
        print(f"  거래 중:      {balance['locked_krw']:,.0f} KRW")
    else:
        print("  잔액 정보를 가져올 수 없습니다.")


def print_upbit_holdings():
    """업비트 보유 코인을 보기 좋게 출력합니다."""
    print("\n" + "="*50)
    print("📦 [업비트] 보유 코인 목록")
    print("="*50)
    
    holdings = get_upbit_holdings()
    if holdings:
        if len(holdings) == 0:
            print("  보유 중인 코인이 없습니다.")
        else:
            total_eval = 0
            for coin in holdings:
                profit_indicator = "📈" if coin['profit_rate'] >= 0 else "📉"
                print(f"\n  [{coin['currency']}]")
                print(f"    보유 수량: {coin['total']:.8f}")
                print(f"    평균 매수가: {coin['avg_buy_price']:,.0f} KRW")
                print(f"    현재가: {coin['current_price']:,.0f} KRW")
                print(f"    평가 금액: {coin['eval_amount']:,.0f} KRW")
                print(f"    수익률: {profit_indicator} {coin['profit_rate']:+.2f}%")
                total_eval += coin['eval_amount']
            
            print(f"\n  ─────────────────────────────")
            print(f"  💎 총 평가 금액: {total_eval:,.0f} KRW")
    else:
        print("  보유 코인 정보를 가져올 수 없습니다.")


def print_upbit_top_volume(limit: int = 10):
    """업비트 거래량 상위 코인을 보기 좋게 출력합니다."""
    print("\n" + "="*50)
    print(f"🔥 [업비트] 거래량 상위 {limit}개 코인")
    print("="*50)
    
    top_coins = get_upbit_top_volume_coins(limit)
    if top_coins:
        for i, coin in enumerate(top_coins, 1):
            change_indicator = "🔴" if coin['change_rate'] < 0 else "🟢"
            print(f"\n  {i}. {coin['korean_name']} ({coin['market']})")
            print(f"     현재가: {coin['current_price']:,.0f} KRW")
            print(f"     변동률: {change_indicator} {coin['change_rate']:+.2f}%")
            print(f"     거래대금: {coin['trade_price']/100000000:,.2f}억 KRW")
    else:
        print("  거래량 정보를 가져올 수 없습니다.")


if __name__ == "__main__":
    # 테스트 실행
    print_upbit_balance()
    print_upbit_holdings()
    print_upbit_top_volume(10)
