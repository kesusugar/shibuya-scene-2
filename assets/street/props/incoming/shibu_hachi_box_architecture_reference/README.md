# SHIBU HACHI BOX architecture — standalone reference module

## Status
Original architectural reconstruction, **unplaced**. No existing kiosk or plaza-facilities geometry is replaced. No runtime loader, placement, collision, walking, FPS, QFRONT or Seibu code is changed. Operator plan plus exterior observations inform the model. The wide existing plaza-kiosk footprint is not a verified identity match.

This is NOT a full current-plaza reconstruction and NOT an exact October 2025 advertisement state. Architecture was documented in 2024 and corroborated by an August 2026 photograph. User allows present-day appearance specifically around Hachiko; that does not prove every part of the plaza construction has finished.

## Contents and regeneration
Run Blender **4.2.3** in background with `--python source/generate.py -- --output output --render` from this directory. No network, add-ons, fonts, source photos or external textures are required. Render files are original model views, not photographs. GLB uses five standard materials, portable alpha glass (not transmission-dependent), no lighting or camera objects. The editable blend preserves named components; exporter batches only temporary mesh copies by material.

Units are metres, Blender Z-up and front -Y; exported GLB Y-up. Architectural object origins are (0,0,0), at the base footprint centre. Model extends below neither floor zero nor the declared slab bottom. The canopy is wider than the base and intentionally not used as the origin reference.

## Dimension evidence and estimates
Verified operator plan dimensions: overall outer horizontal 12.559 m; column-centre span 12.259 m; wall-centre span 12.206 m; three 3.853 m bays with two 0.350 m inter-bay divisions; short-side column centres 2.222 m, wall centres 2.244 m; overall plan depth 3.572 m including the approach zone. Promotional-space clear height 2.354 m is NOT the full building height.

The model follows a 12.559 × 3.572 m base and 12.206 × 2.244 m wall-centre enclosure. The front and rear wall planes are Y=-0.536 and Y=1.708 m. Interior floor is approximately Z=0.23 m. Differences between structural centre lines and visible enclosure are retained rather than treating every dimension as the same outside edge.

**Estimated, not measured:** roof 12.76 × 3.64 m, top 2.805 m; fascia depth 0.16 m; raised slab 0.23 m; end steps 0.115 m; sign-carrier dimensions and position; front rail height 1.17 m; pane divisions and door width; frame/gasket dimensions; downpipe diameter; panel joints; material reflectance and transparent appearance. End-step shape approximates the stepped approach shown in the plan, not a certified accessibility or fabrication plan.

**Back:** plain rear closure is explicitly inferred. No unobserved vents, service equipment, decorative back graphics or extra entrances are invented. Soffit colour is warm pale, without asserting a timber species or wood structure. Original identifier text only; sponsor, artwork, watches, exhibition furniture, operating signs and date-varying advertisements are omitted.

## Integration handoff
Do not automatically replace the existing approximately 13 m-square plaza-kiosk or approximately 7 m-wide facilities footprint. Integration must first identify existing source objects, reconcile position/yaw and establish duplicate suppression. This package gives no geographic placement coordinates. Preserve the current scene until that reconciliation is complete. A separate Codex-owned integration change is needed.

## Visual comparison (source-linked, no source image redistribution)
Compare `output/front.png`, `side.png`, `oblique.png` and `rear.png` against the operator plan and CASIO source in SOURCES.md. The three-bay frontage, shallow dark roof rim, pale framing, glazed end, raised pale platform and corner downpipe are represented. Glass is deliberately simplified for portable WebGL; rear closure, vertical dimensions and subdivision proportions are estimated. Removed advertising and empty interior mean this is an architectural layer, not a photographic replica. No source-photo montage is distributed because an open redistribution license was not established.
