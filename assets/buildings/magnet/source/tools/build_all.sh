#!/usr/bin/env bash
# Rebuild MAGNET end to end: sign art, day/night .blend, the three web GLBs, emissive tables, final renders, boards, manifests.
#   BLENDER=/path/to/blender bash tools/build_all.sh [--no-renders]
set -euo pipefail
cd "$(dirname "$0")/.."
B=${BLENDER:-blender}; W=../web; E=../../eiraku/web
python3 tools/make_signs.py textures/
for m in day night; do "$B" -b -P blender/build_magnet.py -- blend $m final view=m027 save norender | grep RENDERED; done
"$B" -b blend/magnet_night.blend -P blender/export_web.py -- $W/magnet.glb 01_,02_,03_,04_,05_,06_ | grep EXPORTED
"$B" -b blend/magnet_night.blend -P blender/export_web.py -- $W/magnet_signs_2025.glb 08_SIGNS_2025 | grep EXPORTED
"$B" -b blend/magnet_night.blend -P blender/export_web.py -- $E/eiraku.glb 07_ | grep EXPORTED
for m in day night; do "$B" -b blend/magnet_$m.blend -P blender/export_web.py -- --table-only $W/emissive_$m.json | grep TABLE; cp $W/emissive_$m.json $E/; done
if [ "${1:-}" != "--no-renders" ]; then
  for a in "day final view=m027" "night final view=m027" "day final view=sw" "night final view=sw" "day final view=west" "day final view=m027 era=none"; do
    "$B" -b -P blender/build_magnet.py -- renders/v1 $a | grep RENDERED
  done
  python3 tools/roi_metric.py refs/raw/M027.jpg renders/v1/day_m027_final.png ../renders/v1/roi_day_m027.json
  python3 tools/board.py refs/raw/M027.jpg renders/v1/day_m027_final.png ../renders/v1 day_m027
fi
python3 tools/write_manifest.py
