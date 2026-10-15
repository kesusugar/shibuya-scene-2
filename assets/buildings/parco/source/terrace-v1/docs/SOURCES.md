# Sources and reuse boundaries

## Geometry inherited from the accepted project

- PLATEAU building ID: `bldg_e199100f-cb89-4a81-8e38-0abee12cb1d4`.
- Associated OSM way: `451564412`.
- Source rings are preserved in `inputs/source-plateau.json`; SHA-256 `031a66d351a04474ffef5346264e1871f50f6d292bdd898d20bce7ca6bb644a1`.
- Baseline and source geometry retain the accepted project's original attribution/licensing obligations. This candidate does not relicense the building dataset, textures or project. Consult the project's dataset registry for the particular PLATEAU release and OSM attribution. No unverified blanket CC license is asserted.

## Architectural references, links only

These copyrighted materials were used to interpret geometry. Their maps, drawings, photographs, logos and PDF pages are **not embedded or distributed** in the candidate, Blender file, scripts or comparison boards. Numerical model coordinates and residuals are analysis outputs, not reproduced drawing pixels.

1. JSSI seismic-engineering article, dimensioned plans and section:
   https://www.jssi.or.jp/wordpress/wp-content/uploads/2022/08/109-seishinshokai-shibuyaparco.pdf
   Basis for structural dimensions, relative floor increments and sectional interpretation. The exact plan position of the section cut remains uncertain.
2. Official PARCO 4F floor map:
   https://shibuya.parco.jp/floor/detail/?f=4f
3. Official PARCO 5F floor map:
   https://shibuya.parco.jp/floor/detail/?f=5f
4. Official PARCO 6F floor map:
   https://shibuya.parco.jp/floor/detail/?f=6f
   These are circulation/tenant schematics, not survey CAD. Their registration residuals and lift/stair cross-checks are retained in `registration/`.
5. Nikken Sekkei architectural discussion:
   https://www.nikken.jp/ja/insights/expertise/zadankai_shibuya_parco_miyasihta_part1.html
6. PARCO project release:
   https://www.parco.co.jp/pdf/jp/store/storage/cname_20190618101432.pdf
7. Exterior architectural photo context:
   https://archi-cost.com/shibuya/
   Reference only; caption and URL date are not treated as a surveyed capture date.
8. Syced 2024 CC0 photograph, independent exterior reference:
   https://commons.wikimedia.org/wiki/File:Shibuya_Parco.jpg
   No photograph is needed for terrace regeneration. The delivery includes a licensed CC0 crop for comparison, separately attributed in references/PHOTO_SOURCE.json. No photo is used as a texture.

## Reproduction and evidence

The candidate can be regenerated from local numerical inputs with Blender 4.2.3 without downloading any of the above reference images. The original source JSON, accepted baseline and frozen prototype are immutable. Model details remain inferences within the explicitly bounded scope, not a claim that these references prove every support, frame or material parameter.
