# ヒカリエ source91 限定補正候補

上部の汎用ガラス格子だけを限定的に整理し、元の淡色・不透明シェルを見せる候補です。906三角形のみを除外し、推定した細い暗色帯と、写真で隠れている下部を含む204三角形は保持。屋根・シェル・隣のsource63・他の建物は変更していません。下部の暗い2段が実物どおりだという主張ではありません。

Geometry, editable-scene parity and portable regeneration validated. Scoped copied-assembly checks passed; this does not claim latest-main or full-scene validation. See docs/REPORT.md and docs/UNCERTAINTY.md.

## Portable byte-exact regeneration
Requirements: Python3.9+ standard library only. From this package directory (or pass the absolute script path from another working directory):

python tools/regenerate.py
python tools/validate.py

The generator reads baseline/hikarie.glb and source/overlay_contract.json relative to its own package directory, writes web/hikarie.glb, and refuses an incorrect baseline or output hash. Optional --output PATH writes elsewhere. No NumPy, browser, network, original repository or external source file is required. All906 removed and204 retained original triangle indices are explicit in the contract.

Expected input SHA256:14cb88b7d3870512c23a750e7b9f701e85dc184cc1d473954725b6c138a0749d
Expected output SHA256:2f4e95126c0d126c8db2d7d8aad4a54d5d0010ba7af0734b357a939077a87721

## Editable Blender scene and rendering
source/hikarie.blend is editable in Blender4.2.3. It contains the candidate geometry/materials, a README text, and no external image textures. The canonical GLB serializer is the Python patch generator, not Blender export: byte-identical GLB serialization is distinct from editable-scene semantic parity. evidence/blend-parity.json proves that imported GLB geometry, oriented triangle positions, corner normals, materials and counts survive save/reopen unchanged.

To recreate the editable scene:
blender --background --python-exit-code 1 --python tools/create_editable.py

To render actual before/after views:
blender --background --python-exit-code 1 --python tools/render.py
Optional arguments after -- select front, west_side or photo_jun15_angle. Cameras and lighting are fixed in source/cameras.json and tools/render.py.

## Publication scope
This is a filtered source package resealed on 2026-10-15. Logs, caches and old integration inventories are excluded. manifest.json inventories the actual package. All before images here compare the intermediate 14cb88b7 source91 baseline, NOT current main. The cumulative current-main comparison and fresh validation are ../../evidence/cumulative-v2/. The current asset README supersedes historical integration guidance.

## Rights
The June2025 crop and boards credit Nesnad,CC BY4.0; exact URLs and crop notes are in docs/SOURCES.json. Other copyrighted references were examined privately and are not packaged. No photographs are used as textures. Third-party photo rights do not transfer rights in the project/model; no new blanket model license is asserted.
