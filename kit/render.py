"""Klein Phönix afiş çizici.

Kullanım:  python3 render.py <KIT_KLASORU> <HAFTA_KLASORU>

HAFTA_KLASORU içindeki her *.html dosyasını aynı adla PNG ve JPG olarak çizer.
- "assets/..." yolları KIT_KLASORU/assets altından,
- "foto/..." yolları HAFTA_KLASORU/foto altından okunur.
- {{accent}} ve {{dim}} şablondaki varsayılan değerlerle doldurulur.
Boyut, dosyadaki "$preview" (1080x1920 dikey / 1920x1080 yatay) değerinden alınır.
Gerekenler: python playwright + chromium (pip install playwright; playwright install chromium).
"""
import re, json, os, sys, glob
from playwright.sync_api import sync_playwright

kit = os.path.abspath(sys.argv[1]); week = os.path.abspath(sys.argv[2])
F = f"{kit}/fonts"
css = f"""@font-face{{font-family:'Archivo';src:url('file://{F}/archivo-latin-wdth-normal.woff2') format('woff2');font-weight:100 900;font-stretch:62% 125%;unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}}
@font-face{{font-family:'Archivo';src:url('file://{F}/archivo-latin-ext-wdth-normal.woff2') format('woff2');font-weight:100 900;font-stretch:62% 125%;unicode-range:U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}}
@font-face{{font-family:'IBM Plex Mono';src:url('file://{F}/ibm-plex-mono-latin-600-normal.woff2') format('woff2');font-weight:400 700;unicode-range:U+0000-00FF,U+2000-206F,U+20AC,U+2122,U+2192}}
@font-face{{font-family:'IBM Plex Mono';src:url('file://{F}/ibm-plex-mono-latin-ext-600-normal.woff2') format('woff2');font-weight:400 700;unicode-range:U+0100-02AF,U+1E00-1EFF}}
body{{margin:0}}"""

def fix(m):
    p = m.group(2)
    base = kit if p.startswith("assets/") else week
    full = os.path.join(base, p)
    if not os.path.exists(full):
        raise SystemExit(f"EKSIK DOSYA: {full}")
    return f'{m.group(1)}"file://{full}"'

files = sorted(glob.glob(f"{week}/*.html"))
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for fp in files:
        src = open(fp, encoding="utf-8").read()
        body = re.search(r"<x-dc>(.*)</x-dc>", src, re.S).group(1)
        body = re.sub(r"<helmet>.*?</helmet>", "", body, flags=re.S)
        props = json.loads(re.search(r"data-props='([^']*)'", src).group(1).replace("&amp;", "&"))
        body = body.replace("{{accent}}", props["accent"]["default"]).replace("{{dim}}", str(props["dim"]["default"]))
        body = re.sub(r'(src=)"((?:assets|foto)/[^"]+)"', fix, body)
        w, h = props["$preview"]["width"], props["$preview"]["height"]
        html = f"<!doctype html><html lang='tr'><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
        tmp = fp[:-5] + ".__render.html"
        open(tmp, "w", encoding="utf-8").write(html)
        pg = br.new_page(viewport={"width": w, "height": h})
        pg.goto("file://" + tmp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
        out = fp[:-5] + ".png"
        pg.screenshot(path=out, clip={"x": 0, "y": 0, "width": w, "height": h})
        # Instagram API yalnızca JPEG kabul eder: aynı görselin .jpg kopyası
        pg.screenshot(path=fp[:-5] + ".jpg", type="jpeg", quality=92, clip={"x": 0, "y": 0, "width": w, "height": h})
        pg.close(); os.remove(tmp); print("ok", out)
    br.close()
