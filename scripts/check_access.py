"""Jetonun hangi Facebook sayfalarına ve Instagram hesaplarına erişebildiğini listeler (hiçbir şey yayınlamaz)."""
import json, os, urllib.request, urllib.parse, urllib.error
API = "https://graph.facebook.com/v21.0"
TOKEN = os.environ.get("IG_TOKEN", "").strip()

def get(path, **p):
    p["access_token"] = TOKEN
    try:
        with urllib.request.urlopen(f"{API}/{path}?{urllib.parse.urlencode(p)}", timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode(errors="replace")}

if not TOKEN:
    raise SystemExit("IG_TOKEN tanımlı değil")
perms = get("me/permissions")
print("İzinler:", ", ".join(p["permission"] for p in perms.get("data", []) if p.get("status") == "granted") or perms)
pages = get("me/accounts", fields="id,name,instagram_business_account{id,username}")
for pg in pages.get("data", []):
    ig = pg.get("instagram_business_account") or {}
    print(f"Sayfa: {pg['name']} ({pg['id']}) · Instagram: @{ig.get('username','-')} ({ig.get('id','-')})")
    if ig.get("id"):
        lim = get(f"{ig['id']}/content_publishing_limit", fields="quota_usage,config")
        print("   Yayın kotası:", json.dumps(lim.get("data", lim)))
if "error" in pages:
    print("Hata:", pages["error"])
