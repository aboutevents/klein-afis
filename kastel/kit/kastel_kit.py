#!/usr/bin/env python3
"""Kastel haftalik/gunluk story + yatay afis cizici (About Events).

Kullanim:  python3 kastel/kit/kastel_kit.py program.json kastel/haftalar/<PAZARTESI>_hafta

program.json ornegi:
{
 "week_dates": "18–21 KASIM",
 "week_days": "ÇARŞAMBA, CUMA & CUMARTESİ",
 "nights": [
  {"key": "wed", "date": "18 KASIM ÇARŞAMBA", "tag": "RAVIN PROJECT PRESENTS", "tag_short": "RAVIN PROJECT",
   "head": "ANIL VARDARELI", "support": ["BİLGEHAN ÜNVER", "ORKUN GÜRSELOĞLU B2B EREN YZB"],
   "doors": "21:00", "genre": "MELODIC · TECHNO",
   "ig": {"head": ["anilvardareli"], "support": ["bilgehanunver", "orkun", "erenyzb"],
          "org": ["ravinproject"], "other": []}}
 ]
}
"ig" = Instagram kullanici adlari (story'de gorunmeyen etiket). head: headliner(lar)in hesaplari
(grup ise grubun + uyelerin), support: support DJ'ler, org: etkinlik organizatoru/sunan (varsa),
other: diger ilgili hesaplar. Mekan (@kastel_istanbul) her story'ye otomatik eklenir.
Etiket sirasi / sinir (en fazla 20): headliner -> mekan -> organizator -> support -> digerleri;
sinira gelinirse sondan kesilir (mekan ve organizator hep kalir).
"key": wed / fri / sat (baska gece varsa thu / sun; bunlar yalniz haftalik afise girer).
Ciktilar (hafta klasorune): haftalik-story/-yatay, <key>-story/-yatay -> .png + .jpg + 24 sn .mp4,
program.json kopyasi ve plan.json (scripts/post_story.py'nin okudugu gun -> dosya listesi).
Sadece plan.json'u yeniden yazmak (cizmeden):  python3 kastel/kit/kastel_kit.py program.json <klasor> --plan
Gerekenler: python playwright + chromium, Pillow, ffmpeg. Yazi tipleri depodaki kit/fonts'tan okunur.
"""
import json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = Path(__file__).resolve().parent
A = HERE / 'assets'
FONTS = HERE.parent.parent / 'kit' / 'fonts'
RED = '#E8321E'
RGB = (232, 50, 30)
MONO = "font-family: 'IBM Plex Mono', monospace; font-weight: 600"
COND = "font-family: 'Archivo Variable', sans-serif; font-weight: 900; font-stretch: 62%"
PHOTOS = [('amb-booth.jpg', 'contrast(1.15)'), ('amb-crowd.jpg', 'brightness(2) contrast(1.2)'), ('amb-hall.jpg', 'contrast(1.15)')]
CW = 0.475  # yaklasik karakter genisligi (em) Archivo 62% 900


def fit(text, width, maxsize):
    longest = max(len(x) for x in text.split('<br>'))
    return int(min(maxsize, width / (longest * CW)))


def split_b2b(name):
    return name.replace(' B2B ', '<br>B2B ') if ' B2B ' in name else name


def photo_layer(i, shade=0.62):
    f, bf = PHOTOS[i % len(PHOTOS)]
    return f'''<div style="position:absolute;inset:0;overflow:hidden">
<img src="file://{A/f}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:grayscale(1) {bf}">
<div style="position:absolute;inset:0;background:{RED};mix-blend-mode:multiply;opacity:.85"></div>
<div style="position:absolute;inset:0;background:rgba(17,17,17,{shade})"></div></div>'''


def frame(w, h, title_grey, date_line, inner):
    story = h > w
    if story:
        head = f'''<img src="file://{A/'about-logo.png'}" style="position:absolute;top:120px;left:80px;height:64px">
<img src="file://{A/'kastel-logo.png'}" style="position:absolute;top:112px;right:80px;height:80px;filter:brightness(0) invert(1)">
<div style="position:absolute;left:80px;right:80px;top:268px;display:flex;flex-direction:column;gap:22px">
<div style="{MONO};font-size:26px">{date_line}</div>
<div style="{COND};font-size:104px;line-height:.9;letter-spacing:-1px;white-space:nowrap"><span style="color:#BFBFBF">{title_grey}</span> KASTEL&#39;DE.</div></div>'''
        foot = f'''<div style="position:absolute;left:80px;right:80px;bottom:80px;display:flex;justify-content:space-between;{MONO};font-size:24px"><div>KASTEL MAIN STAGE</div><div>@KASTEL_ISTANBUL</div></div>'''
        box = 'left:80px;right:80px;top:540px;bottom:170px'
    else:
        head = f'''<img src="file://{A/'about-logo.png'}" style="position:absolute;top:72px;left:100px;height:56px">
<img src="file://{A/'kastel-logo.png'}" style="position:absolute;top:64px;right:100px;height:72px;filter:brightness(0) invert(1)">
<div style="position:absolute;left:100px;right:100px;top:168px;display:flex;justify-content:space-between;align-items:flex-end">
<div style="{COND};font-size:80px;line-height:.9;letter-spacing:-1px;white-space:nowrap"><span style="color:#BFBFBF">{title_grey}</span> KASTEL&#39;DE.</div>
<div style="{MONO};font-size:26px;padding-bottom:6px">{date_line}</div></div>'''
        foot = f'''<div style="position:absolute;left:100px;right:100px;bottom:44px;display:flex;justify-content:space-between;{MONO};font-size:22px"><div>KASTEL MAIN STAGE</div><div>@KASTEL_ISTANBUL</div></div>'''
        box = 'left:100px;right:100px;top:340px;bottom:96px'
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8">
<style>
@font-face{{font-family:'Archivo Variable';src:url('file://{FONTS}/archivo-latin-wdth-normal.woff2') format('woff2');font-weight:100 900;font-stretch:62% 125%;unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}}
@font-face{{font-family:'Archivo Variable';src:url('file://{FONTS}/archivo-latin-ext-wdth-normal.woff2') format('woff2');font-weight:100 900;font-stretch:62% 125%;unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}}
@font-face{{font-family:'IBM Plex Mono';src:url('file://{FONTS}/ibm-plex-mono-latin-600-normal.woff2') format('woff2');font-weight:400 700;unicode-range:U+0000-00FF,U+2000-206F,U+20AC,U+2122,U+2192}}
@font-face{{font-family:'IBM Plex Mono';src:url('file://{FONTS}/ibm-plex-mono-latin-ext-600-normal.woff2') format('woff2');font-weight:400 700;unicode-range:U+0100-02AF,U+1E00-1EFF}}
html,body{{margin:0;background:transparent}}</style></head><body>
<div style="position:relative;width:{w}px;height:{h}px;overflow:hidden;color:#fff">
{head}
<div style="position:absolute;{box}">{inner}</div>
{foot}</div></body></html>'''


def card(i, n, pad, top, main, sup, supsize, tag):
    return f'''<div style="position:relative;overflow:hidden;background:#111;min-width:0;min-height:0">{photo_layer(i)}
<div style="position:absolute;inset:0;padding:{pad};display:flex;flex-direction:column;justify-content:space-between">
<div style="display:flex;justify-content:space-between;gap:16px;{MONO};font-size:{top}px"><div style="color:{RED}">{n['date']}</div><div style="opacity:.8;text-align:right">{tag}</div></div>
{main}
<div style="{MONO};font-size:{supsize}px;line-height:1.5">{sup}</div></div></div>'''


def weekly(prog, story):
    nights = prog['nights']
    cards = []
    for i, n in enumerate(nights):
        if story:
            hs = fit(n['head'], 832, 104)
            head = n['head'] if hs >= 60 else split_b2b(n['head'])
            hs = fit(head, 832, 104)
            main = f'<div style="{COND};font-size:{hs}px;line-height:.9;white-space:nowrap">{head}</div>'
            sup = ' · '.join(n.get('support', []))
            cards.append(card(i, n, '40px 44px', 24, main, sup, 22, n['tag']))
        else:
            hs = fit(n['head'], 474, 74)
            head = n['head']
            if hs < 52:
                head = split_b2b(n['head'])
                hs = fit(head, 474, 74)
            main = f'<div style="{COND};font-size:{hs}px;line-height:.92;white-space:nowrap">{head}</div>'
            sup = '<br>'.join(n.get('support', []))
            cards.append(card(i, n, '40px 40px', 22, main, sup, 20, n.get('tag_short', n['tag'])))
    k = len(cards)
    grid = (f'grid-template-rows:repeat({k},minmax(0,1fr))' if story else f'grid-template-columns:repeat({k},minmax(0,1fr))')
    inner = f'<div style="position:absolute;inset:0;display:grid;{grid};gap:28px">{"".join(cards)}</div>'
    date_line = f"{prog['week_dates']} · {prog['week_days']}".replace('&', '&amp;')
    return frame(1080 if story else 1920, 1920 if story else 1080, 'BU HAFTA', date_line, inner)


def daily(prog, n, idx, story):
    names = [n['head']] + n.get('support', [])
    rows = []
    for j, nm in enumerate(names):
        txt = split_b2b(nm) if len(nm) > 16 else nm
        if story:
            size = fit(txt, 888, 120 if j == 0 else 84)
            rows.append(f'<div style="{COND};font-size:{size}px;line-height:.98;white-space:nowrap;padding:20px 0;border-top:2px solid rgba(255,255,255,.25)">{txt}</div>')
        else:
            size = fit(txt, 760, 84 if j == 0 else 72)
            rows.append(f'<div style="{COND};font-size:{size}px;line-height:.98;white-space:nowrap;padding:18px 0;border-top:2px solid rgba(255,255,255,.25)">{txt}</div>')
    genre = n.get('genre', '')
    if story:
        body = f'<div style="display:flex;flex-direction:column">{"".join(rows)}</div>'
        top = f'<div style="display:flex;justify-content:space-between;{MONO};font-size:26px"><div style="color:{RED}">{n["tag"]}</div><div style="opacity:.8">MAIN STAGE</div></div>'
        bottom = f'<div style="{MONO};font-size:24px">{genre}</div>'
        pad = '48px'
    else:
        body = f'<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:56px">{"".join(rows)}</div>'
        top = f'<div style="display:flex;justify-content:space-between;{MONO};font-size:24px"><div style="color:{RED}">{n["tag"]}</div><div style="opacity:.8">{genre}</div></div>'
        bottom = '<div></div>'
        pad = '44px 56px'
    inner = f'''<div style="position:absolute;inset:0;background:#111;overflow:hidden">{photo_layer(idx)}
<div style="position:absolute;inset:0;padding:{pad};display:flex;flex-direction:column;justify-content:space-between">{top}{body}{bottom}</div></div>'''
    date_line = n['date'] + (f" · KAPI {n['doors']}" if n.get('doors') else '')
    return frame(1080 if story else 1920, 1920 if story else 1080, 'BU GECE', date_line, inner)


def render(html, w, h, out_base):
    out_base.parent.mkdir(parents=True, exist_ok=True)
    hp = out_base.with_suffix('.html')
    hp.write_text(html)
    ov = out_base.with_name(out_base.name + '-overlay.png')
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--allow-file-access-from-files'])
        pg = b.new_page(viewport={'width': w, 'height': h})
        pg.goto(f'file://{hp}')
        pg.wait_for_load_state('networkidle')
        pg.evaluate('document.fonts.ready')
        pg.wait_for_timeout(600)
        pg.screenshot(path=str(ov), omit_background=True)
        b.close()
    stop, sh, cell = (448, 40, 20) if h > w else (272, 36, 18)
    sw = w + 160
    strip = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
    px = strip.load()
    for y in range(sh):
        for x in range(sw):
            if ((x % cell) >= cell / 2) != ((y % cell) >= cell / 2):
                px[x, y] = (17, 17, 17, 255)
    sp = out_base.with_name(out_base.name + '-strip.png'); strip.save(sp)
    scan = Image.new('RGBA', (w, h + 16), (0, 0, 0, 0))
    for y in range(0, h + 16, 8):
        scan.paste((0, 0, 0, 18), (0, y, w, min(y + 2, h + 16)))
    sc = out_base.with_name(out_base.name + '-scan.png'); scan.save(sc)
    v = 'clip(clip((val/255-0.5)*1.2+0.5,0,1)*1.3,0,1)'
    lut = ':'.join(f"{c}='({v}*{RGB[i]}*0.75+{RGB[i]}*0.25)'" for i, c in enumerate('rgb'))
    base = (f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30,"
            f"colorchannelmixer=.2126:.7152:.0722:0:.2126:.7152:.0722:0:.2126:.7152:.0722:0,format=rgb24,lutrgb={lut}[bg];")
    anim = base + (f"[bg][3:v]overlay=x=0:y='-mod(t*16/1.2,16)'[a];[a][2:v]overlay=x='-mod(t*80/2.5,80)':y={stop}[b];"
                   f"[b][1:v]overlay=0:0,format=yuv420p[out]")
    ins = ['-i', str(A / 'bg24.mp4'), '-loop', '1', '-i', str(ov), '-loop', '1', '-i', str(sp), '-loop', '1', '-i', str(sc)]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', anim, '-map', '[out]', '-t', '24', '-r', '30',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-movflags', '+faststart', str(out_base) + '.mp4'], check=True)
    still = base + f"[bg][3:v]overlay=0:0[a];[a][2:v]overlay=0:{stop}[b];[b][1:v]overlay=0:0,format=rgb24[out]"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '5', *ins, '-filter_complex', still, '-map', '[out]',
                    '-frames:v', '1', str(out_base) + '.png'], check=True)
    Image.open(str(out_base) + '.png').convert('RGB').save(str(out_base) + '.jpg', quality=92)
    for f in (hp, ov, sp, sc):
        f.unlink(missing_ok=True)


VENUE = 'kastel_istanbul'
MAX_TAGS = 20  # Instagram API: medya basina en fazla 20 etiket


def _clean(xs):
    seen, out = set(), []
    for x in xs:
        x = (x or '').strip().lstrip('@').lower()
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out


def tags_for(nights):
    """Oncelik: headliner(lar) -> mekan -> organizator -> support -> diger; en fazla MAX_TAGS."""
    ig = [n.get('ig', {}) for n in nights]
    head = _clean([u for g in ig for u in g.get('head', [])])
    org = _clean([u for g in ig for u in g.get('org', [])])
    rest = _clean([u for g in ig for u in g.get('support', [])] + [u for g in ig for u in g.get('other', [])])
    fixed = _clean([VENUE] + org)
    head = [u for u in head if u not in fixed]
    rest = [u for u in rest if u not in fixed and u not in head]
    room = MAX_TAGS - len(fixed)
    head = head[:room]
    rest = rest[:max(0, room - len(head))]
    return head + fixed + rest


def write_plan(prog, out):
    nights = {n['key']: n for n in prog['nights']}
    item = lambda f, ns: {'file': f, 'tags': tags_for(ns)}
    has = lambda k: [item(f'{k}-story.png', [nights[k]])] if k in nights else []
    plan = {
        'pazartesi': [item('haftalik-story.png', prog['nights'])],
        'sali': has('wed') + has('fri'),
        'carsamba': has('wed'),
        'persembe': has('sat'),
        'cuma': has('fri'),
        'cumartesi': has('sat'),
    }
    (out / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    (out / 'program.json').write_text(json.dumps(prog, ensure_ascii=False, indent=1))


def main():
    prog = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2]).resolve()
    if '--plan' in sys.argv[3:]:
        write_plan(prog, out); print((out / 'plan.json').read_text()); return
    render(weekly(prog, True), 1080, 1920, out / 'haftalik-story')
    render(weekly(prog, False), 1920, 1080, out / 'haftalik-yatay')
    for i, n in enumerate(prog['nights']):
        render(daily(prog, n, i, True), 1080, 1920, out / f"{n['key']}-story")
        render(daily(prog, n, i, False), 1920, 1080, out / f"{n['key']}-yatay")
    write_plan(prog, out)
    print('\n'.join(sorted(str(p) for p in out.glob('*.png'))))


if __name__ == '__main__':
    main()
