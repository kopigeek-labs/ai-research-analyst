import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class OpenAIService:
    def __init__(self, api_key=None, model_name="gpt-4.1-nano"):
        """
        Initializes the OpenAI Service.
        Args:
            api_key (str, optional): OpenAI API key. If None, attempts to use OPENAI_API_KEY environment variable.
            model_name (str, optional): The OpenAI model to use (e.g. "gpt-4").
        """
        effective_api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        
        if not effective_api_key:
            print("Warning: OPENAI_API_KEY not found in environment or passed directly. "
                  "OpenAI functionality will be limited or fail.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=effective_api_key)
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.client = None
        
        self.model_name = model_name

    def _get_openai_response(self, system_prompt: str, user_prompt: str, is_json_response: bool = False):
        """
        Helper function to get a response from the OpenAI Chat Completions API.
        """
        if not self.client:
            error_msg = "OpenAI client not initialized. Cannot make API call."
            print(error_msg)
            if is_json_response:
                return None
            return error_msg

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            completion_params = {
                "model": self.model_name,
                "messages": messages,
            }

            # Enable JSON mode or Structured Output mode
            if is_json_response:
                completion_params["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**completion_params)
            
            content = response.choices[0].message.content
            if is_json_response:
                # If json_object mode was successful, OpenAI outputs valid JSON.
                # If not, parse manually and handle errors.
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from OpenAI response: {e}. Response content: {content}")
                    return None # Or a default error JSON structure
            return content
        except Exception as e:
            print(f"Error getting response from OpenAI: {e}")
            if is_json_response:
                return None 
            return f"Error communicating with OpenAI: {e}"

    # Guardrail to identify only relevant intent
    def parse_query(self, query: str):
        """Uses OpenAI to parse the user's query to extract intent and entities."""
        system_prompt = """
            You are an AI assistant helping to parse user queries for a financial research tool.
            Identify the company name (or symbol if provided) and the user's intent.
            The intent should be one of: 'get_stock_price', 'get_latest_announcements', 'get_stock_movement_reasons'.
            If a company name is identified, also provide its common stock ticker symbol if known (e.g., Apple Inc. -> AAPL, Microsoft -> MSFT, Tesla -> TSLA, Meta -> META, Google -> GOOGL or GOOG).
            If a ticker symbol is directly provided, use that as the symbol.
            Return the response strictly as a JSON object with keys 'company_name', 'symbol', and 'intent'.
            If a company name cannot be reliably identified, return null for company_name and symbol.
            If the intent cannot be reliably identified, return null for intent.
            Your output MUST be a valid JSON object.
            """
        user_prompt = f"User Query: \"{query}\""
        
        parsed_response = self._get_openai_response(system_prompt, user_prompt, is_json_response=True)
        
        if parsed_response and isinstance(parsed_response, dict):
            return parsed_response
        else:
            print(f"Failed to get valid JSON parsed response for query: {query}")
            return {"company_name": None, "symbol": None, "intent": None}

    # Integrate with Yahoo Finance to get price_history
    def analyze_stock_movement_reasons(self, symbol: str, price_history: list, announcements: dict, news_articles: list):
        """Analyzes provided data to suggest reasons for stock price movements using OpenAI."""
        system_prompt = f"""
            You are an AI Investment Research Assistant. Your task is to analyze the provided data for {symbol} 
            and explain its stock price movements over the recent period covered by the price history (typically the last 2 weeks).
            """
        user_prompt = f"""
            Analyze the following data for {symbol}:
            Price History (Date, Open, High, Low, Close, Adjusted Close, Volume):
            {json.dumps(price_history, indent=2)}

            Recent Announcements (Significant Developments & SEC Filings):
            Significant Developments: {json.dumps(announcements.get('significant_developments', []), indent=2)}
            SEC Filings: {json.dumps(announcements.get('sec_filings', []), indent=2)}

            Recent News Articles (Headlines and Snippets):
            {json.dumps(news_articles, indent=2)}

            Based on this information, provide a concise analysis of the key reasons for {symbol}'s stock price movements. 
            Identify any significant price changes and correlate them with specific announcements, news, or market events if possible.
            Focus on the last 2 weeks as reflected in the price history.
            Present the analysis in a clear, narrative format.
            """

        analysis = self._get_openai_response(system_prompt, user_prompt)
        return analysis if analysis else "Could not analyze stock movement reasons due to an error with OpenAI."

    # Currently hardcoded for the MVP
    def generate_announcement_summary(self, symbol: str, announcements: dict, news_articles: list):
        """Generates a summary of latest announcements and news using OpenAI."""
        system_prompt = f"""
        You are an AI Investment Research Assistant. Your task is to summarize the latest announcements and relevant news for {symbol}.
        """
        
        user_prompt = f"""
        Summarize the latest announcements and relevant news for {symbol}.
        
        Announcements Data:
        Significant Developments: {json.dumps(announcements.get('significant_developments', []), indent=2)}
        SEC Filings: {json.dumps(announcements.get('sec_filings', []), indent=2)}

        Recent News Articles (Headlines and Snippets):
        {json.dumps(news_articles, indent=2)}

        Provide a concise summary of the most important and recent items. Focus on information relevant to an investment professional.
        Present the summary in a clear, narrative format.
        """
        
        summary = self._get_openai_response(system_prompt, user_prompt)
        return summary if summary else "Could not generate announcement summary due to an error with OpenAI."

# # Hardcoded Inputs for Testing only
# if __name__ == "__main__":
#     if not os.getenv("OPENAI_API_KEY"):
#         print("Skipping OpenAIService example: OPENAI_API_KEY not set in environment.")
#     else:
#         # Example: openai_service = OpenAIService(model_name="gpt-4-turbo-preview")
#         openai_service = OpenAIService() 

#         if not openai_service.client:
#             print("OpenAI client not properly initialized. Exiting example.")
#         else:
#             print(f"Using OpenAI model: {openai_service.model_name}")
#             # Test query parsing
#             print("\n--- Query Parsing (OpenAI) ---")
#             queries = [
#                 "What is the latest stock price for Apple?",
#                 "What are the latest related announcements for META?",
#                 "Why did Tesla's stock go up recently?",
#                 "Tell me about Google's financials" # Might not map to a defined intent
#             ]
#             for q in queries:
#                 parsed = openai_service.parse_query(q)
#                 print(f"Query: {q}\nParsed: {json.dumps(parsed, indent=2)}\n")

#             # Test announcement summary (dummy data)
#             print("--- Announcement Summary (OpenAI) ---")
#             dummy_symbol = "ANYCO"
#             dummy_announcements = {
#                 "significant_developments": [{"headline": f"New AI Chip Unveiled by {dummy_symbol}", "date": "2025-07-15"}],
#                 "sec_filings": [{"type": "10-Q", "title": "Quarterly Report", "filingDate": "2025-07-01"}]
#             }
#             dummy_news = [
#                 {"title": f"{dummy_symbol} stock surges on AI chip news", "snippet": f"Analysts are bullish on {dummy_symbol}'s new technology..."},
#                 {"title": f"Market Outlook: Tech stocks rally, {dummy_symbol} leads", "snippet": "Positive sentiment in the tech sector..."}
#             ]
#             summary = openai_service.generate_announcement_summary(dummy_symbol, dummy_announcements, dummy_news)
#             print(f"Summary for {dummy_symbol}:\n{summary}\n")

#             # Test stock movement analysis (dummy data)
#             print("--- Stock Movement Analysis (OpenAI) ---")
#             dummy_price_history = [
#                 {"date": "2025-07-01", "close": 200.00, "volume": 1000000},
#                 {"date": "2025-07-08", "close": 205.00, "volume": 1200000},
#                 {"date": "2025-07-15", "close": 220.00, "volume": 2500000} # Corresponds with chip news
#             ]
#             analysis = openai_service.analyze_stock_movement_reasons(dummy_symbol, dummy_price_history, dummy_announcements, dummy_news)
#             print(f"Analysis for {dummy_symbol}:\n{analysis}")