#!/bin/sh
# C3a: one variable at a time against the baseline; class masks are shared (they do not depend on the look).
# usage: sh scripts/look-sweep.sh <base url> <out root>   (variants are listed below: name views look-query)
B=${1:-http://127.0.0.1:5182}; O=${2:-evidence/c3a/sweep}
run() {
  name=$1; views=$2; q=$3; d=$O/$name; mkdir -p $d
  for f in evidence/c3a/baseline/*_class.png; do cp -n $f $d/; done
  VIEWS=$views PASSES=beauty node scripts/capture-look.mjs $B $d "$q" > $d/capture.txt 2>&1
  python3 scripts/look-metrics.py $d $d/metrics.json > $d/metrics.txt 2>&1
  echo "$name $(tail -1 $d/metrics.txt | cut -c1-400)"
}
run base   m027,q032,refa,refb ""
run E1     m027,q032,refa "look=dayExposure:0.85"
run E2     m027,q032,refa "look=dayExposure:0.92"
run G1     m027,q032,refa "look=glassEnv:0.5"
run G2     m027,q032,refa "look=glassEnv:1.6"
run W1     m027,q032,refa "look=wallEnv:0.5"
run R1     m027,q032,refa "look=road:0.03"
run R2     m027,q032,refa "look=road:0.07"
run S1     m027,q032,refa "look=sidewalk:0.18"
run N1     refb "look=nightGround:1.5"
run N2     refb "look=nightGround:4"
run K1     refb "look=nightSign:0.5"
