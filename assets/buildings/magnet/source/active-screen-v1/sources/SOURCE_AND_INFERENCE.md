# MAGNET Forum Vision: source, rights, and bounded inference

Review date: 2026-10-14 UTC. Target year: 2025. Only the active image plane is corrected.

## Authoritative dimensions
- PAS operator renewal release, published 2021-03-08: https://pas-com.co.jp/wp/wp-content/uploads/2021/03/news_210308.pdf . Active screen width 8.64 m, height 4.80 m. Specifications are facts used as geometry; no PDF pixels are packaged.
- SHIBUYA109 operator media page independently repeats the dimensions: https://shibuya109square.com/service/109%E3%83%95%E3%82%A9%E3%83%BC%E3%83%A9%E3%83%A0%E3%83%93%E3%82%B8%E3%83%A7%E3%83%B3/ . Undated supporting source, not a dated 2025 photograph.

## Photo-informed relative placement
- HUIS advertiser release, published 2025-10-24 08:10: https://prtimes.jp/main/html/rd/p/000000016.000158371.html . Announces the campaign beginning 2025-10-10. Its unobstructed photograph was actually inspected at 1950 × 1300 pixels.
- Exact capture date is not established by EXIF. Describe it as “the photograph in HUIS's 2025-10-24 release,” not “photographed on 2025-10-24.” A campaign-period capture is contextual inference only.
- Copyright reference-only; no open license was identified. The photo, derivative photo crops, screenshot pixels, and campaign art are **not included** in the model, source inputs, comparison board, or delivery. Only manually recorded geometric observations and newly drawn schematic geometry are included.
- A homography from the visible cassette front to a unit square gives active centre v=0.5712689591579574. Applied to the inherited cassette Z9–32, that is Z18.86081393936698 m. The approved implementation rounds the centre to 18.86 m, bounds Z16.46–21.26. Rounding changes centre by −0.00081394 m before float32 storage.
- Horizontal centre X39.8 and front plane Y8.67 are inherited anchors, not newly calibrated photogrammetric measurements. Existing −Y normal and 0.03 m stand-off are preserved. Float32 Y remains 8.669999122619629 m without modification.

## Important limitations
The inherited cassette is photo-estimated, not a surveyed elevation. Mapping both photographed screen edges to that 23 m cassette would give Z15.76857–21.95306 and a 6.18449 m active height, conflicting with the operator's 4.80 m. The chosen dimension-correct plane remains about 0.69 m from each full-cassette photo-mapped edge. No surrounding geometry is resized to hide the conflict.

Manual-pick sensitivity (10,000 deterministic samples, cassette picks ±6 px, screen ±3 px) gives centre Z18.72–19.00 m at the 5th–95th percentiles. This is **not a real-world confidence interval**. Unknown lens distortion, camera intrinsics, source editing, non-coplanarity, and inherited cassette error are additional.

The actual cassette ribs/vent-band/lower-banner detail, logo shapes, roof, and other building differences visible in the source are not repaired by this narrow correction. Existing geometry stays unchanged; no claim is made that every photographed detail was already modeled. The lower STARTS display is a different installation and is untouched.

## Existing artwork and inherited sources
The accepted source/data/signage_2025.json and asset README identify embedded screen/banner graphics as original placeholder artwork, never photo crops. The existing 760 × 900 led_box image and its UVs/material are preserved byte-for-byte. It is mapped to the corrected landscape quad, so the placeholder is now wider; it is not a reconstruction of the HUIS campaign or another dated advertisement. All other embedded images stay identical.

The companion MAGNET and Eiraku assets preserve their inherited PLATEAU and photo-derived provenance. Their original manifest attribution remains in the repository. No M027 image, blocked Commons original, or certificate-warning source was fetched in this implementation. The inherited M027 camera numbers were used only for repeatable model renders, not as new calibration evidence.
