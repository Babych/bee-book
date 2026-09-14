import urllib.request, json, os, sys

token = os.environ.get('MONOAPI') or os.environ.get('MONO_TOKEN')
if not token:
    print('Error: MONOAPI secret is not set')
    sys.exit(0)

url = 'https://api.monobank.ua/personal/client-info'
req = urllib.request.Request(url, headers={'X-Token': token, 'User-Agent': 'BeeBookSite/1.0'})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
except Exception as e:
    print('Failed to query Monobank API:', e)
    sys.exit(0)

jars = data.get('jars', [])
target_jar = None

# Look for jar by ID or title
for j in jars:
    if '125MBQpSnH' in str(j):
        target_jar = j
        break

if not target_jar and len(jars) == 1:
    target_jar = jars[0]
elif not target_jar:
    for j in jars:
        t_low = j.get('title', '').lower()
        if 'бджіл' in t_low or 'книга' in t_low or 'root' in t_low:
            target_jar = j
            break

sales = 0
balance_uah = 0
if target_jar:
    balance_kopecks = target_jar.get('balance', 0)
    balance_uah = balance_kopecks / 100.0
    sales = int(balance_uah // 99)
    j_title = target_jar.get('title', 'Без назви')
    print('Found jar:', j_title, 'Balance:', balance_uah, 'UAH, Calculated sales:', sales)
else:
    print('Jar 125MBQpSnH not found in jars list, keeping previous count')
    try:
        with open('stats.json', 'r', encoding='utf-8') as f:
            prev = json.load(f)
            sales = prev.get('sales', 0)
    except:
        sales = 0

stats_data = {
    'sales': sales,
    'balance_uah': balance_uah,
    'updated_at': str(os.environ.get('GITHUB_RUN_ID', 'manual'))
}

with open('stats.json', 'w', encoding='utf-8') as f:
    json.dump(stats_data, f, indent=2)

print('Updated stats.json successfully with sales:', sales)
