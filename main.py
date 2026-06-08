from flask import Flask, request, jsonify, send_from_directory
import requests, os

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'bot.html')

@app.route('/api/yahoo')
def yahoo():
    symbol   = request.args.get('symbol', '')
    interval = request.args.get('interval', '1d')
    period   = request.args.get('period',  '1y')

    # Yahoo Finance interval/range mapping
    # 1h  → interval=1h,  range=7d
    # 4h  → interval=60m, range=30d  (Yahoo max for intraday is 60d)
    # 1d  → interval=1d,  range=1y
    # 1w  → interval=1wk, range=2y

    range_map = {
        '1h':  '7d',
        '60m': '30d',
        '1d':  '1y',
        '1wk': '2y',
    }
    period = range_map.get(interval, period)

    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
    params = {'interval': interval, 'range': period}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        data = r.json()
        result = data.get('chart', {}).get('result', [])
        if not result:
            return jsonify({'error': 'no_data'}), 200
        chart = result[0]
        q = chart['indicators']['quote'][0]
        closes = q.get('close', [])
        highs  = q.get('high',  [])
        lows   = q.get('low',   [])
        vols   = q.get('volume',[])
        clean = [(c,h,l,v if v else 0) for c,h,l,v in zip(closes,highs,lows,vols) if c and h and l]
        if len(clean) < 14:
            return jsonify({'error': 'insufficient_data'}), 200
        resp = jsonify({
            'c': [x[0] for x in clean],
            'h': [x[1] for x in clean],
            'l': [x[2] for x in clean],
            'v': [x[3] for x in clean],
            's': 'ok'
        })
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
