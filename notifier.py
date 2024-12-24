import requests
import schedule
import time
from twilio.rest import Client
import sys

# Configuration
STOCK_API_URL = "https://www.alphavantage.co/query"
NEWS_API_URL = "https://newsapi.org/v2/everything"
STOCK_API_KEY = "S17JQF9E6RVHEL5R"  # Alpha Vantage API Key
NEWS_API_KEY = "01c5fa7dc0674e87a21636bbf0712828"  # NewsAPI Key
TWILIO_ACCOUNT_SID = "ACd5ef32040e44f2a2f177a91656106a3a"  # Twilio Account SID
TWILIO_AUTH_TOKEN = "c5f2e737dd6df23e5dee689b68e8dcc6"  # Twilio Auth Token
TWILIO_PHONE_NUMBER = "whatsapp:+14155238886"  # Twilio WhatsApp Sandbox Number

# Global variable to store the last sent news
last_news_sent = ""

# Buzzwords to filter relevant news


BUZZWORDS = {
    # Corporate Actions
    "acquisition", "merger", "bought", "sold", "partnership", "deal", "divestiture",
    "buyback", "takeover", "spin-off", "spinoff", "IPO", "exit", "dividend", "split", "valuation",
    "buyout", "rebranding", "launch", "expansion", "hiring", "layoffs", "closure", "shutdown",
    "new product", "product recall", "keynote", "conference", "announcement", "restructure",

    # Financial Performance
    "earnings", "revenue", "profit", "loss", "guidance", "forecast", "downgrade", "upgrade",
    "rating", "growth", "decline", "margin", "cash flow", "quarterly results", "annual results",
    "earnings surprise", "unexpected loss", "price target", "cost reduction", "cost-cutting",

    # Regulatory/Legal
    "lawsuit", "settlement", "fine", "sanction", "antitrust", "monopoly", "regulation", "compliance",
    "approval", "rejection", "intellectual property", "patent", "licensing", "royalties",
    "insider trading", "tax", "policy", "tariff", "probe", "inquiry", "investigation", "scandal",

    # Economic Indicators
    "inflation", "interest rates", "GDP", "recession", "economic slowdown", "stimulus", "trade war",
    "currency", "export", "import", "federal reserve", "central bank", "market collapse", "market rally",
    "global market", "sector performance", "volatility", "price movement", "supply chain",

    # Market/Investor Behavior
    "activist investor", "proxy", "shareholder", "hedge fund", "venture capital", "ETF", "short squeeze",
    "stock split", "reverse split", "block trade", "insider sale", "insider purchase", "volume spike",
    "options activity", "institutional buying", "institutional selling",

    # Technology and Innovation
    "technology", "AI", "automation", "machine learning", "cyberattack", "data breach", "hack",
    "innovation", "breakthrough", "automation", "security vulnerability", "software update", "bug",
    "product failure", "outage", "cloud computing", "blockchain", "metaverse", "quantum computing",

    # Environmental and Social
    "sustainability", "carbon", "climate", "green", "renewable", "ESG", "environmental compliance",
    "labor strike", "union", "boycott", "diversity", "inclusivity", "community impact", "social responsibility",

    # Industry Trends and Competitors
    "competition", "market share", "new entrant", "disruption", "monopoly", "oligopoly", "sector growth",
    "sector decline", "industry consolidation", "supply", "demand", "shortage", "surplus", "logistics",
    "production", "manufacturing", "backorder", "overstock", "pricing strategy",

    # Crisis and Risk
    "bankruptcy", "fraud", "scandal", "penalty", "disruption", "security breach", "natural disaster",
    "geopolitical risk", "war", "pandemic", "epidemic", "market crash", "debt default", "credit risk",
    "delisting", "non-compliance", "whistleblower", "termination", "recall", "executive departure",

    # Leadership and Strategy
    "CEO", "CFO", "chairman", "board", "executive change", "strategy shift", "leadership change",
    "resignation", "promotion", "succession planning", "management restructuring",

    # Macroeconomic and Geopolitical
    "oil prices", "commodity prices", "interest rate hike", "rate cut", "sanctions", "geopolitical tension",
    "government funding", "federal aid", "policy change", "stimulus package", "tax reform", "trade agreement",
    "export restrictions", "import tariffs", "foreign investment",

    # Miscellaneous
    "milestone", "legal victory", "legal defeat", "cyclical trend", "seasonal trend", "market sentiment",
    "headline risk", "recovery", "slowdown", "competitor failure", "sector rotation", "market anomaly",
    "currency fluctuation", "exchange rate", "diversification", "digital transformation", "remote work"
}



# Accept phone number and stock symbol as command-line arguments
if len(sys.argv) != 3:
    print("Usage: python3 notifier.py <phone_number> <stock_symbol>")
    sys.exit(1)

PHONE_NUMBER = sys.argv[1]
STOCK_SYMBOL = sys.argv[2]

# Function to fetch stock data
def fetch_stock_data():
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": STOCK_SYMBOL,
        "interval": "1min",
        "apikey": STOCK_API_KEY
    }
    response = requests.get(STOCK_API_URL, params=params)
    data = response.json()
    try:
        latest_time = list(data["Time Series (1min)"].keys())[0]
        latest_data = data["Time Series (1min)"][latest_time]
        return f"{STOCK_SYMBOL} Stock Update:\nTime: {latest_time}\nPrice: {latest_data['1. open']} USD"
    except KeyError:
        return None  # No stock data available

# Function to fetch news related to the stock
def fetch_stock_news():
    global last_news_sent
    params = {
        "q": STOCK_SYMBOL,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "pageSize": 10
    }
    response = requests.get(NEWS_API_URL, params=params)
    articles = response.json().get("articles", [])
    relevant_articles = [
        f"- {article['title']} (Read more: {article['url']})"
        for article in articles
        if any(buzzword in article.get("title", "").lower() for buzzword in BUZZWORDS)
    ]

    if relevant_articles:
        news = "\n".join(relevant_articles)
        if news == last_news_sent:
            return None  # No new updates
        last_news_sent = news
        return f"Latest News on {STOCK_SYMBOL}:\n{news}"
    return None  # No relevant news found

# Function to send WhatsApp message using Twilio
def send_whatsapp_message(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=f"whatsapp:{PHONE_NUMBER}"
        )
        print(f"Message sent to {PHONE_NUMBER}")
    except Exception as e:
        print(f"Error: {e}")

# Notify function
def check_and_notify():
    stock_message = fetch_stock_data()
    news_message = fetch_stock_news()

    # Only send a message if there is relevant stock data or news
    if stock_message and news_message:
        final_message = f"{stock_message}\n\n{news_message}"
        send_whatsapp_message(final_message)
    elif stock_message:
        send_whatsapp_message(stock_message)

# Schedule the task every minute
schedule.every(1).minutes.do(check_and_notify)
while True:
    schedule.run_pending()
    time.sleep(1)

