// Change one material's PBR factors in a GLB without regenerating its geometry (used when only a colour/finish is
// corrected and a rebuild would also re-sample footing). node scripts/patch-glb-material.mjs file.glb name r,g,b metal rough
import { NodeIO } from '@gltf-transform/core';
const [file, name, rgb, metal, rough] = process.argv.slice(2);
const io = new NodeIO(); const doc = await io.read(file);
const m = doc.getRoot().listMaterials().find((x) => x.getName() === name);
if (!m) throw new Error(`no material ${name}`);
const [r, g, b] = rgb.split(',').map(Number);
m.setBaseColorFactor([r, g, b, 1]).setMetallicFactor(Number(metal)).setRoughnessFactor(Number(rough));
await io.write(file, doc); console.log('patched', name, 'in', file);
