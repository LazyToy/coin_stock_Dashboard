import yfinance as yf

def test_fast_info(symbol):
    print(f"Fetching fast_info for {symbol}...")
    try:
        t = yf.Ticker(symbol)
        # fast_info doesn't use dict access, it has attributes
        # keys like 'currency', 'exchange', 'quoteType', 'last_price'
        # Does it have name?
        # Let's verify dir()
        print(t.fast_info.keys()) 
        # But fast_info is lazy. Attributes are only loaded when accessed?
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fast_info("NVDA")
