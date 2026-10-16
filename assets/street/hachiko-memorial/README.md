# Hachiko memorial panel

`web/hachiko-memorial.glb` is the four-primitive model from
`hachiko_memorial_bilingual_v001_20261016.zip` (Drive file
`1vt5OAwlY00wnj6jCwUIGutHIGCeGUAcM`), SHA-256 of ZIP
`7bb7dc92af6928dfb2befdefccde44ca3ec1fe2327cd38d40c2e06336bc83a22`.
The source archive was checked for byte size, SHA-256, every ZIP CRC and each
listed manifest file before importing this GLB. The source ZIP and unneeded
photos are deliberately outside the repository.

This replaces only the former `stone_panel` and `unread_inscription` source
parts of `street/hachiko-surround`. It does not alter the statue scan, pedestal,
surrounding walls, rails or shrubs. `web/placement.json` carries a single
uniform-scale transform, derived from the previous panel's local frame and
the statue layout. The centre is shifted 0.35 m outward because the 1.60 m
replacement would otherwise intersect the existing stone border and shrubs.
The ground Y is the lowest of six sidewalk contact samples over the revised
footprint. The panel's metric dimensions and resulting site placement
are estimates; the memorial source photo was captured 2025-07-13. The rest of
the scene includes sources from other dates, so this is a mixed-date view.

Photo-derived front: RuinDig/Yuki Uchida,
[Wikimedia Commons, Tokyo-Shibuya-and-Shinbashi---2025-07-13_090.jpg](https://commons.wikimedia.org/wiki/File:Tokyo-Shibuya-and-Shinbashi---2025-07-13_090.jpg),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The original photo
is projectively mapped and cropped on newly authored geometry; no lettering is
reconstructed. Model and original hidden-side texture:
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), as stated in
the package `PROVENANCE.md`. No endorsement is implied.
