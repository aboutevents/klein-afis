"""Klein Phönix story paylaşımı (Instagram Graph API).

GitHub Actions her gün (Pzt–Cmt) çalıştırır. Bugünün gününe göre
haftalar/<Pazartesi>_hafta/plan.json içindeki görselleri abouteventsorg
Instagram hesabına story olarak paylaşır. Etiket/metin eklemez.

Ortam değişkenleri:
  IG_TOKEN    : Meta sistem kullanıcısı erişim anahtarı (GitHub Secrets)
  IG_USER_ID  : Instagram hesap kimliği (varsayılan abouteventsorg)
  MODE        : "publish" (paylaş) veya "test" (taslak hazırlar, YAYINLAMAZ)
  DATE        : YYYY-MM-DD (boşsa İstanbul saatine göre bugün)
  BASE        : hafta klasörlerinin kökü: "haftalar" (Klein Phönix, varsayılan)
                veya "kastel/haftalar" (Kastel). Virgülle birden fazla verilebilir.
"""
import json, os, sys, time, datetime, urllib.request, urllib.parse, urllib.error

API = "https://graph.facebook.com/v21.0"
TOKEN = os.environ.get("IG_TOKEN", "").strip()
IG_USER_ID = os.environ.get("IG_USER_ID", "").strip() or "17841449383702414"
MODE = (os.environ.get("MODE") or "publish").strip().lower()
REPO = os.environ.get("GITHUB_REPOSITORY", "aboutevents/klein-afis")
SHA = os.environ.get("GITHUB_SHA", "main")
BASES = [b.strip().strip("/") for b in (os.environ.get("BASE") or "haftalar").split(",") if b.strip()]
GUNLER = ["pazartesi", "sali", "carsamba", "persembe", "cuma", "cumartesi", "pazar"]


def call(method, path, params):
    params = dict(params, access_token=TOKEN)
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise SystemExit(f"API HATASI {e.code} ({path}): {body}")


def main():
    if not TOKEN:
        raise SystemExit("IG_TOKEN tanımlı değil (GitHub > Settings > Secrets and variables > Actions).")
    d = os.environ.get("DATE", "").strip()
    today = (datetime.date.fromisoformat(d) if d
             else (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).date())
    monday = today - datetime.timedelta(days=today.weekday())
    gun = GUNLER[today.weekday()]
    print(f"Tarih {today} ({gun}) · kökler {', '.join(BASES)} · mod {MODE}")

    acct = call("GET", IG_USER_ID, {"fields": "username"})
    print("Instagram hesabı:", acct.get("username"))

    for base in BASES:
        post_week(f"{base}/{monday.isoformat()}_hafta", today, gun)


def post_week(week, today, gun):
    print(f"— klasör {week}")
    plan_path = f"{week}/plan.json"
    if not os.path.exists(plan_path):
        print("Bu hafta için plan.json yok; paylaşılacak bir şey yok.")
        return
    files = json.load(open(plan_path, encoding="utf-8")).get(gun, [])
    if not files:
        print("Bugün için planlanmış story yok.")
        return

    log_path = f"{week}/paylasim.log"
    done = open(log_path, encoding="utf-8").read() if os.path.exists(log_path) else ""
    for f in files:
        jpg = os.path.splitext(f)[0] + ".jpg"
        if not os.path.exists(f"{week}/{jpg}"):
            raise SystemExit(f"Görsel bulunamadı: {week}/{jpg}")
        already = any(l.startswith(today.isoformat()) and f" {jpg} OK" in l for l in done.splitlines())
        if MODE == "publish" and already:
            print("Zaten paylaşılmış, atlanıyor:", jpg)
            continue
        url = f"https://raw.githubusercontent.com/{REPO}/{SHA}/{week}/{jpg}"
        c = call("POST", f"{IG_USER_ID}/media", {"image_url": url, "media_type": "STORIES"})
        cid = c["id"]
        for _ in range(30):
            st = call("GET", cid, {"fields": "status_code"}).get("status_code")
            if st == "FINISHED":
                break
            if st == "ERROR":
                raise SystemExit(f"Instagram görseli işleyemedi: {jpg}")
            time.sleep(5)
        if MODE != "publish":
            print(f"TEST OK: {jpg} için story taslağı hazırlandı ({cid}), YAYINLANMADI.")
            continue
        p = call("POST", f"{IG_USER_ID}/media_publish", {"creation_id": cid})
        now = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime("%H:%M")
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(f"{today.isoformat()} {now} {jpg} OK {p.get('id')}\n")
        print("PAYLAŞILDI:", jpg, p.get("id"))
        time.sleep(10)


if __name__ == "__main__":
    main()
