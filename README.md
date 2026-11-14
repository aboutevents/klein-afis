# klein-afis

About Events · Klein Phönix ve Kastel haftalık afişleri ve otomatik Instagram story paylaşımı.

- Her Pazar gecesi haftanın afişleri `haftalar/<Pazartesi>_hafta/` klasörüne eklenir (dikey + yatay: haftalık, Cuma, Cumartesi).
- Pazartesi–Cumartesi ~11:00'de GitHub Actions, `plan.json`'a göre story'yi @abouteventsorg hesabına paylaşır (etiketsiz).
  - Pzt / Sal / Çar: haftalık afiş · Sal + Cum: Cuma etkinliği · Per + Cmt: Cumartesi etkinliği
- **Kastel** (`kastel/`): Pazar gecesi `kastel/haftalar/<Pazartesi>_hafta/`'ya afişler eklenir; Pzt–Cmt ~13:00'te aynı workflow paylaşır.
  - Pzt: haftalık · Sal: Çarşamba + Cuma · Çar: Çarşamba · Per: Cumartesi · Cum: Cuma · Cmt: Cumartesi
- Ayrıntılar: [TALIMAT.md](TALIMAT.md)
