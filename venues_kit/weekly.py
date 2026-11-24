"""Izaka / ARTI2 haftalık afiş (About Events stili): haftalik_dikey + haftalik_yatay (PNG + JPG).
Kullanım: python3 venues_kit/weekly.py <cfg.json> <çıktı_klasörü>
cfg: accent, venue_title, dates, logo, logo_w, bg, bg_pos, foot_l, foot_r, nights[{date,time,head,support[],photo,pos}].
Yollar cfg dosyasının klasörüne göredir (ör. assets/arti2_white.png). Kart fotoğrafı: mekânın kendi story afişinin
YAZISIZ bölümünden kırpılmış görsel (ör. Izaka: story'deki DJ fotoğrafı (300,650,785,1030); ARTI2: disko topu / heykel panelleri)."""
import json, sys, os
from playwright.sync_api import sync_playwright
cfg = json.load(open(sys.argv[1], encoding='utf-8')); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.join(HERE, '..', 'kit'); F = KIT + '/fonts'; A = os.path.dirname(os.path.abspath(sys.argv[1]))
css = open(os.path.join(HERE, 'fonts.css')).read().replace('{F}', F)
M = "font-family:'IBM Plex Mono',monospace;font-weight:600"; C = "font-family:'Archivo';font-weight:900;font-stretch:62%"
acc = cfg['accent']
def f(p): return 'file://' + (p if p.startswith('/') else os.path.join(A, p))
def card(n, vertical, fs, nsup):
    sup = '<br>'.join(n['support'] + ['&nbsp;'] * (nsup - len(n['support'])))
    if vertical:
        photo = (f'<img src="{f(n["photo"])}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:{n.get("pos","50% 30%")}">'
                 '<div style="position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.92) 0%,rgba(0,0,0,.55) 42%,rgba(0,0,0,0) 75%)"></div>')
    else:
        # yatay: fotoğraf kartın sağında, yazılar solda (yüzün üstüne yazı binmez)
        photo = (f'<img src="{f(n["photo"])}" style="position:absolute;top:0;right:0;width:58%;height:100%;object-fit:cover;object-position:{n.get("pos_h", n.get("pos","50% 30%"))}">'
                 '<div style="position:absolute;inset:0;background:linear-gradient(to right,rgba(13,13,13,1) 40%,rgba(13,13,13,.55) 48%,rgba(13,13,13,0) 62%)"></div>')
    return f'''<div style="position:relative;overflow:hidden;background:#0d0d0d">
{photo}
<div style="position:absolute;left:34px;right:{'30px' if vertical else '50%'};bottom:32px;display:flex;flex-direction:column;gap:12px;text-shadow:0 2px 12px rgba(0,0,0,.8)">
<div style="{M};font-size:24px;color:{acc};line-height:1.4">{n['date']}<br>{n['time']}</div>
<div style="{C};font-size:{fs}px;line-height:.9;white-space:nowrap">{n['head']}</div>
<div style="{M};font-size:{n.get('sup_size',20)}px;line-height:1.5">{sup}</div></div></div>'''
def page(w, h):
    v = h > w
    k = len(cfg['nights']); cw = (((w - (160 if v else 200)) - 24 * (k - 1)) / k) * (1 if v else 0.5) - (64 if v else 40)
    fs = int(min(84, min(cw / (len(n['head']) * 0.5) for n in cfg['nights'])))
    nsup = max(len(n['support']) for n in cfg['nights'])
    cards = ''.join(card(n, v, fs, nsup) for n in cfg['nights'])
    grid = (f'left:80px;right:80px;top:700px;bottom:110px;grid-template-columns:repeat({len(cfg["nights"])},minmax(0,1fr))' if v
            else f'left:100px;right:100px;top:380px;bottom:90px;grid-template-columns:repeat({len(cfg["nights"])},minmax(0,1fr))')
    head = (f'''<div style="position:absolute;left:80px;right:80px;top:380px;display:flex;flex-direction:column;gap:22px;text-shadow:0 2px 14px rgba(0,0,0,.7)">
<div style="{M};font-size:28px">{cfg['dates']}</div>
<div style="{C};font-size:104px;line-height:.9;letter-spacing:-1px">BU HAFTA<br><span style="color:{acc}">{cfg['venue_title']}</span></div></div>''' if v else
            f'''<div style="position:absolute;left:100px;right:100px;top:150px;display:flex;justify-content:space-between;align-items:flex-end;text-shadow:0 2px 14px rgba(0,0,0,.7)">
<div style="{C};font-size:80px;line-height:.92;letter-spacing:-1px">BU HAFTA<br><span style="color:{acc}">{cfg['venue_title']}</span></div>
<div style="{M};font-size:28px;padding-bottom:8px;margin-right:{cfg['logo_w']+40}px">{cfg['dates']}</div></div>''')
    lw = cfg['logo_w'] * (1.25 if v else 1)
    logo = f'<img src="{f(cfg["logo"])}" style="position:absolute;top:{90 if v else 90}px;right:{80 if v else 100}px;width:{lw}px">'
    about = f'<img src="file://{KIT}/assets/aboutevents.png" style="position:absolute;top:{120 if v else 90}px;left:{80 if v else 100}px;height:{64 if v else 56}px">'
    foot = f'<div style="position:absolute;left:{80 if v else 100}px;right:{80 if v else 100}px;bottom:{50 if v else 36}px;display:flex;justify-content:space-between;{M};font-size:{22 if v else 20}px;opacity:.85"><div>{cfg["foot_l"]}</div><div>{cfg["foot_r"]}</div></div>'
    bg = f'<img src="{f(cfg["bg"])}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:{cfg.get("bg_pos","50% 50%")};filter:{cfg.get("bg_filter","none")}"><div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.82),rgba(0,0,0,.45) 45%,rgba(0,0,0,.85))"></div>'
    return f'''<html><head><style>{css}</style></head><body><div style="position:relative;width:{w}px;height:{h}px;overflow:hidden;background:#0b0b0b;color:#fff;font-family:'Archivo'">
{bg}{about}{logo}{head}<div style="position:absolute;display:grid;gap:24px;{grid}">{cards}</div>{foot}</div></body></html>'''
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for name, w, h in [('haftalik_dikey', 1080, 1920), ('haftalik_yatay', 1920, 1080)]:
        p = br.new_page(viewport={'width': w, 'height': h}); hp=f'{out}/{name}.html'; open(hp,'w',encoding='utf-8').write(page(w, h)); p.goto('file://'+os.path.abspath(hp)); p.wait_for_timeout(600)
        png = f'{out}/{name}.png'; p.screenshot(path=png)
        from PIL import Image; Image.open(png).convert('RGB').save(png[:-4] + '.jpg', quality=92); print('ok', png)
    br.close()
