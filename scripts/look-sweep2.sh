#!/bin/sh
# C3a second round after the envMap fix (glass/wall intensity now takes effect) and the night ground range.
B=${1:-http://127.0.0.1:5182}; O=${2:-evidence/c3a/sweep}
run() {
  name=$1; views=$2; q=$3; d=$O/$name; rm -rf $d; mkdir -p $d
  for f in evidence/c3a/baseline/*_class.png; do cp $f $d/; done
  VIEWS=$views PASSES=beauty node scripts/capture-look.mjs $B $d "$q" > $d/capture.txt 2>&1
  python3 scripts/look-metrics.py $d $d/metrics.json > $d/metrics.txt 2>&1
  echo "$name done"
}
run base2  m027,q032,refa ""
run G1     m027,q032,refa "look=glassEnv:0.5"
run G2     m027,q032,refa "look=glassEnv:1.6"
run W1     m027,q032,refa "look=wallEnv:0.5"
run N3     refb "look=nightGround:0.5"
run N4     refb "look=nightGround:0.8"
