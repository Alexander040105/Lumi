"""Test PSA API pagination."""
import httpx, os, json
from dotenv import load_dotenv
load_dotenv(r'd:\63947\Documents\GitHub\Lumi\.env')
token = os.getenv('PSGC_API_CODE')

for level in ['provinces', 'barangays']:
    for ps in [100, 500, 1000]:
        url = f'https://classification.psa.gov.ph/psgc/Q2_2024/{level}?token={token}&perPage={ps}&page=1'
        resp = httpx.get(url, timeout=30.0)
        data = resp.json()
        results = data.get('results', {})
        records = results.get('psgc_data', []) if isinstance(results, dict) else results
        nxt = data.get('next', 'None')
        print(f'{level} perPage={ps}: got {len(records)} records, next={str(nxt)[:100]}')
    print()
