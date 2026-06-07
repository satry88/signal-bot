from flask import Flask, jsonify, request, send_file
import requests, os, math

app = Flask(__name__)
FH_KEY = os.getenv("FINNHUB_API_KEY", "")

@app.route("/")
def index():
    return send_file("bot.html")

@app.route("/candle")
def candle():
    sym = request.args.get("symbol", "")
    res = request.args.get("resolution", "D")
    frm = request.args.get("from", "")
    to  = request.args.get("to", "")
    typ = request.args.get("type", "stock")

    if typ == "forex":
        url = "https://finnhub.io/api/v1/forex/candle"
        sym_use = f"OANDA:{sym}"
    else:
        url = "https://finnhub.io/api/v1/stock/candle"
        sym_use = sym

    try:
        r = requests.get(url, params={
            "symbol": sym_use,
            "resolution": res,
            "from": frm,
            "to": to,
            "token": FH_KEY
        }, timeout=10)
        data = r.json()
    except Exception as e:
        data = {"s": "error", "error": str(e)}

    resp = jsonify(data)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET"
    return resp

@app.route("/health")
def health():
    return jsonify({"status": "ok", "key_set": bool(FH_KEY)})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
