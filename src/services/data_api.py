import yfinance as yf

class ApiClient:
    def call_api(self, endpoint: str, query: dict):
        symbol = query.get('symbol')
        region = query.get('region', 'US')
        interval = query.get('interval', '1d')
        range_ = query.get('range', '1mo')

        ticker = yf.Ticker(symbol)

        if endpoint == 'YahooFinance/get_stock_chart':
            # Fetch historical market data
            data = ticker.history(period=range_, interval=interval)
            if data.empty:
                return None

            # Prepare response similar to Yahoo Finance API structure
            timestamps = [int(ts.timestamp()) for ts in data.index]
            indicators = {
                "quote": [{
                    "open": data['Open'].tolist(),
                    "high": data['High'].tolist(),
                    "low": data['Low'].tolist(),
                    "close": data['Close'].tolist(),
                    "volume": data['Volume'].tolist()
                }]
            }

            response = {
                "chart": {
                    "result": [{
                        "meta": {
                            "regularMarketPrice": data['Close'][-1]
                        },
                        "timestamp": timestamps,
                        "indicators": indicators
                    }]
                }
            }
            return response

        elif endpoint == 'YahooFinance/get_stock_insights':
            # yfinance does not provide stock insights directly; hardcode this for MVP
            return {
                "finance": {
                    "result": {
                        "sigDevs": []
                    }
                }
            }

        elif endpoint == 'YahooFinance/get_stock_sec_filing':
            # yfinance does not provide stock filing data directly; hardcode this for MVP
            return {
                "quoteSummary": {
                    "result": [{
                        "secFilings": {
                            "filings": []
                        }
                    }]
                }
            }

        else:
            raise ValueError(f"Unsupported endpoint: {endpoint}")
