import urllib.request
import json

BASE = 'http://127.0.0.1:8003/api/v1'

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

# 1. Get a valid municipality
print('=== 1. GET MUNICIPALITIES ===')
c, r = req(f'{BASE}/ecosim/municipalities')
items = r.get('items', []) if isinstance(r, dict) else []
print(f'  Status: {c}  Count: {len(items)}')
first_muni = items[0]['name'] if items else 'Manila'
print(f'  Testing with municipality: {first_muni}')

# 2. Test EcoSim POST with valid municipality
print('\n=== 2. ECOSIM POST ===')
c, r = req(f'{BASE}/ecosim/', method='POST', data={
    'house_name': 'Test House',
    'municipality': first_muni,
    'current_electricity_bill': 5000,
    'electricity_rate': 12.5,
    'desired_savings': 0.3
})
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'error' in r:
        print(f'  Error: {r["error"]}')
    elif 'detail' in r:
        print(f'  Detail: {r["detail"]}')
    else:
        print('  Simulation successful!')
        for k in ['solar', 'wind', 'hydro', 'economic_summary', 'energy_independence_score']:
            print(f'  Has {k}: {k in r}')
else:
    print(f'  Body: {r[:300] if len(str(r)) > 300 else r}')

# 3. Test EcoSim GET
print('\n=== 3. ECOSIM GET ===')
c, r = req(f'{BASE}/ecosim/?municipality_id=1&monthly_consumption=350&monthly_bill=5000')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'detail' in r:
        print(f'  Detail: {r["detail"]}')
else:
    print(f'  Body: {r[:300] if len(str(r)) > 300 else r}')

# 4. Test EcoSim Seasonal
print('\n=== 4. ECOSIM SEASONAL ===')
c, r = req(f'{BASE}/ecosim/seasonal?municipality_id=1')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'detail' in r:
        print(f'  Detail: {r["detail"]}')
else:
    print(f'  Body: {r[:300] if len(str(r)) > 300 else r}')

# 5. Test ML training
print('\n=== 5. ML TRAIN (LinearTrend only - faster) ===')
c, r = req(f'{BASE}/ml/train?model_type=LinearTrend', method='POST')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'results' in r:
        results = r['results']
        if results and isinstance(results, list):
            print(f'  Model trained: {results[0].get("model_type")}')
            print(f'  MAPE: {results[0].get("metrics", {}).get("mape")}%')
            print(f'  Status: {results[0].get("status")}')
    elif 'detail' in r:
        print(f'  Detail: {r["detail"]}')
else:
    print(f'  Body: {r[:300] if len(str(r)) > 300 else r}')

# 6. Test ML models list after training
print('\n=== 6. ML MODELS LIST ===')
c, r = req(f'{BASE}/ml/models')
print(f'  Status: {c}')
if isinstance(r, dict):
    items = r.get('items', [])
    print(f'  Models count: {len(items)}')
    if items:
        print(f'  First model: {items[0].get("model_type")} (active: {items[0].get("is_active")})')

# 7. Test ML forecast
print('\n=== 7. ML FORECAST ===')
c, r = req(f'{BASE}/ml/forecast?target_variable=total_consumption_gwh&horizon_years=6')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'forecast_years' in r:
        print(f'  Years: {r["forecast_years"]}')
        print(f'  Values: {[round(v,1) for v in r["forecast_values"][:3]]}...')
    elif 'detail' in r:
        print(f'  Detail: {r["detail"]}')

# 8. Test RAG retrieve with query param
print('\n=== 8. RAG RETRIEVE ===')
c, r = req(f'{BASE}/energyhub/rag/retrieve?query=solar%20panels&top_k=3')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'results' in r:
        print(f'  Results count: {len(r["results"])}')
else:
    print(f'  Body: {r[:300] if len(str(r)) > 300 else r}')

# 9. Test EnergyHub AI Insight
print('\n=== 9. ENERGYHUB AI INSIGHT ===')
c, r = req(f'{BASE}/energyhub/ai-insight')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'insight' in r:
        print(f'  Insight preview: {r["insight"][:100]}...')

print('\n=== ALL TESTS COMPLETE ===')
