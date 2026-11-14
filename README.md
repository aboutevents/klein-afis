# klein-afis

About Events · Klein Phönix haftalık afişleri ve otomatik Instagram story paylaşımı.

- Her Pazar gecesi haftanın afişleri `haftalar/<Pazartesi>_hafta/` klasörüne eklenir (dikey + yatay: haftalık, Cuma, Cumartesi).
- Pazartesi–Cumartesi ~11:00'de GitHub Actions, `plan.json`'a göre story'yi @abouteventsorg hesabına paylaşır (etiketsiz).
  - Pzt / Sal / Çar: haftalık afiş · Sal + Cum: Cuma etkinliği · Per + Cmt: Cumartesi etkinliği
- Ayrıntılar: [TALIMAT.md](TALIMAT.md)
