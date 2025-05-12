
import sys
import os

from .data_api import ApiClient
import json
from datetime import datetime, timedelta

class YahooFinanceService:
    def __init__(self):
        self.client = ApiClient()

    # Uses Yahoo Finance API to get the latest stock price for a given symbol
    def get_latest_stock_price(self, symbol: str, region: str = "US"):
        """Fetches the latest stock price for a given symbol."""
        try:
            response = self.client.call_api(
                'YahooFinance/get_stock_chart',
                query={'symbol': symbol, 'region': region, 'interval': '1m', 'range': '1d'}
            )
            if response and response.get("chart") and response["chart"].get("result") and len(response["chart"]["result"]) > 0:
                meta = response["chart"]["result"][0].get("meta")
                if meta and "regularMarketPrice" in meta:
                    return meta["regularMarketPrice"]
                # Fallback if regularMarketPrice is not directly in meta, try to get the last close price
                elif response["chart"]["result"][0].get("indicators", {}).get("quote") and \
                     response["chart"]["result"][0]["indicators"]["quote"][0].get("close") and \
                     len(response["chart"]["result"][0]["indicators"]["quote"][0]["close"]) > 0:
                    # Get the last available close price from the series
                    close_prices = [p for p in response["chart"]["result"][0]["indicators"]["quote"][0]["close"] if p is not None]
                    if close_prices:
                        return close_prices[-1]
            return None # Or raise an error
        except Exception as e:
            print(f"Error fetching stock price for {symbol}: {e}")
            return None

    # Hardcoded placeholder data for MVP, can integrate with a Search API in the future
    # For MVP, we'll hardcode the data for each symbol, but this can be replaced with a more dynamic approach.
    def get_latest_announcements(self, symbol: str, region: str = "US"):
        """
        Generates a dictionary of placeholder company announcements and SEC filings.
        Includes various common scenarios.
        """
        announcements = {
            "significant_developments": [
            # Example: Meta-specific news
            {
                "related_symbol": "META",
                "headline": "Placeholder: Meta Continues Significant Investments in AI, Introduces New Language Model",
                "date": "2025-05-07", # Note: This date is fixed as per the user's example
                "summary": "Placeholder: Meta is heavily investing in artificial intelligence, increasing its capital expenditures to support its AI infrastructure and research efforts. The company recently launched its next-generation large language model with multimodal capabilities, aiming to enhance AI agents and competitive positioning in the generative AI space."
            },
            # Example: Tesla-specific news
            {
                "related_symbol": "TSLA",
                "headline": "Placeholder: Tesla Stock Soars 5%",
                "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                "summary": "Placeholder: Recent optimism was fueled by a major announcement impacting Tesla's global market exposure. Despite a rocky start to the year with recent disappointing earnings, investor sentiment has shifted positively, bolstered by confidence in the company's leadership."
            },
            # Example: Apple-specific news
            {
                "related_symbol": "AAPL",
                "headline": "Placeholder: Apple shares fall as CEO says ‘very difficult’ to predict tariff costs beyond June",
                "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                "summary": "Placeholder: The company expects tariffs to add significant costs for the current quarter, assuming no other major changes occur, the CEO said. The CEO told CNBC that Apple is already sourcing products for the U.S. from regions where tariffs are lower."
            },
            # Example: Google-specific news
            {
                "related_symbol": "GOOGL",
                "headline": "Placeholder: Alphabet shares drop sharply after Apple executive's testimony on Safari search",
                "date": "2025-05-07",
                "summary": "Placeholder: Shares of Alphabet, Google's parent company, fell significantly following testimony from an Apple executive who stated that Google's search traffic on Safari had declined and that Apple was exploring adding other AI search options to its browser. [2, 4, 5, 10, 11] This news raised concerns about potential challenges to Google's dominant search market position. [2, 5, 10]"
            }
            ],
            "financial_results": [ # Added a new category for financial news
                {
                    "headline": f"Placeholder: {symbol} Reports QX Financial Results",
                    "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                    "summary": f"{symbol} announced its financial results for the quarter ending {datetime.now() + timedelta(days=15)}, reporting strong revenue growth and solid earnings per share."
                },
                {
                    "headline": f"Placeholder: {symbol} Raises Full-Year Guidance",
                    "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    "summary": f"Following better-than-expected performance, {symbol} has raised its financial guidance for the full fiscal year."
                }
                # Add more financial results scenarios here
            ],
            "sec_filings": [
                {
                    "type": "8-K",
                    "title": f"Placeholder: Current report for {symbol}",
                    "filingDate": int((datetime.now() - timedelta(days=2)).timestamp()), 
                    "description": f"This is a placeholder 8-K filing for {symbol} regarding recent events such as a material agreement or management change."
                },
                {
                    "type": "10-Q", # Quarterly Report
                    "title": f"Placeholder: Quarterly report for {symbol}",
                    "filingDate": int((datetime.now() - timedelta(days=4)).timestamp()),
                    "description": f"This is a placeholder 10-Q filing for {symbol}, containing the company's unaudited financial results and related disclosures for the quarter."
                },
                {
                    "type": "10-K", # Annual Report
                    "title": f"Placeholder: Annual report for {symbol}",
                    "filingDate": int((datetime.now() - timedelta(days=30)).timestamp()), 
                    "description": f"This is a placeholder 10-K filing for {symbol}, containing the company's audited annual financial statements and comprehensive business report."
                },
                {
                    "type": "S-1", # Registration Statement (often for IPOs or new offerings)
                    "title": f"Placeholder: Registration Statement for {symbol}",
                    "filingDate": int((datetime.now() - timedelta(days=60)).timestamp()), 
                    "description": f"This is a placeholder S-1 filing for {symbol} regarding the registration of securities for a public offering."
                },
                {
                    "type": "4", # Statement of Changes in Beneficial Ownership (Insider Trading)
                    "title": f"Placeholder: Insider Trading Report for {symbol}",
                    "filingDate": int((datetime.now() - timedelta(days=1)).timestamp()),
                    "description": f"This is a placeholder Form 4 filing showing insider trading activity for {symbol}."
                }
                # Add more SEC filing scenarios here (hardcoded for MVP)
            ]
        }
        return announcements

    def get_stock_price_history(self, symbol: str, days: int = 14, region: str = "US"):
        """Fetches stock price history for the last N days."""
        try:
            response = self.client.call_api(
                'YahooFinance/get_stock_chart',
                query={'symbol': symbol, 'region': region, 'interval': '1d', 'range': '1mo', 'includeAdjustedClose': 'true'}
            )
            
            if response and response.get("chart") and response["chart"].get("result") and len(response["chart"]["result"]) > 0:
                chart_result = response["chart"]["result"][0]
                timestamps = chart_result.get("timestamp", [])
                indicators = chart_result.get("indicators", {})
                quote = indicators.get("quote", [{}])[0]
                adjclose = indicators.get("adjclose", [{}])[0].get("adjclose", []) if indicators.get("adjclose") else [] 

                if not (timestamps and quote.get("open") and quote.get("high") and quote.get("low") and quote.get("close") and quote.get("volume")):
                    return [] # Not enough data

                price_data = []
                
                num_entries = len(timestamps)
                start_index = max(0, num_entries - days)

                for i in range(start_index, num_entries):
                    dt_object = datetime.fromtimestamp(timestamps[i])
                    price_data.append({
                        "date": dt_object.strftime("%Y-%m-%d"),
                        "open": quote["open"][i],
                        "high": quote["high"][i],
                        "low": quote["low"][i],
                        "close": quote["close"][i],
                        "adj_close": adjclose[i] if i < len(adjclose) else quote["close"][i],
                        "volume": quote["volume"][i]
                    })
                return price_data
            return []
        except Exception as e:
            print(f"Error fetching stock price history for {symbol}: {e}")
            return []