# SHIBUHACHIBOX counter Tourist Information placard

Standalone, unplaced sign from the front-right of the visitor counter. The board and artwork are newly authored; no source photograph pixels, map, QR code, mascots or advertising posters are included.

## Deliverables and regeneration
- `shibu_hachi_counter_info_placard.glb`: glTF 2 binary, embedded own-authored PNG, standard PBR, non-emissive, Y-up export.
- Same-name `.blend`: editable Blender 4.2.3 scene with packed image.
- `regenerate.py`: run `blender -b -t 2 --python regenerate.py -- /path/to/output` from the extracted directory. Uses adjacent `placard_albedo.png`; no extra Python packages required by the Blender generator.
- `make_texture.py`: optional artwork regeneration using Python Pillow, system DejaVu and Noto Sans CJK fonts. Font paths are explicit. Fonts themselves are not bundled; license notices are included. The delivered PNG is sufficient for portable Blender regeneration.
- `renders/front.png`, `side.png`, `oblique.png`: model-only inspection images. The side is intentionally very thin.
- `logs/build.log`, `validation.json` and `glb_validation.json`: generation and structural checks.

## Evidence and uncertainty
Principal reference: JR East andtrip, https://www.andtrip.jp/article/006193.html , article dated 19 September 2024. Reference photo examined locally; not redistributed. Photograph copyright remains with its publisher/photographer and no redistribution permission is asserted.

Visible content reproduced: blue rectangular field with rounded white border, pale circular field and red italic lowercase `i`, white `Tourist Information` and `観光案内所`. The main words are legible; the tiny footer in the source is unreadable and deliberately omitted. Typeface, exact tracking, colors, corner radii and icon proportions are approximations, not traced artwork. The source shows a slight bend/creased corner which is not represented by this rigid nominal board. No authentication or official-information service is implemented.

This is a **2024-reference variant**. Continued presence and appearance after construction in 2026 are unverified. Do not represent it as a current measured survey.

## Dimensions and attachment
Width 0.340 m, height 0.450 m, total thickness 0.0031 m. All are estimates from photo proportions relative to the counter's estimated 0.98 m height; no scale ruler or rectified camera is available. Plausible width/height ranges are 0.28–0.38 / 0.38–0.50 m. Thickness and back finish are assumed.

Metres; bottom-centre origin at (0,0,0); front is Blender -Y. No scene placement is encoded. For the separate 2.40 × 0.56 × 0.98 m counter, a rough initial attachment translation in its Blender local frame is (0.79,-0.283,0.43), zero rotation. This places the placard near the front-right, below the top. It is only a starting estimate, not a measured or approved placement; verify the actual counter surface and avoid coplanar faces. See `attachment_hint.json`. Codex/user owns runtime integration.

## Fidelity and QA scope
14 triangles, 2 materials, one embedded 768 × 1024 texture. Front preview manually inspected: both English lines and all five Japanese characters render correctly. Geometry origins, accessors and embedded-image presence were checked. A successful export is not a claim of full Three.js scene/FPS validation. No runtime code, existing models, protected buildings, or walking/FPS behavior changed.
