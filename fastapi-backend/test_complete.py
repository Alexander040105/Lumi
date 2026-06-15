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

print('=== EcoSim GET (invalid id=1) ===')
c, r = req(f'{BASE}/ecosim/?municipality_id=1&monthly_consumption=350&monthly_bill=5000')
print(f'  Status: {c}')
if isinstance(r, dict) and 'detail' in r:
    print(f'  Detail: {r["detail"]}')
else:
    print(f'  Body: {r[:200] if len(str(r)) > 200 else r}')

print('\n=== EcoSim GET (valid id=5441) ===')
c, r = req(f'{BASE}/ecosim/?municipality_id=5441&monthly_consumption=350&monthly_bill=5000')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'detail' in r:
        print(f'  Detail: {r["detail"]}')
else:
    print(f'  Body: {r[:200] if len(str(r)) > 200 else r}')

print('\n=== EcoSim Seasonal (valid id=5441) ===')
c, r = req(f'{BASE}/ecosim/seasonal?municipality_id=5441')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'detail' in r:
        print(f'  Detail: {r["detail"]}')
elif isinstance(r, list):
    print(f'  Results count: {len(r)}')
else:
    print(f'  Body: {r[:200] if len(str(r)) > 200 else r}')

print('\n=== ML Train (RandomForest) ===')
c, r = req(f'{BASE}/ml/train?model_type=RandomForest', method='POST')
print(f'  Status: {c}')
if isinstance(r, dict):
    if 'results' in r and r['results']:
        res = r['results'][0]
        print(f'  Status: {res.get("status")}')
        print(f'  MAPE: {res.get("metrics", {}).get("mape")}')
    elif 'detail' in r:
        print(f'  Detail: {r["detail"]}')
else:
    print(f'  Body: {r[:200] if len(str(r)) > 200 else r}')

print('\n=== ML Models List ===')
c, r = req(f'{BASE}/ml/models')
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Count: {len(r.get("items", []))}')

print('\n=== RAG Retrieve (POST) ===')
c, r = req(f'{BASE}/energyhub/rag/retrieve', method='POST', data={'query': 'solar panels', 'top_k': 3})
print(f'  Status: {c}')
if isinstance(r, dict):
    print(f'  Keys: {list(r.keys())}')
    if 'results' in r:
        print(f'  Results count: {len(r["results"])}')
else:
    print(f'  Body: {r[:200] if len(str(r)) > 200 else r}')

print('\n=== Homes (no auth) ===')
c, r = req(f'{BASE}/homes')
print(f'  Status: {c}')
if isinstance(r, dict) and 'detail' in r:
    print(f'  Detail: {r["detail"]}')

print('\n=== Done ===')
