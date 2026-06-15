import urllib.request
import json

BASE = 'http://127.0.0.1:8001/api/v1'

def test(url, method='GET', data=None):
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode('utf-8')
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode('utf-8')
            try:
                parsed = json.loads(body)
            except:
                parsed = body
            return resp.status, parsed
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return -1, str(e)

print('--- Health ---')
c, r = test(f'{BASE}/health')
print(f'  Status: {c}')

print('\n--- Municipalities ---')
c, r = test(f'{BASE}/ecosim/municipalities')
print(f'  Status: {c}  Count: {len(r.get("items", [])) if isinstance(r, dict) else "N/A"}')

print('\n--- EnergyHub Overview ---')
c, r = test(f'{BASE}/energyhub/overview')
print(f'  Status: {c}  Keys: {list(r.keys()) if isinstance(r, dict) else "N/A"}')

print('\n--- EnergyHub Forecast ---')
c, r = test(f'{BASE}/energyhub/forecast?variable=consumption')
print(f'  Status: {c}  Keys: {list(r.keys()) if isinstance(r, dict) else "N/A"}')

print('\n--- ML Models (empty expected) ---')
c, r = test(f'{BASE}/ml/models')
print(f'  Status: {c}  Keys: {list(r.keys()) if isinstance(r, dict) else "N/A"}')

print('\n--- Homes (no auth - expect 403) ---')
c, r = test(f'{BASE}/homes')
print(f'  Status: {c}')

print('\n--- EcoSim Simulate ---')
c, r = test(f'{BASE}/ecosim/simulate', method='POST', data={
    'municipality': 'Manila',
    'monthly_kwh': 350,
    'monthly_bill': 5000,
    'roof_area_sqm': 50
})
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'detail' in r:
        print(f'  Error detail: {r["detail"]}')
    else:
        print('  Simulation successful!')
        for k in ['solar', 'wind', 'hydro', 'economic_summary']:
            if k in r:
                print(f'  Has {k}: yes')

print('\n--- EnergyHub RAG Stats ---')
c, r = test(f'{BASE}/energyhub/rag/stats')
print(f'  Status: {c}  Data: {r if isinstance(r, dict) else r[:200]}')

print('\n=== ALL TESTS COMPLETE ===')
