import httpx, os
from dotenv import load_dotenv
load_dotenv(r'd:\63947\Documents\GitHub\Lumi\.env')
url = os.getenv('SUPABASE_URL') or os.getenv('VITE_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

# Check regions with PSGC data
resp = httpx.get(f'{url}/rest/v1/regions?select=region_id,name,psgc_code,island_group,population_2020&limit=3', headers=headers)
print(f'Regions: {resp.json()}')

# Check municipal_population
resp2 = httpx.get(f'{url}/rest/v1/municipal_population?select=*&limit=3', headers=headers)
print(f'Municipal_population: {resp2.json()}')

# Check population_data count via content-range
resp3 = httpx.get(f'{url}/rest/v1/population_data?select=id&limit=1', headers={**headers, 'Prefer': 'count=exact'})
print(f'Population_data content-range: {resp3.headers.get("content-range", "unknown")}')

# Check barangays with PSGC data
resp4 = httpx.get(f'{url}/rest/v1/barangays?select=barangay_id,name,psgc_code,urban_rural,population_2020&limit=3', headers=headers)
print(f'Barangays sample: {resp4.json()}')

# Count barangays with psgc_code set
resp5 = httpx.get(f'{url}/rest/v1/barangays?select=barangay_id&psgc_code=not.is.null&limit=1', headers={**headers, 'Prefer': 'count=exact'})
print(f'Barangays with psgc_code: {resp5.headers.get("content-range", "unknown")}')

# Count municipalities with population_2020
resp6 = httpx.get(f'{url}/rest/v1/municipalities?select=municipality_id&population_2020=not.is.null&limit=1', headers={**headers, 'Prefer': 'count=exact'})
print(f'Municipalities with population_2020: {resp6.headers.get("content-range", "unknown")}')
