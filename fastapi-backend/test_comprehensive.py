import urllib.request
import json

BASE = 'http://127.0.0.1:8006/api/v1'

def req(url, method='GET', data=None):
    try:
        r = urllib.request.Request(url, method=method)
        if data:
            r.add_header('Content-Type', 'application/json')
            r.data = json.dumps(data).encode('utf-8')
        with urllib.request.urlopen(r, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return -1, str(e)

results = []

def test(name, status, expected_status, body=None):
    passed = status == expected_status
    results.append((name, status, expected_status, passed))
    status_icon = "PASS" if passed else "FAIL"
    print(f"[{status_icon}] {name}: {status} (expected {expected_status})")
    if body and not passed:
        print(f"      Body: {str(body)[:150]}")

# Health
s, r = req(f'{BASE}/health')
test('Health', s, 200)

# EcoSim Municipalities
s, r = req(f'{BASE}/ecosim/municipalities')
test('EcoSim Municipalities', s, 200)
if isinstance(r, dict):
    print(f"      Count: {len(r.get('items', []))}")

# EcoSim POST
s, r = req(f'{BASE}/ecosim/', method='POST', data={
    'house_name': 'Test House',
    'municipality': 'ABORLAN',
    'current_electricity_bill': 5000,
    'electricity_rate': 12.5,
    'desired_savings': 0.3
})
test('EcoSim POST', s, 201, r)

# EcoSim GET valid
s, r = req(f'{BASE}/ecosim/?municipality_id=5441&monthly_consumption=350&monthly_bill=5000')
test('EcoSim GET (valid)', s, 200, r)

# EcoSim GET invalid
s, r = req(f'{BASE}/ecosim/?municipality_id=1&monthly_consumption=350&monthly_bill=5000')
test('EcoSim GET (invalid)', s, 404, r)

# EcoSim Seasonal valid
s, r = req(f'{BASE}/ecosim/seasonal?municipality_id=5441')
test('EcoSim Seasonal (valid)', s, 200, r)

# EnergyHub Overview
s, r = req(f'{BASE}/energyhub/overview')
test('EnergyHub Overview', s, 200)

# EnergyHub Forecast
s, r = req(f'{BASE}/energyhub/forecast?variable=consumption')
test('EnergyHub Forecast', s, 200)

# EnergyHub Trends
s, r = req(f'{BASE}/energyhub/trends?variable=consumption&years=5')
test('EnergyHub Trends', s, 200)

# EnergyHub Source Breakdown
s, r = req(f'{BASE}/energyhub/source-breakdown')
test('EnergyHub Source Breakdown', s, 200)

# EnergyHub Grid Breakdown
s, r = req(f'{BASE}/energyhub/grid-breakdown')
test('EnergyHub Grid Breakdown', s, 200)

# EnergyHub AI Insight
s, r = req(f'{BASE}/energyhub/ai-insight')
test('EnergyHub AI Insight', s, 200)

# ML Models List
s, r = req(f'{BASE}/ml/models')
test('ML Models List', s, 200)
if isinstance(r, dict):
    print(f"      Models count: {len(r.get('items', []))}")

# ML Train
s, r = req(f'{BASE}/ml/train?model_type=LinearTrend', method='POST')
test('ML Train', s, 202, r)

# ML Forecast
s, r = req(f'{BASE}/ml/forecast?target_variable=total_consumption_gwh&horizon_years=6')
test('ML Forecast', s, 200)

# Homes (no auth)
s, r = req(f'{BASE}/homes')
test('Homes (no auth)', s, 401, r)

# RAG Stats
s, r = req(f'{BASE}/energyhub/rag/stats')
test('RAG Stats', s, 200)

# Summary
passed = sum(1 for _, _, _, p in results if p)
total = len(results)
print(f"\n=== SUMMARY: {passed}/{total} tests passed ===")
for name, status, expected, p in results:
    if not p:
        print(f"  FAIL: {name} got {status}, expected {expected}")
