import httpx, os, json
from dotenv import load_dotenv
load_dotenv(r'd:\63947\Documents\GitHub\Lumi\.env')
url = os.getenv('SUPABASE_URL') or os.getenv('VITE_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

# Get all region names from DB
resp = httpx.get(f'{url}/rest/v1/regions?select=region_id,name,psgc_code', headers=headers)
db_regions = resp.json()
print("DB Regions:")
for r in db_regions:
    print(f"  {r['region_id']}: {r['name']} (psgc: {r.get('psgc_code')})")

# Get region names from cache
with open('scripts/psgc_cache/regions.json') as f:
    api_regions = json.load(f)
print("\nAPI Regions:")
for r in api_regions:
    print(f"  {r['psgc_code']}: {r['area_name']}")

# Check normalize_name matching
import re
def normalize_name(name):
    name = name.upper().strip()
    name = re.sub(r'^(CITY OF|MUNICIPALITY OF|BARANGAY OF)\s+', '', name)
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'[^A-Z0-9 ]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

print("\nNormalized names comparison:")
db_norms = {normalize_name(r['name']): r['name'] for r in db_regions}
api_norms = {normalize_name(r['area_name']): r['area_name'] for r in api_regions}
for dn, orig in db_norms.items():
    match = "MATCH" if dn in api_norms else "NO MATCH"
    print(f"  DB '{orig}' -> '{dn}' [{match}]")
