#!/usr/bin/env python3
"""Haftanın story planını (plan.json) aboutevents.org paneline aktarır.

Kullanım:
  python3 scripts/to_panel.py kastel kastel/haftalar/2026-11-16_hafta /home/claude/web
  python3 scripts/to_panel.py klein  haftalar/2026-11-16_hafta        /home/claude/web

Her story için web deposunda database/data/social/<hesap>-<tarih>-<dosya>/post.json yazar
(görsel bu deponun raw.githubusercontent adresinden; panel indirip saklar). Web deposu main'e
push edilince sunucu 5–10 dk içinde içe aktarır: admin > Sosyal paylaşımlar.

Kim paylaşır? (--mod)
  panel  : panel paylaşır (kayıtlar "Planlandı"); plan.json'a "_panel": true yazılır, GitHub Actions o haftayı atlar.
  github : GitHub Actions paylaşır; panel kayıtları "Durduruldu" (sadece görmek için).
  auto   : (varsayılan) sunucuda Meta anahtarı etkinse panel, değilse github
           (https://test.aboutevents.org/storage/ops-status.txt içindeki "meta: ... env=var").
Geçmiş saatli story'ler aktarılmaz. Panelde düzenlenen kayıtların üzerine yazılmaz.
"""
import datetime, json, os, sys, urllib.request

REPO = "aboutevents/klein-afis"
GUNLER = ["pazartesi", "sali", "carsamba", "persembe", "cuma", "cumartesi", "pazar"]
GUN_TR = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
AYLAR = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
HESAP = {
    # saat: GitHub'ın paylaştığı saatle aynı; platformlar panelde değiştirilebilir
    "kastel": {"ad": "Kastel", "saat": "13:00", "platforms": ["ig", "fb"]},
    "klein": {"ad": "Klein Phönix", "saat": "11:00", "platforms": ["ig"]},
}
ETIKET = {
    "haftalik": "Haftalık program", "wed": "Çarşamba etkinliği", "fri": "Cuma etkinliği", "sat": "Cumartesi etkinliği",
    "thu": "Perşembe etkinliği", "sun": "Pazar etkinliği", "cuma": "Cuma etkinliği", "cumartesi": "Cumartesi etkinliği",
}
STATUS_URL = "https://test.aboutevents.org/storage/ops-status.txt"


def panel_hazir():
    try:
        with urllib.request.urlopen(STATUS_URL, timeout=20) as r:
            txt = r.read().decode("utf-8", "replace")
    except Exception as e:
        print("Sunucu durumu okunamadı:", e)
        return False
    return any(l.startswith("meta:") and "env=var" in l for l in txt.splitlines())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if len(args) != 3 or args[0] not in HESAP:
        sys.exit(__doc__)
    hesap, week, web = args[0], args[1].strip("/"), args[2]
    h = HESAP[hesap]
    mod = opts.get("mod", "auto")
    if mod == "auto":
        mod = "panel" if panel_hazir() else "github"
    print(f"Paylaşan: {mod}")

    plan_path = os.path.join(week, "plan.json")
    plan = json.load(open(plan_path, encoding="utf-8"))
    monday = datetime.date.fromisoformat(os.path.basename(week).split("_")[0])
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
    out_root = os.path.join(web, "database", "data", "social")
    n = 0
    for i, gun in enumerate(GUNLER):
        for entry in plan.get(gun, []) or []:
            f = entry["file"] if isinstance(entry, dict) else entry
            tags = entry.get("tags", []) if isinstance(entry, dict) else []
            stem = os.path.splitext(f)[0]
            d = monday + datetime.timedelta(days=i)
            when = datetime.datetime.fromisoformat(f"{d.isoformat()} {h['saat']}")
            if when <= now.replace(tzinfo=None):
                print("Geçmiş, atlandı:", d, f)
                continue
            konu = ETIKET.get(stem.replace("-story", "").replace("_dikey", "").replace("-", "_").split("_")[0], stem)
            key = f"{hesap}-{d.isoformat()}-{stem}"
            post = {
                "title": f"{h['ad']} · {konu} · {d.day} {AYLAR[d.month]} {GUN_TR[i]}",
                "account": "aboutevents",
                "type": "story",
                "platforms": h["platforms"],
                "scheduled_at": when.strftime("%Y-%m-%d %H:%M"),
                "status": "scheduled" if mod == "panel" else "paused",
                "media": [f"https://raw.githubusercontent.com/{REPO}/main/{week}/{stem}.jpg"],
                "tags": tags,
            }
            os.makedirs(os.path.join(out_root, key), exist_ok=True)
            with open(os.path.join(out_root, key, "post.json"), "w", encoding="utf-8") as fh:
                json.dump(post, fh, ensure_ascii=False, indent=1)
            n += 1
            print(f"{key}: {post['scheduled_at']} · {len(tags)} etiket · {post['status']}")

    if mod == "panel":
        plan["_panel"] = True
    else:
        plan.pop("_panel", None)
    with open(plan_path, "w", encoding="utf-8") as fh:
        json.dump(plan, fh, ensure_ascii=False, indent=1)
    print(f"{n} story panele yazıldı ({out_root}).")


if __name__ == "__main__":
    main()
