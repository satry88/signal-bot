from flask import Flask, request, jsonify, send_from_directory
import requests, os, time

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'bot.html')

# ── Yahoo Finance proxy ──────────────────────────
@app.route('/api/yahoo')
def yahoo():
    symbol   = request.args.get('symbol', '')
    interval = request.args.get('interval', '1d')   # 1d, 1wk
    period   = request.args.get('period',  '6mo')   # 6mo, 1y

    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
    params = {'interval': interval, 'range': period}
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        result = data.get('chart', {}).get('result', [])
        if not result:
            return jsonify({'error': 'no_data'}), 200

        chart = result[0]
        closes = chart['indicators']['quote'][0].get('close', [])
        highs  = chart['indicators']['quote'][0].get('high',  [])
        lows   = chart['indicators']['quote'][0].get('low',   [])
        vols   = chart['indicators']['quote'][0].get('volume',[])

        # Remove None values
        data_clean = [(c,h,l,v) for c,h,l,v in zip(closes,highs,lows,vols)
                      if c is not None and h is not None and l is not None]
        if len(data_clean) < 14:
            return jsonify({'error': 'insufficient_data'}), 200

        c_list = [x[0] for x in data_clean]
        h_list = [x[1] for x in data_clean]
        l_list = [x[2] for x in data_clean]
        v_list = [x[3] if x[3] else 0 for x in data_clean]

        resp = jsonify({'c': c_list, 'h': h_list, 'l': l_list, 'v': v_list, 's': 'ok'})
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
