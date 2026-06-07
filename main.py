from flask import Flask, jsonify, request, send_file
import requests, os, io

app = Flask(__name__)
FH_KEY = os.getenv("FINNHUB_API_KEY", "")

@app.route("/")
def index():
    return send_file("bot.html")

@app.route("/candle")
def candle():
    sym = request.args.get("symbol","")
    res = request.args.get("resolution","60")
    frm = request.args.get("from","")
    to  = request.args.get("to","")
    typ = request.args.get("type","stock")
    
    url = "https://finnhub.io/api/v1/forex/candle" if typ=="forex" else "https://finnhub.io/api/v1/stock/candle"
    s   = f"OANDA:{sym}" if typ=="forex" else sym
    
    r = requests.get(url, params={"symbol":s,"resolution":res,"from":frm,"to":to,"token":FH_KEY}, timeout=8)
    resp = jsonify(r.json())
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",5000)))
