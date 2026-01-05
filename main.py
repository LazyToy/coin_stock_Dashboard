"""
암호화폐 자동매매 프로그램 - 메인 모듈
업비트와 바이낸스 API를 통합하여 사용합니다.
"""

from upbit_api import (
    get_upbit_balance,
    get_upbit_holdings,
    get_upbit_top_volume_coins,
    print_upbit_balance,
    print_upbit_holdings,
    print_upbit_top_volume
)

from binance_api import (
    get_binance_balance,
    get_binance_holdings,
    get_binance_top_volume_coins,
    print_binance_balance,
    print_binance_holdings,
    print_binance_top_volume
)


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
    main()
