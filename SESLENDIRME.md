# Mehir · ElevenLabs seslendirme metni (15 sn video)

## Zamanlama

| Video | Ekranda | Ses |
|---|---|---|
| 0.0 – 2.4 | Alev, "mehir kapında" | Mehir… artık kapında. |
| 2.4 – 4.8 | Kart duvarı, "Közün en lezzetli hali" | Közün en lezzetli hali. |
| 4.8 – 7.2 | Telefon, "mehir bir tık uzağında" | Şimdi, sadece bir tık uzağında. |
| 7.8 | Küp: Yemeksepeti | Yemeksepeti'nde, |
| 8.6 | Küp: Trendyol Go | Trendyol Go'da, |
| 9.5 | Küp: Migros Yemek | Migros Yemek'te, |
| 10.4 | Küp: Getir | ve Getir'de. |
| 11.4 – 15.0 | Gece tabelası, "Köz bizden sofra senden" | Köz bizden, sofra senden. Mehir Ocakbaşı. |

## ElevenLabs'e yapıştırılacak metin

```
Mehir... artık kapında. <break time="0.8s" />
Közün en lezzetli hali. <break time="0.8s" />
Şimdi, sadece bir tık uzağında. <break time="0.5s" />
Yemeksepeti'nde, <break time="0.3s" /> Trendyol Go'da, <break time="0.3s" /> Migros Yemek'te, <break time="0.3s" /> ve Getir'de. <break time="0.7s" />
Köz bizden, sofra senden. <break time="0.4s" /> Mehir Ocakbaşı.
```

## Ayarlar

- Model: Eleven Multilingual v2 (Türkçe telaffuz en oturaklı). v3 kullanırsan `<break>` yerine satır sonlarında `...` bırak.
- Ses: erkek, tok, sıcak, orta yaş. Reklam bağırması değil, sakin ve kendinden emin.
- Stability 45 · Similarity 75 · Style 20 · Speaker boost açık
- Hız 1.0. Toplam süre 14 sn'yi geçerse 1.05 yap.

## Montajda

- "Yemeksepeti'nde" kelimesini 7.8. saniyeye oturt, kalan üç platform kendiliğinden küp dönüşlerine yakın düşer. Kaçarsa her platformu ayrı kesip dönüş anına kaydır (8.6, 9.5, 10.4).
- "Köz bizden" 11.6. saniyede başlasın.
