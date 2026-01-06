import yfinance as yf

def test_name(symbol):
    print(f"Fetching info for {symbol}...")
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        short = info.get('shortName')
        long_n = info.get('longName')
        print(f"Symbol: {symbol}")
        print(f"Short Name: {short}")
        print(f"Long Name: {long_n}")
    except Exception as e:
        print(f"Error: {e}")

test_name("NVDA")
test_name("AAPL")
