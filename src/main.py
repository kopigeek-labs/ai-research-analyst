import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, request, jsonify, render_template

# Services are in a 'services' subdirectory within 'src'
from services.yahoo_finance_service import YahooFinanceService
from services.openai_service import OpenAIService

# Initialize Flask App
app = Flask(__name__, static_folder='static', template_folder='static')

# Initialize YAHOO API Services
yf_service = YahooFinanceService()

# Initialize OPENAI API Service
openai_service = None
OPENAI_API_KEY_ERROR = None

try:
    if not os.getenv("OPENAI_API_KEY"):
        OPENAI_API_KEY_ERROR = "OPENAI_API_KEY environment variable not set. Please set the key in .ENV"
        print(f"Warning: {OPENAI_API_KEY_ERROR}")
    openai_service = OpenAIService() 

except Exception as e:
    OPENAI_API_KEY_ERROR = f"Error initializing OpenAI API: {e}. Please check your API key."
    print(OPENAI_API_KEY_ERROR)

# Helper to get web search results (simulated here, will use actual tool in post MVP development)
def search_web_for_company_news(company_name_or_symbol, time_period_prompt="last 2 weeks"):
    """Use Search API to get company latest news."""
    
    print(f"[Placeholder] Searching web for: {company_name_or_symbol} news {time_period_prompt}")
    # Simulate some news findings for now for MVP
    return [
        {"title": f"News about {company_name_or_symbol} 1", "snippet": f"Details about {company_name_or_symbol} event A..."},
        {"title": f"Market reacts to {company_name_or_symbol} update", "snippet": f"Analysts discuss {company_name_or_symbol}"}
    ]

@app.route('/')
def index():
    return render_template('index.html', api_key_error=OPENAI_API_KEY_ERROR) # Pass OpenAI error

@app.route('/ask', methods=['POST'])
def ask_assistant():
    if not openai_service or not openai_service.client: # Check if openai_service and its client are initialized
        return jsonify({"error": f"OpenAI Service is not available. {OPENAI_API_KEY_ERROR if OPENAI_API_KEY_ERROR else 'Unknown initialization error.'}"}), 500
        
    user_query = request.form.get('query')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    # 1. Parse Query using OpenAI
    company_symbol = None
    intent = None
    
    # Use OpenAI to parse company and query intent of the user
    parsed_info = openai_service.parse_query(user_query)
    company_name = parsed_info.get("company_name")
    company_symbol = parsed_info.get("symbol")
    intent = parsed_info.get("intent")

    if not company_symbol and company_name:
        print(f"OpenAI identified company: {company_name}, but no symbol. Attempting to proceed if intent is general.")

    if not intent:
        return jsonify({'error': 'Could not understand the intent of your query. Please try rephrasing.'}), 400
    
    # Ensure symbol is present for most intents.
    if intent in ['get_stock_price', 'get_latest_announcements', 'get_stock_movement_reasons'] and not company_symbol:
         return jsonify({'error': f'Could not identify a stock symbol for "{company_name if company_name else user_query}". Please specify a known symbol like AAPL, MSFT, etc.'}), 400

    # 2. Process based on intent
    response_data = ""

    if intent == 'get_stock_price':
        if not company_symbol: # Redundant check if above condition is strict, but good for clarity
             return jsonify({'error': f'Could not identify a stock symbol for your query about stock price. Please specify a known symbol.'}), 400
        price = yf_service.get_latest_stock_price(company_symbol)
        if price is not None:
            response_data = f"The latest stock price for {company_symbol} is ${price:.2f}."
        else:
            response_data = f"Could not retrieve the latest stock price for {company_symbol}."

    elif intent == 'get_latest_announcements':
        if not company_symbol:
             return jsonify({'error': f'Could not identify a stock symbol for your query about announcements. Please specify a known symbol.'}), 400
        announcements_data = yf_service.get_latest_announcements(company_symbol)
        web_news = search_web_for_company_news(company_symbol, "latest") 
        response_data = openai_service.generate_announcement_summary(company_symbol, announcements_data, web_news)

    elif intent == 'get_stock_movement_reasons':
        if not company_symbol:
             return jsonify({'error': f'Could not identify a stock symbol for your query about stock movements. Please specify a known symbol.'}), 400
        price_history = yf_service.get_stock_price_history(company_symbol, days=14)
        announcements_data = yf_service.get_latest_announcements(company_symbol)
        web_news = search_web_for_company_news(company_symbol, "last 2 weeks") 
        response_data = openai_service.analyze_stock_movement_reasons(company_symbol, price_history, announcements_data, web_news)

    else:
        response_data = "I can help with finding the latest stock price, latest announcements, or reasons for stock price movements for US-listed companies."

    return jsonify({'response': response_data})

if __name__ == '__main__':
    # Port 5000 is default for Flask. Ensure it's not in use or choose another like 5001
    app.run(host='0.0.0.0', port=5001, debug=True)

