# Hachiko local scene fit

Normal display loads all eight fitted parts: `lottery`, `enclosure`, `finish`, `a8`, `louvre`, `fence`, `tactile`, `kerb`. These are **estimated reconstructions**, not surveyed positions. `?fit=off` restores the original visible facilities and paving. Originals are retained for collision and fallback; only their visible roots are switched after all requested GLBs succeed.

No preview selection is required. The former `fit=preview` URL now shows the same normal scene; `fitparts` is no longer used. A8 and louvre assignment, hidden enclosure dimensions and the connected guidance route are explicit estimates adopted for the owner's scene. No interior/underground function is added.

Each `web/*.json` records metres, rotation, representative ground samples, source basis and estimated details. GLBs already contain world transforms in the existing T.P.15m datum; the loader does not apply them again. Lottery keeps the previous fitted frontage. A8 retains the northern kiosk roof and sides, with a complete local canopy infill and folded side/rear closures to bridge the two roof heights.

The enclosure now has four closed stone sides and a continuous draped soil bed around the retained trunk. Louvre banks sit on a local opaque apron/backpan with end and head closures; only plane01 is covered, and the other 13 planes stay intact. Four white-beam bays follow existing posts, with joint plates and terminal caps; no cropped beam is repeated. Tactile geometry joins the existing southern endpoint, routes around the kiosk and ends at the A8 approach warning pad. Every surface vertex is draped to existing sidewalk/fill geometry. Two local side kerbs leave the opening clear. The existing fan paving and all terrain positions are unchanged.

## Rebuild

Use the locally verified extracted deliveries as the first argument; do not run their bundled scripts. No network or photo input is used by this fitting script.

```powershell
python assets/street/hachiko-fit/source/make_fan_paving.py
blender -b --python-exit-code 1 -P assets/street/hachiko-fit/source/fit_scene.py -- <verified-extracted-packages> lottery
```

Repeat for `a8`, `louvre`, `enclosure`, `finish`, `fence`, `tactile`, `kerb`, then run `python assets/street/hachiko-fit/source/write_manifest.py`. Blender 5.2.2 and existing Python/Pillow/NumPy were used. [Source rights](source/RIGHTS.md) records source terms; the separate rear-tree folder contains its own attribution and supplied provenance.
