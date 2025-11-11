from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
        price_change = current_price - previous_close if current_price and previous_close else None
        price_change_pct = (price_change / previous_close * 100) if price_change and previous_close else None

        summary = {
            "ticker": ticker,
            "companyName": info.get("longName", "N/A"),
            "exchange": info.get("exchange", "N/A"),
            "marketCap": f"${info.get('marketCap'):,}" if info.get("marketCap") else "N/A",
            "ebitda": f"${info.get('ebitda'):,}" if info.get("ebitda") else "N/A",
            "latestPrice": f"${current_price:.2f}" if current_price else "N/A",
            "previousClose": f"${previous_close:.2f}" if previous_close else "N/A",
            "open": f"${open_price:.2f}" if open_price else "N/A",
            "priceChange": f"${price_change:.2f}" if price_change else "N/A",
            "priceChangePct": f"{price_change_pct:.2f}%" if price_change_pct else "N/A",
            "peRatio": f"{info.get('trailingPE'):.2f}" if info.get("trailingPE") else "N/A",
            "revenueGrowth": f"{info.get('revenueGrowth') * 100:.2f}%" if info.get("revenueGrowth") else "N/A",
            "taxRate": f"{info.get('effectiveTaxRate') * 100:.2f}%" if info.get("effectiveTaxRate") else "N/A",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return jsonify(summary)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch data for {ticker}: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
