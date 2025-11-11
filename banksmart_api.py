from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import os
from datetime import datetime

# ✅ Create Flask app before defining routes
app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "BankSmart API is running."

@app.route("/api/ticker_summary")
def ticker_summary():
    ticker = request.args.get("ticker", "").upper()
    if not ticker:
        return jsonify({"error": "Ticker symbol is required"}), 400

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        current_price = info.get("currentPrice")
        previous_close = info.get("previousClose")
        open_price = info.get("open")
        price_change = (current_price - previous_close) if current_price and previous_close else None
        price_change_pct = (price_change / previous_close * 100) if price_change and previous_close else None

        return jsonify({
            "ticker": ticker,
            "companyName": info.get("longName"),
            "exchange": info.get("exchange"),
            "marketCap": info.get("marketCap"),
            "ebitda": info.get("ebitda"),
            "currentPrice": current_price,
            "previousClose": previous_close,
            "open": open_price,
            "priceChange": price_change,
            "priceChangePct": price_change_pct,
            "peRatio": info.get("trailingPE"),
            "revenueGrowth": info.get("revenueGrowth"),
            "taxRate": info.get("effectiveTaxRate"),
            "lastUpdated": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": f"Failed to fetch data for {ticker}: {str(e)}"}), 500

# ✅ Required for Render deployment
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
