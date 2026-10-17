# Visual and integration review

- Completed and inspected `01_current_components_oblique.png`: both straight side components appear, granite granularity and vertical joints read, silver dual rails and inclined ties are distinct, feet sit at preview Z=0, horizontal lamp details are non-emissive. No statue, plants, soil, rock or large-tree enclosure is included.
- Completed and inspected `04_candidate_layout_contact_sheet.png`: explicitly labeled unverified; left is a technical plan diagram of two partial strips, not a shaded 3D render; right is the exact authored atlas. No full closed seating ring is claimed.
- Additional close/front/full candidate renders were deliberately stopped after the essential oblique, to release shared render resources. They are NOT presented as completed evidence.
- Both current GLBs and current_pair plus the candidate GLBs passed independent structure/material validation, Blender 4.2.3 reimport and winding checks. Paving preview has one intentional open plane. No negative or ambiguous closed shells.
- Six GLBs were byte-identical to a clean separate-directory rebuild; all seven texture images were byte-identical to regeneration.
- An independent integration-contract review corrected source-Z versus glTF-Y wording and explicitly separated world-baked shrub coordinates from local seating coordinates.

## Not established here

Live Three.js loading, ground contact in the actual sloped scene, shadows with site lighting, camera matching to source photos, exact current-world layout, collisions, path clearance, draw-call budget compliance and interaction regressions remain integration QA. This is not permission to alter large trees, four-sided enclosure, statue scan or terrain.
