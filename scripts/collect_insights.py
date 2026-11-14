"""Story performansını kaydeder (Instagram Graph API, instagram_manage_insights).

Story istatistikleri yalnızca story yayındayken (24 saat) okunabilir. Bu betik her sabah
paylaşım çalışmasından önce koşar; son 30 saatte paylaşılmış (paylasim.log) ve henüz
kaydedilmemiş story'lerin sayılarını performans.csv'ye ekler. Hata verirse işi durdurmaz.
"""
import csv, glob, json, os, datetime, urllib.request, urllib.parse, urllib.error

API = "https://graph.facebook.com/v21.0"
TOKEN = os.environ.get("IG_TOKEN", "").strip()
SAVE = os.environ.get("SAVE", "1") == "1"  # test modunda sadece ekrana yazar
OUT = "performans.csv"
METRICS = ["reach", "views", "replies", "navigation", "profile_visits", "follows", "shares", "total_interactions"]
FIELDS = ["tarih", "saat", "kaynak", "hafta", "dosya", "media_id"] + METRICS + ["etiket"]
TR = datetime.timezone(datetime.timedelta(hours=3))


def metric(mid, name):
    q = urllib.parse.urlencode({"metric": name, "access_token": TOKEN})
    try:
        with urllib.request.urlopen(f"{API}/{mid}/insights?{q}", timeout=60) as r:
            data = json.load(r).get("data", [])
        return data[0]["values"][0]["value"] if data else ""
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"  {name}: alınamadı ({e.code}) {body[:160]}")
        return ""
    except Exception as e:  # ağ hatası vb.
        print(f"  {name}: alınamadı ({e})")
        return ""


def main():
    if not TOKEN:
        print("IG_TOKEN yok; istatistik toplanmadı.")
        return
    seen = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            seen = {row["media_id"] for row in csv.DictReader(f)}
    now = datetime.datetime.now(TR)
    rows = []
    for log in sorted(glob.glob("haftalar/*/paylasim.log") + glob.glob("kastel/haftalar/*/paylasim.log")):
        kaynak = "kastel" if log.startswith("kastel/") else "klein"
        hafta = log.split("/")[-2]
        for line in open(log, encoding="utf-8"):
            p = line.split()
            if len(p) < 5 or p[3] != "OK" or "(silindi)" in line:
                continue
            tarih, saat, dosya, mid = p[0], p[1], p[2], p[4]
            if mid in seen:
                continue
            try:
                t = datetime.datetime.fromisoformat(f"{tarih}T{saat}").replace(tzinfo=TR)
            except ValueError:
                continue
            if not (datetime.timedelta(0) <= now - t <= datetime.timedelta(hours=30)):
                continue
            etiket = line.split("etiket:", 1)[1].strip() if "etiket:" in line else ""
            print(f"{kaynak} {tarih} {saat} {dosya} ({mid})")
            row = {"tarih": tarih, "saat": saat, "kaynak": kaynak, "hafta": hafta, "dosya": dosya, "media_id": mid, "etiket": etiket}
            for m in METRICS:
                row[m] = metric(mid, m)
            print("  " + ", ".join(f"{m}={row[m]}" for m in METRICS))
            if all(row[m] == "" for m in METRICS):
                print("  Hiçbir metrik alınamadı (izin eksik olabilir); kaydedilmedi, yarın tekrar denenmeyecek çünkü story süresi doldu.")
                continue
            rows.append(row)
            seen.add(mid)
    if not rows:
        print("Kaydedilecek yeni story istatistiği yok.")
        return
    if not SAVE:
        print(f"TEST: {len(rows)} story okundu, performans.csv'ye KAYDEDİLMEDİ.")
        return
    new = not os.path.exists(OUT)
    with open(OUT, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} story kaydedildi → {OUT}")


if __name__ == "__main__":
    main()
