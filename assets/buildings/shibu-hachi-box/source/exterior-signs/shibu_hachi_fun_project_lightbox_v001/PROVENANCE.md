# Evidence and provenance

## Primary observation
CASIO Computer Co., Ltd., official note account: 「渋谷ハチ公前の新名所！？SHIBU HACHI BOX（シブハチボックス）がG-SHOCKに染まります」
https://note-pr.casio.co.jp/n/n848d1c101d53

Published 2024-12-10. The article says the G-SHOCK treatment began on 2024-11-15; that is not a verified photo capture date. The present-day existence and appearance of this small sign are unverified.

The frontal photograph shows a small luminous rounded rectangular box above the right-hand facade bay. The readable lettering is SHIBUYA, FUN, PROJECT. A small graphic immediately before FUN and the fine outline detail are insufficiently resolved. They have not been guessed or copied. The side photograph independently supports the shallow projecting sign's location, not a measured depth.

## Reconstructed and estimated
- Overall dimensions (1.150 × 0.1056 × 0.205 metres), depth, rear closure, colors, material parameters and lighting appearance are estimates.
- Width is a rough photo proportion against the existing pavilion facade width. It is not a survey or manufacturer's dimension.
- The body has a dark rounded rim and a pale mildly emissive acrylic-like face. No claim is made about its actual electrical or internal construction.
- Readable words use Blender's bundled Bfont converted to geometry. Letter proportions are approximate. The simple FUN outline is original geometry, not a traced or extracted brand image.
- A small unresolved graphic and fine outline details are omitted. The model is a scene-scale identification prop, not an exact logo master.

## Duplicate avoidance and placement
The existing shibu_hachi_box_revision/source/generate.py contains the roof SHIBU HACHI BOX identifier and a blank central doorway carrier. The separate shibu_hachi_box_info_header/source/generate.py contains Tourist Information & Souvenir Store. Neither contains this small right-bay project lightbox. Generator hashes are recorded in source_reference.json.

The parent geometry establishes facade direction and pier centers, so a semantic right-bay anchor and rough parent-local X are supplied. Vertical fit against the parent's head/soffit has not been reconciled to the photograph. No complete parent-local or world transform is supplied, and no placement was performed.

## Rights and dependencies
No source photographs, crops, downloaded logos, textures or third-party advertising artwork are distributed. Reference photographs were viewed locally only; hashes and the original public source link are recorded. All delivered geometry and rendering are procedural reconstructions. The brand wording is a factual identifier; no trademark ownership or affiliation is claimed. No external font file or image dependency is required by the generator or GLB.

Only this standalone asset directory and temporary verification output were changed. No protected building models, walking display, FPS, runtime source, GitHub branch/PR, merge or deployment were touched.
