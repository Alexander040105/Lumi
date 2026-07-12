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
if not url or not key:
    print("ERROR: Missing Supabase credentials", file=sys.stderr)
    sys.exit(1)

headers = {"apikey": key, "Authorization": f"Bearer {key}"}
resp = httpx.get(f"{url}/rest/v1/provinces?select=province_id,name", headers=headers, timeout=30)
print("Status:", resp.status_code)
if resp.status_code == 200:
    data = resp.json()
    for p in data:
        print(f"{p['province_id']}: {p['name']}")
else:
    print(resp.text[:500])
