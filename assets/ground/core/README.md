# Core ground (C2a)

This asset is the ground of the Shibuya Scramble Core, within 150 m of the crossing centre (OSM node/291758776).
It fixes positions and heights only. The materials are flat placeholder colours until the C3 material pass.

## What it contains
| Object | Source |
|---|---|
| `ground_road`, `ground_intersection` | PLATEAU 2025 road surfaces, LOD3 (車道部 and 車道交差部), at PLATEAU heights |
| `ground_sidewalk` | PLATEAU 2025 歩道部 and 島, see "Sidewalks" below |
| `ground_kerb` | Kerb faces, plus 0.3 m skirts, see "Kerbs and skirts" below |
| `ground_marking` | Zebra bars of the OSM-marked crosswalks, see "Crosswalks" below |
| `ground_fill` | **Provisional** ground (purple-grey), see "Fill" below |

### Sidewalks
- Densified so that no edge is longer than 1.5 m.
- Lifted 0.15 m above the road.
- Drop to 0.02 m within 1 m of a crosswalk band, then ramp back up over the next 1.5 m.

### Kerbs and skirts
- A kerb face is built wherever a sidewalk edge meets the road.
- Every other open edge gets a 0.3 m skirt that hides the seam.

### Crosswalks
- Zebra bars are 0.45 m wide with 0.45 m gaps, and run parallel to the walking direction.
- They are clipped to the road and draped 12 mm above it.
- Widths and centre lines were measured on the GSI orthophoto.

### Fill
- `ground_fill` covers ground that PLATEAU's road data leaves out, such as forecourts and plazas.
- It sits at sidewalk level and excludes building footprints.
- Within 50 m of the centre it is 1.7 % of the area.

## Datum
- The GLB is already in the common datum, world Y = T.P. − 15.000 m, so it is placed at the origin.
- Each building is placed by its `viewer.json` `groundElevationTP`: Y = elevationTP − 15.000.
- The elevation is the lowest finished ground just outside the building's PLATEAU footprint, so no base floats. It is measured by `source/blender/ground_anchor.py` and written to `source/data/ground_anchors.json`.

| Building | Offset | Roof vs PLATEAU |
|---|---|---|
| QFRONT | +0.202 m | +0.10 m |
| MAGNET and Eiraku | −0.093 m | +0.35 m |

## Rebuild
Run these from `assets/ground/core`:

```
python3 source/tools/measure_crosswalks.py <old shibuya-scene-data.json> <GSI z18 tiles dir> source/data/crosswalks_measured.json
python3 source/tools/prepare_ground.py <plateau_core.json> source/data/crosswalks_measured.json source/data/ground_input.json 150
blender -b -P source/blender/build_ground.py -- source/data/ground_input.json web/ground_core.glb source/data/ground_stats.json
blender -b -P source/blender/ground_anchor.py -- web/ground_core.glb <plateau_core.json> source/data/ground_anchors.json
python3 source/tools/write_manifest.py <53393596_tran.gml> <plateau_core.json> <old data json>
```

- `plateau_core.json` comes from `tools/core/plateau_core.py` (PLATEAU 2025 Shibuya-ku).

## Not measured yet (checked against photos in C3)
- The kerb height (0.15 m) and the low kerb (0.02 m).
- The zebra bar and gap.
- The default width of crosswalks the orthophoto could not measure.
- Whether the PLATEAU road heights match the pavement seen in photos, to within 5 cm.
- The ground floor of the station corridor block, which may be open.

## Licences
- PLATEAU: 国土交通省 Project PLATEAU, CC BY 4.0 compatible.
- OSM: ODbL, © OpenStreetMap contributors.
- GSI: 出典：国土地理院（シームレス空中写真）. Used as a measurement reference only.
