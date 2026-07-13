import json
for f in ['regions', 'provinces', 'municipalities', 'barangays']:
    data = json.load(open(f'scripts/psgc_cache/{f}.json'))
    print(f'{f}: {len(data)} records')
