# Independent Center-gai casing review

## Result
The bounded asset refinement has a visible silhouette improvement: broad shallow, flat-sided tapering casings replace narrow circular hooks, three pale ribs replace each single dark collar, and outlined permanent name panels follow the bend. Two separate posts remain. This is an asset-level review, not full-scene fidelity acceptance.

Reviewed final architecture GLB SHA256: `f20e95cac51cafd108ccbacd6a565be66f074c7f15a7503fd39bd363858e6832`.

## Visual evidence actually inspected
- Original-pixel Jan31, Feb7 and Nov1 crops in center_gai_research/crops, plus historical current-gate.png.
- Fresh isolated same-camera before-front and final after-front, after-side, after-walk renders in center_gai_fidelity/evidence/center-gai-fidelity.
- Candidate had disconnected lamps below its new tips. Reported to modeler; final renders show narrow support necks resolving the gap without moving lamps/banner. Those support details are explicitly inferred, not independently photo-certified.
- Permanent name texture was inspected. Actual approximate Noto Sans CJK JP text, not fabricated unreadable pseudo-glyphs. Typeface/weight/spacing and unknown reverse-side details disclosed.
- Diagnostic render cameras are orthographic and not matched to dated photographs or an existing full-scene camera. Low-angle view has display-plane occlusion in lower half; it is not a walkthrough.

## Independent measurements and checks
- Baseline mesh actual crest: local Y6.5457453728m, versus old incorrectly tips-derived stats6.09577553m. Final actual crest6.5164775848m,29.268mm lower, consistent with new stats. T.P. datum15m unchanged.
- Final2180 triangles/8 primitives, versus baseline2572/5. Final architecture172344 bytes; January layer100104 bytes/4 triangles/1 primitive. Combined2184 triangles/9 primitives/272448 bytes is within existing B budget120000/40/3000000.
- Canonical triangle coordinates identical for bases, banner backing and lamps. Feet and historical ten ground samples retained. No new terrain measurement claimed.
- January layer SHA256 remains `e3d61300241cfc5cf3692739f1a33d994d5abc05f64b703536ec35495852d3ec` byte-identical. No October relabeling. Persistent name is architecture, campaign remains separate.
- Independent21 transverse passage ray checks at heights0.8/1.9/2.3m and seven offsets across central6m all clear. Both posts intersect collision rays at1.9m. Existing banner clearance4.022110939m retained.
- Exact Blender4.2.3 LTS (hash0e22e4fcea03) rebuild in review/rebuild using explicit historic-sample mode `-` produced byte-identical architecture and campaign GLBs.
- Packed blend opened with Blender4.2.3:8 mesh objects; banner and permanent-name images both packed. Architecture source preserved; rebuild requires no installed font unless regenerating the supplied name PNG.
- Independently ran candidate's focused Vitest file:4/4 pass. Additional raw-mesh audit and preservation checks saved alongside this report.
- Reference register supplies dates, authors, Commons URLs, licenses and original SHA256s. Jan/Feb CC0 evidence included. Nov CC BY-SA used as visual research only, no pixels in deliverable texture/board. Noto font not distributed; approximate raster label and font provenance supplied.

## Explicit limits
No fresh full current-scene capture, protected-facade mesh wall-ray audit, runtime asset-load check, signs-off/street-off browser verification, full current-main test suite or owner-PC FPS was performed by this review. Existing wall tests sampled foot+1m and cannot certify new high collars. A supplemental targeted source-footprint check finds zero plan overlap of final gate triangles with QFRONT and all three available Seibu footprints. QFRONT minimum plan separation is0.100799m versus baseline0.145808m,45mm narrower due to ribs; this narrow source-ground-footprint margin does not certify facade overhang/projection clearance. Final gate geometry is wholly separated in X from the latest local west_storefront_fidelity west-block GLB by at least1.022800m (baseline1.067469m), proving no intersection with that mesh regardless elevation. Checks use actual GLB coordinates and supplied source-footprint polygons; neighbors were not modified. Modeler typecheck/build logs use an older source snapshot and must not be called current-main integration validation. QFRONT/Seibu and unrelated assets must remain excluded from changed-only manifest.

Dimensions and typography remain estimates, not survey accuracy. October campaign, lower-pole posters, reverse-face lettering and real night light distribution remain unverified. No remote write or merge performed.
