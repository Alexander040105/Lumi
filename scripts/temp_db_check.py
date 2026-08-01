import os, httpx, sys
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)

url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
key = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY")
)
headers = {"apikey": key, "Authorization": f"Bearer {key}"}

# Check provinces in NCR (region_id=69)
resp = httpx.get(
    f"{url}/rest/v1/provinces?select=province_id,name,region_id&region_id=eq.69&order=province_id.asc",
    headers=headers, timeout=30
)
print("=== NCR Provinces (region_id=69) ===")
for p in resp.json():
    print(f"  {p['province_id']}: {p['name']}")

# Check all provinces to see if there's a "Metropolitan Manila" or similar
resp2 = httpx.get(
    f"{url}/rest/v1/provinces?select=province_id,name,region_id&order=name.asc",
    headers=headers, timeout=30
)
print("\n=== All provinces (by name) ===")
for p in resp2.json():
    if p['region_id'] in (53, 56, 57, 69):
        print(f"  {p['province_id']}: {p['name']} (region_id={p['region_id']})")

# Check HUC municipalities
resp3 = httpx.get(
    f"{url}/rest/v1/municipalities?select=municipality_id,name,province_id&order=name.asc&limit=20",
    headers=headers, timeout=30
)
print("\n=== First 20 municipalities ===")
for m in resp3.json():
    print(f"  {m['municipality_id']}: {m['name']} (province_id={m['province_id']})")
