#!/usr/bin/env python3
"""Haftalık story takvimi (plan.json) üretir — Klein, Kastel, Izaka, ARTI2 için ortak kural.

Kullanım:  python3 scripts/plan_week.py <hafta_klasörü>            (klasördeki plan_kaynak.json'u okur)
           python3 scripts/plan_week.py <hafta_klasörü> --from 2026-11-25   (bu tarihten önceki günleri boş bırakır)

plan_kaynak.json:
{
 "weekly": {"file": "haftalik_dikey.png", "tags": ["dj1", "mekan", ...]},
 "events": {"cuma": {"file": "cuma_dikey.png", "tags": [...]},
            "cumartesi": {"file": "cumartesi_dikey.png", "tags": [...]}}
}
Kural (kullanıcı isteği, 24 Kasım 2026):
- DJ'ye özel (günlük) afiş SADECE etkinlik günü paylaşılır.
- Haftalık program afişi, etkinlik günü OLMAYAN günlere yayılır: Pazartesi'den haftanın son etkinliğine kadar
  etkinliksiz her gün (son etkinlikten sonraki günlere konmaz; program bitmiş olur).
- Pazar paylaşımı yok (workflow Pazar sadece istatistik toplar).
"""
import json, sys, datetime, os

GUNLER = ["pazartesi", "sali", "carsamba", "persembe", "cuma", "cumartesi", "pazar"]


def build(src, monday, start=None):
    events = src.get("events", {})
    weekly = src.get("weekly")
    idx = [GUNLER.index(g) for g in events]
    last = max(idx) if idx else -1
    plan = {}
    for i, g in enumerate(GUNLER[:6]):
        day = monday + datetime.timedelta(days=i)
        if start and day < start:
            continue
        if g in events:
            e = events[g]
            plan[g] = e if isinstance(e, list) else [e]
        elif weekly and i < last:
            plan[g] = [weekly]
    return plan


if __name__ == "__main__":
    week = sys.argv[1].rstrip("/")
    start = None
    if "--from" in sys.argv:
        start = datetime.date.fromisoformat(sys.argv[sys.argv.index("--from") + 1])
    monday = datetime.date.fromisoformat(os.path.basename(week).split("_")[0])
    src = json.load(open(f"{week}/plan_kaynak.json", encoding="utf-8"))
    plan = build(src, monday, start)
    old = {}
    if os.path.exists(f"{week}/plan.json"):
        old = json.load(open(f"{week}/plan.json", encoding="utf-8"))
    if old.get("_panel"):
        plan["_panel"] = True
    json.dump(plan, open(f"{week}/plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for g in GUNLER[:6]:
        print(f"{g:10s}", ", ".join(e["file"] if isinstance(e, dict) else e for e in plan.get(g, [])) or "—")
