import urllib.request
import json

BASE = 'http://127.0.0.1:8001/api/v1'

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

print('--- EcoSim POST (corrected desired_savings) ---')
c, r = req(f'{BASE}/ecosim/', method='POST', data={
    'house_name': 'Test House',
    'municipality': 'Manila',
    'current_electricity_bill': 5000,
    'electricity_rate': 12.5,
    'desired_savings': 0.3
})
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'error' in r:
        print(f'  Error: {r["error"]}')
    else:
        for k in ['solar', 'wind', 'hydro', 'economic_summary']:
            print(f'  Has {k}: {k in r}')
else:
    print(f'  Body: {r[:300]}')

print('\n--- EcoSim GET ---')
c, r = req(f'{BASE}/ecosim/?municipality_id=1&monthly_consumption=350&monthly_bill=5000')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
else:
    print(f'  Body: {r[:300] if len(str(r)) > 300 else r}')

print('\n--- EcoSim Seasonal ---')
c, r = req(f'{BASE}/ecosim/seasonal?municipality_id=1')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
else:
    print(f'  Body: {r[:300] if len(str(r)) > 300 else r}')

print('\n--- EnergyHub Source Breakdown ---')
c, r = req(f'{BASE}/energyhub/source-breakdown')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
else:
    print(f'  Body: {r[:200] if len(str(r)) > 200 else r}')

print('\n--- EnergyHub Grid Breakdown ---')
c, r = req(f'{BASE}/energyhub/grid-breakdown')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
else:
    print(f'  Body: {r[:200] if len(str(r)) > 200 else r}')

print('\n--- EnergyHub Trends ---')
c, r = req(f'{BASE}/energyhub/trends?variable=consumption&years=5')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
else:
    print(f'  Body: {r[:200] if len(str(r)) > 200 else r}')

print('\n--- RAG Retrieve ---')
c, r = req(f'{BASE}/energyhub/rag/retrieve', method='POST', data={'query': 'solar panels'})
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'results' in r:
        print(f'  Results count: {len(r["results"])}')
else:
    print(f'  Body: {r[:200] if len(str(r)) > 200 else r}')

print('\n=== ALL TESTS COMPLETE ===')
