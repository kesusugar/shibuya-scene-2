# Mounting contract: world-placed low shrubs, not seat-local geometry

## Primary integration asset

`models/hachiko_low_shrubs_only_v002.glb`

This GLB contains all six shrubs in the existing surround's WORLD placement. Placement is encoded by a combination of mesh vertices and embedded node translations/rotations. It is **not** a single local shrub centered at (0,0,0), and its mesh-node transforms are **not** identity. “World-placed” must not be mistaken for “all coordinates already baked into each vertex with identity nodes.”

### Axis convention

Authoring uses Blender Z-up meters, with the inherited source XY origin (11.568175521259887, -48.68573220011713) and yaw 35°. Blender exports standard glTF Y-up: a source world point (X,Y,Z) becomes approximately (X,Z,-Y) in glTF coordinates. Keep all embedded node transforms and use the same axis-conversion/loading path as the existing `hachiko-surround` asset.

Do not apply another 35° yaw. Do not translate by the statue reference position again. Do not add the per-segment ground elevation again. These placements are already represented by the two mesh nodes.

Verified embedded mesh nodes in the final shrub-only GLB:

- `street_surround_branch`: glTF translation approximately (10.2514296, 1.2910693, 51.3747978), quaternion rotation (0, 0.30070579, 0, 0.95371699).
- `street_surround_needle`: glTF translation approximately (11.5681753, 0, 48.6857338), quaternion rotation (0, 0.30070579, 0, 0.95371699).

These are the origins of material-batched meshes, NOT six independent shrub root positions. The six actual root anchors are documented in `models/shrub_roots.json` in Blender Z-up authoring/world coordinates.

## Relationship to the parallel seating/rail component

The seating/rail pair is LOCAL geometry with its own placement parent. Do not blindly parent this shrub GLB under that translated/rotated seat parent. The simple integration is separate siblings:

- World-placed shrub GLB: use the existing surround/world asset transform path, preserve its embedded mesh transforms.
- Local seat/rail component(s): use the seating package's own mounting contract and placement transform.
- Original soil and rocks: preserve in their existing world placement.

If a common local parent is required by the application, the integrator must explicitly transform the shrub scene by the inverse of that parent's world transform before reparenting, and verify the resulting world coordinates. Do not guess a new offset or apply both coordinate systems.

## Replacement, never append-on-top

1. Locate the existing `street_surround_branch` and `street_surround_needle` nodes in the OLD surround asset. Remove/disable only these two vegetation nodes. The old `needle` group contains old spherical cores and both needle-color primitives; `needle_light` is a material slot, not necessarily a separate node.
2. Load the new shrub-only GLB once. Ensure the old two nodes are no longer drawn. Avoid name-based deletion that accidentally removes the newly loaded nodes; scope removal to the old asset instance first.
3. The parallel seating update may replace the old `street_surround_stone`, `street_surround_silver`, and `street_surround_panel` roles. That is a separate component contract. Preserve old `street_surround_soil` and `street_surround_rock`.
4. Do not load the full-surround comparison GLB as well. That would duplicate shrubs and could revert/duplicate the new seating/rail component.
5. Large trees, the six generic trees, statue, pavement, walking display, FPS code, QFRONT and Seibu are outside this replacement.

## Integration checks still required

- Exactly six shrubs at the existing roots, no doubled foliage or residual sphere/needle model.
- Stone/rail/soil/rock positions unchanged except the independently authorized seating replacement.
- No double yaw/translation, no jump in height.
- Embedded texture resolves; leaf material remains MASK with cutoff 0.5, double-sided, not transparent BLEND.
- Near and mid-distance app views have stable fine foliage; check mipmapped alpha coverage and shimmer while moving.
- App loader, full-scene lighting/shadows, walking, runtime FPS and draw-call behavior have not been tested in this component-only delivery.
