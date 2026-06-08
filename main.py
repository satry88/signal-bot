from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='.')

FINNHUB_KEY = os.environ.get('FINNHUB_KEY', '')

@app.route('/')
def index():
    return send_from_directory('.', 'bot.html')

# ── Proxy: Stock candles ──────────────────────────
@app.route('/api/stock')
def stock():
    symbol     = request.args.get('symbol', '')
    resolution = request.args.get('resolution', 'D')
    from_ts    = request.args.get('from', '')
    to_ts      = request.args.get('to', '')
    key        = request.args.get('token', FINNHUB_KEY)

    url = (f'https://finnhub.io/api/v1/stock/candle'
           f'?symbol={symbol}&resolution={resolution}'
           f'&from={from_ts}&to={to_ts}&token={key}')
    try:
        r = requests.get(url, timeout=10)
        resp = jsonify(r.json())
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Proxy: Forex/metals candles ───────────────────
@app.route('/api/forex')
def forex():
    symbol     = request.args.get('symbol', '')
    resolution = request.args.get('resolution', 'D')
    from_ts    = request.args.get('from', '')
    to_ts      = request.args.get('to', '')
    key        = request.args.get('token', FINNHUB_KEY)

    url = (f'https://finnhub.io/api/v1/forex/candle'
           f'?symbol={symbol}&resolution={resolution}'
           f'&from={from_ts}&to={to_ts}&token={key}')
    try:
        r = requests.get(url, timeout=10)
        resp = jsonify(r.json())
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Proxy: Stock quote (current price) ───────────
@app.route('/api/quote')
def quote():
    symbol = request.args.get('symbol', '')
    key    = request.args.get('token', FINNHUB_KEY)
    url    = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={key}'
    try:
        r = requests.get(url, timeout=10)
        resp = jsonify(r.json())
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
