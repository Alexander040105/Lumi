import urllib.request
import json

BASE = 'http://127.0.0.1:8004/api/v1'

def req(url, method='GET', data=None):
    try:
        r = urllib.request.Request(url, method=method)
        if data:
            r.add_header('Content-Type', 'application/json')
            r.data = json.dumps(data).encode('utf-8')
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return -1, str(e)

print('=== 1. ECOSIM POST ===')
c, r = req(f'{BASE}/ecosim/', method='POST', data={
    'house_name': 'Test House',
    'municipality': 'ABORLAN',
    'current_electricity_bill': 5000,
    'electricity_rate': 12.5,
    'desired_savings': 0.3
})
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
else:
    print(f'  Body: {r[:300]}')

print('\n=== 2. ECOSIM GET ===')
c, r = req(f'{BASE}/ecosim/?municipality_id=1&monthly_consumption=350&monthly_bill=5000')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
else:
    print(f'  Body: {r[:300]}')

print('\n=== 3. ECOSIM SEASONAL ===')
c, r = req(f'{BASE}/ecosim/seasonal?municipality_id=1')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
else:
    print(f'  Body: {r[:300]}')

print('\n=== 4. ML TRAIN ===')
c, r = req(f'{BASE}/ml/train?model_type=LinearTrend', method='POST')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'results' in r and r['results']:
        res = r['results'][0]
        print(f'  Result status: {res.get("status")}')
        metrics = res.get('metrics', {})
        print(f'  MAPE: {metrics.get("mape")}')
else:
    print(f'  Body: {r[:300]}')

print('\n=== 5. ML FORECAST ===')
c, r = req(f'{BASE}/ml/forecast?target_variable=total_consumption_gwh&horizon_years=6')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
else:
    print(f'  Body: {r[:300]}')

print('\n=== DONE ===')
