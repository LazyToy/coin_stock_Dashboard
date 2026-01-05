"""
환경 설정 모듈
.env 파일에서 API 키를 로드합니다.
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Upbit API 설정
UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")

# Binance API 설정
BINANCE_ACCESS_KEY = os.getenv("BINANCE_ACCESS_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")


def validate_upbit_keys() -> bool:
    """Upbit API 키가 설정되어 있는지 확인합니다."""
    if not UPBIT_ACCESS_KEY or not UPBIT_SECRET_KEY:
        print("❌ Upbit API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return False
    return True


def validate_binance_keys() -> bool:
    """Binance API 키가 설정되어 있는지 확인합니다."""
    if not BINANCE_ACCESS_KEY or not BINANCE_SECRET_KEY:
        print("❌ Binance API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return False
    return True
