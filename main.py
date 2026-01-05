"""
암호화폐 자동매매 프로그램 - 메인 모듈 (CLI)
업비트와 바이낸스 API를 통합하여 사용합니다.
Async refactored using anyio.run
"""
import anyio
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

# === Print Helper Functions (Restored/Adapted) ===

def print_upbit_balance():
    async def _run():
        balance = await get_upbit_balance()
        if balance:
            print("\n  [업비트 잔액]")
            print(f"  총 보유자산: {balance['total_krw']:.0f} KRW")
            print(f"  사용 가능: {balance['available_krw']:.0f} KRW")
        else:
            print("  잔액 정보를 가져올 수 없습니다.")
    anyio.run(_run)

def print_upbit_holdings():
    async def _run():
        holdings = await get_upbit_holdings()
        if holdings:
            print(f"\n  [보유 코인] 총 {len(holdings)}개")
            for item in holdings:
                print(f"  - {item['coin']}: {item['total']}개 (평가: {item['eval_amount']:.0f} KRW)")
        else:
            print("  보유 코인이 없거나 가져올 수 없습니다.")
    anyio.run(_run)

def print_upbit_top_volume(limit=10):
    async def _run():
        coins = await get_upbit_top_volume_coins(limit)
        if coins:
            print(f"\n  [업비트 거래량 Top {limit}]")
            for i, coin in enumerate(coins, 1):
                print(f"  {i}. {coin['name']} ({coin['market']}): {coin['current_price']:.0f} KRW")
        else:
            print("  정보를 가져올 수 없습니다.")
    anyio.run(_run)

def print_binance_balance():
    async def _run():
        balance = await get_binance_balance()
        if balance:
            print("\n  [바이낸스 잔액]")
            print(f"  총 보유: {balance['total_usdt']:.2f} USDT")
        else:
            print("  잔액 정보를 가져올 수 없습니다.")
    anyio.run(_run)

def print_binance_holdings():
    async def _run():
        holdings = await get_binance_holdings()
        if holdings:
            print(f"\n  [바이낸스 보유] 총 {len(holdings)}개")
            for item in holdings:
                print(f"  - {item['symbol']}: {item['total']} (평가: {item['eval_amount']:.2f} USDT)")
        else:
            print("  보유 코인이 없습니다.")
    anyio.run(_run)

def print_binance_top_volume(limit=10):
    async def _run():
        coins = await get_binance_top_volume_coins(limit)
        if coins:
            print(f"\n  [바이낸스 거래량 Top {limit}]")
            for i, coin in enumerate(coins, 1):
                print(f"  {i}. {coin['symbol']}: {coin['current_price']:.2f} USDT (Vol: {coin['quote_volume']:.0f})")
    anyio.run(_run)


def show_all_info():
    """모든 거래소의 정보를 한 번에 조회합니다."""
    print("\n" + "🚀" * 25)
    print("      암호화폐 포트폴리오 대시보드")
    print("🚀" * 25)
    
    # === 업비트 ===
    print("\n" + "─" * 50)
    print("                    📊 UPBIT")
    print("─" * 50)
    print_upbit_balance()
    print_upbit_holdings()
    print_upbit_top_volume(10)
    
    # === 바이낸스 ===
    print("\n" + "─" * 50)
    print("                   📊 BINANCE")
    print("─" * 50)
    print_binance_balance()
    print_binance_holdings()
    print_binance_top_volume(10)
    
    print("\n" + "🚀" * 25)
    print("              조회 완료!")
    print("🚀" * 25 + "\n")


def main():
    """메인 메뉴를 표시하고 사용자 입력을 처리합니다."""
    
    while True:
        print("\n" + "="*50)
        print("    🪙 암호화폐 자동매매 프로그램 🪙")
        print("="*50)
        print("\n  [거래소 선택]")
        print("  1. 업비트 (Upbit)")
        print("  2. 바이낸스 (Binance)")
        print("  3. 전체 조회")
        print("  0. 종료")
        
        choice = input("\n  선택: ").strip()
        
        if choice == "1":
            upbit_menu()
        elif choice == "2":
            binance_menu()
        elif choice == "3":
            show_all_info()
        elif choice == "0":
            print("\n  프로그램을 종료합니다. 👋\n")
            break
        else:
            print("\n  ⚠️ 올바른 번호를 선택해주세요.")


def upbit_menu():
    """업비트 메뉴"""
    while True:
        print("\n" + "="*50)
        print("    📊 업비트 (Upbit) 메뉴")
        print("="*50)
        print("\n  1. 잔액 조회")
        print("  2. 보유 코인 조회")
        print("  3. 거래량 상위 10개 코인")
        print("  4. 전체 조회")
        print("  0. 이전 메뉴")
        
        choice = input("\n  선택: ").strip()
        
        if choice == "1":
            print_upbit_balance()
        elif choice == "2":
            print_upbit_holdings()
        elif choice == "3":
            print_upbit_top_volume(10)
        elif choice == "4":
            print_upbit_balance()
            print_upbit_holdings()
            print_upbit_top_volume(10)
        elif choice == "0":
            break
        else:
            print("\n  ⚠️ 올바른 번호를 선택해주세요.")


def binance_menu():
    """바이낸스 메뉴"""
    while True:
        print("\n" + "="*50)
        print("    📊 바이낸스 (Binance) 메뉴")
        print("="*50)
        print("\n  1. 잔액 조회")
        print("  2. 보유 코인 조회")
        print("  3. 거래량 상위 10개 코인")
        print("  4. 전체 조회")
        print("  0. 이전 메뉴")
        
        choice = input("\n  선택: ").strip()
        
        if choice == "1":
            print_binance_balance()
        elif choice == "2":
            print_binance_holdings()
        elif choice == "3":
            print_binance_top_volume(10)
        elif choice == "4":
            print_binance_balance()
            print_binance_holdings()
            print_binance_top_volume(10)
        elif choice == "0":
            break
        else:
            print("\n  ⚠️ 올바른 번호를 선택해주세요.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  종료합니다.")
