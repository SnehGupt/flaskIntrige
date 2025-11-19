from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import os
from datetime import datetime
from google import genai

API_KEY = os.environ.get("API_KEY")
genai_client = genai.Client(api_key=API_KEY)
app = Flask(__name__)
CORS(app)


# ✅ Defensive parser for numeric values
def parse_value(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return value if value != float('inf') else None
    if isinstance(value, str):
        try:
            return float(value.replace(',', '').strip())
        except ValueError:
            return None
    return None

# ✅ Extract logo using Clearbit
def get_logo_url(info):
    website = info.get("website")
    if website:
        domain = website.replace("https://", "").replace("http://", "").split("/")[0]
        return f"https://logo.clearbit.com/{domain}"
    return None

# ✅ Extract CEO name from company officers
def get_ceo_name(info):
    officers = info.get("companyOfficers", [])
    for officer in officers:
        if officer.get("title", "").lower() == "chief executive officer":
            return officer.get("name")
    return None

@app.route("/")
def home():
    return "Investopedia API is running."

# ✅ Main ticker summary route
@app.route("/api/ticker_summary")
def ticker_summary():
    ticker = request.args.get("ticker", "").upper()
    if not ticker:
        return jsonify({"error": "Ticker symbol is required"}), 400

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        current_price = parse_value(info.get("currentPrice"))
        previous_close = parse_value(info.get("previousClose"))
        total_revenue = parse_value(info.get("totalRevenue"))
        ps_ratio = parse_value(info.get("priceToSalesTrailing12Months"))
        open_price = parse_value(info.get("open"))
        market_cap = parse_value(info.get("marketCap"))
        pe_ratio = parse_value(info.get("trailingPE"))
        ebitda = parse_value(info.get("ebitda"))
        pb_ratio = parse_value(info.get("priceToBook"))
        revenue_growth = parse_value(info.get("revenueGrowth"))
        tax_rate = parse_value(info.get("effectiveTaxRate"))

        price_change = (current_price - previous_close) if current_price and previous_close else None
        price_change_pct = (price_change / previous_close * 100) if price_change and previous_close else None

        logo_url = get_logo_url(info)
        ceo_name = get_ceo_name(info)
        sector = info.get("sector")
        valuation_method = None
        if sector == "Financial Services":
            valuation_method = "DDM" if pb_ratio else "DCF"
        else:
            valuation_method = "DCF"
        return jsonify({
            "ticker": ticker,
            "companyName": info.get("longName"),
            "exchange": info.get("exchange"),
            "marketCap": market_cap,
            "ebitda": ebitda,
            "psRatio": ps_ratio,              
            "revenue": total_revenue,  
            "currentPrice": current_price,
            "previousClose": previous_close,
            "open": open_price,
            "priceChange": price_change,
            "priceChangePct": price_change_pct,
            "peRatio": pe_ratio,
            "pbRatio": pb_ratio,
            "revenueGrowth": revenue_growth,
            "taxRate": tax_rate,
            "logoUrl": logo_url,
            "ceoName": ceo_name,
            "valuationMethod": valuation_method, 
            "lastUpdated": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": f"Failed to fetch data for {ticker}: {str(e)}"}), 500

# ✅ Optional: Logo search by company name
@app.route("/api/logo_search")
def logo_search():
    company = request.args.get("company", "")
    if not company:
        return jsonify({"error": "Company name is required"}), 400
    domain = company.lower().replace(" ", "") + ".com"
    return jsonify({"logoUrl": f"https://logo.clearbit.com/{domain}"})

# ✅ Optional: CEO image search placeholder
@app.route("/api/image_search")
def image_search():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    # Placeholder: integrate Bing Image Search or similar here
    return jsonify({"imageUrl": f"https://example.com/search?q={query}"})

# ✅ Required for Render deployment
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
