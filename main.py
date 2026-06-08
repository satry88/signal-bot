from flask import Flask, request, jsonify, send_from_directory
import requests, os

app = Flask(__name__, static_folder='.')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://finance.yahoo.com/',
    'Origin': 'https://finance.yahoo.com',
}

@app.route('/')
def index():
    return send_from_directory('.', 'bot.html')

@app.route('/api/yahoo')
def yahoo():
    symbol   = request.args.get('symbol', '')
    interval = request.args.get('interval', '1d')

    range_map = {
        '1h':  '7d',
        '60m': '60d',
        '1d':  '1y',
        '1wk': '2y',
    }
    period = range_map.get(interval, '1y')

    # Try v8 first, fallback to v7
    for version in ['v8', 'v7']:
        url = f'https://query1.finance.yahoo.com/{version}/finance/chart/{symbol}'
        params = {'interval': interval, 'range': period}
        try:
            # Get crumb/cookie first
            session = requests.Session()
            session.get('https://finance.yahoo.com', headers=HEADERS, timeout=10)
            r = session.get(url, params=params, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            data = r.json()
            result = data.get('chart', {}).get('result', [])
            if not result:
                error = data.get('chart', {}).get('error', {})
                if error:
                    continue
                return jsonify({'error': 'no_data'}), 200

            chart = result[0]
            q = chart['indicators']['quote'][0]
            closes = q.get('close', [])
            highs  = q.get('high',  [])
            lows   = q.get('low',   [])
            vols   = q.get('volume', [])

            clean = [(c,h,l,v if v else 0)
                     for c,h,l,v in zip(closes, highs, lows, vols)
                     if c is not None and h is not None and l is not None]

            if len(clean) < 14:
                continue

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
            continue

    return jsonify({'error': 'insufficient_data'}), 200

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
