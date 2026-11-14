# Klein Phönix haftalık afiş + story otomasyonu (About Events)

Depo: github.com/aboutevents/klein-afis (herkese açık — afişler zaten Instagram'da yayınlanıyor).
- `kit/` → şablonlar, yazı tipleri, logolar, arka planlar, `render.py`
- `haftalar/<YYYY-MM-DD>_hafta/` → o haftanın (Pazartesi tarihi) HTML'leri, `foto/`, PNG + JPG afişler, `plan.json`, `paylasim.log`
- `scripts/post_story.py` + `.github/workflows/story.yml` → story paylaşımı (GitHub Actions, Pzt–Cmt ~11:00)

İş bölümü:
- **Pazar gecesi (Claude zamanlanmış görevi, bulutta):** GÖREV A — afişleri hazırla, bu depoya gönder.
- **Her gün ~11:00 (GitHub Actions):** plan.json'a göre story'yi Instagram API ile paylaşır. Claude'un bir şey yapmasına gerek yok.

Genel kurallar (kullanıcının kalıcı tercihleri):
- Türkçe çalış. Marka adı "About Events". İçerikte alkol gösterme. Kullanıcının adını hiçbir içeriğe yazma.
- Story'lerde DJ'ler ve mekân görünmeden etiketlenir (plan.json "tags"); afişin üstüne @isim/çıkartma/link konmaz (API link çıkartmasını desteklemez). "BU GECE" etiketi koyma.

## ETİKET STANDARDI (kullanıcının kalıcı kuralı — Klein, Kastel ve tüm hesaplar için)
- Her story'de o afişte sahne alan TÜM DJ'ler + mekân + (varsa) etkinlik organizatörü / sunan ("X PRESENTS") etiketlenir.
  Grup/kolektif DJ ise grubun hesabı + üyelerinin hesapları. b2b'lerde iki DJ de.
- Instagram sınırı medya başına 20 etiket. "tags" listesi öncelik sırasıyla yazılır:
  1) headliner(lar) → 2) mekân → 3) organizatör → 4) support DJ'ler (afişteki sırayla) → 5) diğer ilgili hesaplar.
  20'yi aşarsa sondan kesilir (post_story.py da kendisi keser); mekân ve organizatör hiçbir zaman düşmez.
- Haftalık afiş: tüm gecelerin headliner'ları → mekân → tüm organizatörler → support'lar.
- Hesapları şuralardan bul ve doğrula: mekânın o etkinlik için yaptığı Instagram gönderisinde etiketlenen/bahsedilen hesaplar
  (en güvenilir), Bugece sanatçı sayfasındaki Instagram linki, RA sanatçı sayfası. Doğrulanamayan hesabı yazma, raporda belirt.
- Sanatçı fotoğrafı: Google Görseller / RA (static.ra.co/images/profiles/square/<slug>.jpg genelde 1440px temiz; indirmede tarayıcı User-Agent'ı ve Referer https://ra.co/ gerekebilir) / basın sayfaları.
  Getty/Alamy filigranlı görselleri kullanma. Beatport `image_size/590x404` görselleri ORANI BOZUK (gerilmiş) olabilir: yüzler basık/geniş görünüyorsa kullanma.
  Mekân/etkinlik afişi kırpılacaksa yazı kısmı girmesin. Çizimden sonra her afişi gözle kontrol et.

## GÖREV A — Pazar gecesi: haftanın afişlerini hazırla

1. Depoyu klonla. Hafta = yarından (Pazartesi) Pazar'a. Klasör: `haftalar/<Pazartesi tarihi>_hafta` (ör. `haftalar/2026-11-16_hafta`).
   Klasörde zaten JPG'ler + plan.json varsa işi tekrarlama, sadece raporla.
2. Etkinlikleri bul: https://bugece.co/tr/venue/klein-phonix (curl/tarayıcı ile erişilebilir). O haftaki her etkinlik sayfasından:
   ad, tarih, kapı saati (Açılış), lineup (headliner + support'lar), kısa açıklama. Set saati genelde yok → afişe sadece "KAPI hh:mm".
3. Sanatçı fotoğraflarını indir → `<hafta>/foto/`.
4. Şablonlardan HTML üret (`kit/templates`, aynı klasöre):
   - `haftalik_dikey.html` / `haftalik_yatay.html` — "BU HAFTA KLEIN PHÖNIX'TE.", her etkinlik için bir kart (tarih "13 KASIM CUMA", isim, alt satır support'lar).
     Şablonda 2 kart var; 1/3/4 etkinlikte kart sayısını/ızgarayı uyarla (yatayda yan yana; dikeyde 3–4 etkinlikte 2×2). Üstteki tarih aralığını güncelle.
   - Cuma etkinliği: `cuma_dikey.html` / `cuma_yatay.html`; Cumartesi: `cumartesi_dikey.html` / `cumartesi_yatay.html`
     (kaynak `gunluk_dikey.html` / `gunluk_yatay.html`). Başlık = headliner, kısa slogan (sound'a atıf, 4–7 kelime, BÜYÜK HARF),
     tarih + "KAPI 22:00", kartlar HEADLINER + SUPPORT (b2b ise "B2B"). Fotoğrafı olmayan support'u alt satıra yaz.
   - Arka planı her hafta değiştir (assets: bg_kirmizi, bg_mor, bg_altin, bg_petrol).
   - Cuma veya Cumartesi etkinliği yoksa o günün dosyalarını üretme.
5. Çiz: `python3 kit/render.py kit haftalar/<hafta>` → her HTML için PNG + JPG. Her PNG'yi aç ve kontrol et.
6. `plan.json` (sadece var olan dosyalar; değerler PNG adı, betik aynı adlı JPG'yi kullanır). Her girdi "dosya.png" ya da etiketli olabilir:
   `{"file": "dosya.png", "tags": ["kullaniciadi", ...]}` — etiketler görselde GÖRÜNMEZ (Instagram user_tags), hesaplar bildirim alır.
   Hesapları Bugece sanatçı/mekân sayfalarındaki Instagram linklerinden al (Klein: phonix.klein, klein.entertainment).
   Haftalık afişte o haftanın tüm DJ'leri + mekân, günlük afişte o gecenin DJ'leri + mekân (+ organizatör). Sıra ve sınır: yukarıdaki ETİKET STANDARDI.
   Örnek (etiketli):
   ```json
   {"pazartesi": [{"file": "haftalik_dikey.png", "tags": ["dj1", "dj2", "phonix.klein", "klein.entertainment"]}],
    "sali": [{"file": "haftalik_dikey.png", "tags": ["..."]}, {"file": "cuma_dikey.png", "tags": ["..."]}],
    "carsamba": [{"file": "haftalik_dikey.png", "tags": ["..."]}],
    "persembe": [{"file": "cumartesi_dikey.png", "tags": ["..."]}], "cuma": [{"file": "cuma_dikey.png", "tags": ["..."]}],
    "cumartesi": [{"file": "cumartesi_dikey.png", "tags": ["..."]}]}
   ```
7. `git add haftalar/<hafta> && git commit -m "Klein afişleri: <hafta>" && git push` (main). Push edilmezse story'ler paylaşılamaz — hata varsa açıkça raporla.
   Ardından PANEL adımları (`to_panel.py klein ...`).
8. TAKİP ÖNERİSİ: Instagram API takip etmeyi ve takip edilenleri görmeyi desteklemez, bu yüzden otomatik takip YAPMA.
   Bu haftanın etiket listesindeki hesaplardan `takip_listesi.txt`'de OLMAYANLARI raporda "Takip edilecek yeni DJ'ler" başlığıyla
   https://instagram.com/<kullaniciadi> linkleriyle listele (yoksa "bu hafta yeni isim yok" yaz), sonra bu hesapları takip_listesi.txt'ye ekleyip commit et.
9. PERFORMANS: depodaki `performans.csv` (her sabah GitHub Actions doldurur: reach=erişim, views=görüntülenme, replies=yanıt,
   navigation=ileri/geri/çıkış dokunuşları, profile_visits=profil ziyareti, follows=takip, shares=paylaşım, total_interactions).
   Raporda GEÇEN HAFTANIN story'lerini özetle: her story için tarih, afiş, erişim, profil ziyareti, takip, yanıt; haftalık toplam/ortalama;
   en iyi ve en zayıf story; Klein ve Kastel ayrı. Önceki haftayla kıyasla (varsa). Veri yoksa nedenini söyle (ör. izin/anahtar sorunu).
10. PNG'leri kullanıcıya gönder (SendUserFile) + kısa Türkçe rapor (SendUserMessage): etkinlikler, her story'nin etiket listesi, bulunamayan hesaplar, eksik bilgi/fotoğraf, haftanın story takvimi.

## PANEL — planı aboutevents.org panelinde göster (Klein ve Kastel, her Pazar)
Kullanıcı haftanın story planını admin > Sosyal paylaşımlar'da görüp düzenlemek istiyor. Afişler push edildikten SONRA:
1. Web deposu: add_repo (owner aboutevents, repo web, access push) → `git clone --depth 1 https://github.com/aboutevents/web /home/claude/web`.
2. `python3 scripts/to_panel.py <klein|kastel> <hafta klasörü> /home/claude/web` — her story için `database/data/social/<hesap>-<tarih>-<dosya>/post.json` yazar
   (görsel bu deponun raw adresinden, etiketler, saat: Klein 11:00 IG · Kastel 13:00 IG+FB).
   Sunucuda Meta anahtarı etkinse (ops-status "meta: … env=var") panel paylaşır: kayıtlar "Planlandı", plan.json'a `"_panel": true` yazılır ve
   GitHub Actions o haftayı atlar (çift paylaşım olmaz). Değilse GitHub paylaşır, panel kayıtları "Durduruldu" (sadece görmek için).
3. plan.json değiştiği için bu depoyu tekrar commit/push et; sonra web deposunda `git add database/data/social && git commit -m "<Hesap> story planı: <hafta>" && git pull --rebase --autostash && git -c push.negotiate=true push origin HEAD:main`.
   Sunucu 5–10 dk içinde içe aktarır. Panelde düzenlenen kayıtların üzerine yazılmaz. Raporda "kim paylaşıyor: panel/GitHub" yaz.

## GÖREV B — story paylaşımı (GitHub Actions)
Otomatik. Elle test: GitHub → Actions → "Klein story paylaşımı" → Run workflow → mode=test (yayınlamaz) veya publish, isteğe bağlı tarih.
Hata olursa GitHub, depo sahibine e-posta ile bildirir. Anahtar: Settings → Secrets and variables → Actions → `IG_TOKEN`.

---

# KASTEL — haftalık afiş + story (aynı sistem)

Kastel afişleri de bu depodan, aynı `scripts/post_story.py` ve aynı workflow ile paylaşılır.
- `kastel/kit/` → `kastel_kit.py` (çizici) + `assets/` (logolar, mekân fotoğrafları, kırmızı arka plan videosu). Yazı tipleri depodaki `kit/fonts`'tan.
- `kastel/haftalar/<YYYY-MM-DD>_hafta/` → o haftanın (Pazartesi tarihi) `program.json`, `plan.json`, PNG + JPG afişler, `paylasim.log`.
  MP4'ler depoya girmez (`.gitignore`); kullanıcıya sohbetten gönderilir.
- Paylaşım: GitHub Actions 09:50 UTC = 12:50 İstanbul (Pzt–Cmt) çalışır, story ~13:00'te düşer (Klein'ınki 10:50'de, ayrı).

Story takvimi (kastel_kit.py plan.json'u kendisi yazar; etkinlik yoksa o gün boş kalır):
- Pazartesi: haftalık · Salı: Çarşamba + Cuma etkinlikleri · Çarşamba: Çarşamba · Perşembe: Cumartesi · Cuma: Cuma · Cumartesi: Cumartesi
- DJ'ler + @kastel_istanbul + (varsa) organizatör görünmeden etiketlenir (ETİKET STANDARDI). Müzik, link yok.

## GÖREV K — Pazar gecesi: Kastel afişlerini hazırla
1. Depoyu klonla. Hafta = yarından (Pazartesi) Pazar'a. Klasör: `kastel/haftalar/<Pazartesi tarihi>_hafta`. Klasörde zaten JPG'ler + plan.json varsa işi tekrarlama, sadece raporla.
2. Etkinlikleri bul: https://bugece.co/tr/venue/kastel → o haftaki her etkinlik sayfasının "LINE-UP" listesi, tarih, Açılış saati, Genre, sunan (ör. "BEATGATE PRESENTS"). Kastel Instagram (@kastel_istanbul) açıklamaları ve aylık takvim görseliyle karşılaştır; çelişkide Bugece LINE-UP'ı esas al, raporda belirt.
3. `program.json` yaz (biçim `kastel_kit.py` başında). İsimler BÜYÜK HARF, Türkçe karakterler doğru; lineup'ı yazıldığı gibi kullan. A–Z (headliner'sız) gecede listedeki ilk isim `head`. b2b'ler "X B2B Y" tek öğe.
   Her geceye `"ig"` ekle: `{"head": [...], "support": [...], "org": [...], "other": [...]}` (Instagram kullanıcı adları, ETİKET STANDARDI).
   Hesapları @kastel_istanbul'un o gece için paylaştığı gönderide etiketlenenlerden al (tarayıcıda gönderiyi aç; sayfa HTML'indeki
   "usertags" ve açıklamadaki @'ler), sonra Bugece/RA ile tamamla. Mekân otomatik eklenir. kastel_kit.py sırayı ve 20 sınırını uygular.
   Sonradan sadece etiket düzeltmek için: `python3 kastel/kit/kastel_kit.py program.json kastel/haftalar/<hafta> --plan` (çizmeden plan.json yazar).
4. Çiz: `python3 kastel/kit/kastel_kit.py program.json kastel/haftalar/<hafta>` (~6 dk; playwright + chromium, Pillow, ffmpeg). Her PNG'yi aç: isim taşması, okunurluk.
5. `git add kastel/haftalar/<hafta> && git commit -m "Kastel afişleri: <hafta>" && git push` (main). Push olmazsa story'ler paylaşılamaz — açıkça raporla.
   Ardından PANEL adımları (`to_panel.py kastel ...`).
6. PNG + MP4'leri kullanıcıya gönder (SendUserFile) + kısa Türkçe rapor: program tablosu, her story'nin etiket listesi, bulunamayan hesaplar, kaynaklar, belirsizlikler, story takvimi.

Elle test: Actions → "Klein story paylaşımı" → Run workflow → hesap=kastel, mode=test (yayınlamaz), isteğe bağlı tarih.
