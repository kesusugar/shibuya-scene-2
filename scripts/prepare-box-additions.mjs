// Run from repository root. Reuse authored geometry; no Blender regeneration.
import {batchGlb} from './batch-box-glb.mjs';
import {Matrix4} from 'three';
const incoming='assets/street/props/incoming/', out='assets/street/box-contents/';
await batchGlb(out+'source/originals/tkts.glb',out+'web/tkts.glb');
for(const [src,dest] of [
 ['shibu_hachi_box_soffit_dome_fixture/output/soffit_dome_fixture.glb','soffit-dome'],
 ['shibu_hachi_box_information_header/output/shibu_hachi_box_information_header.glb','information-header'],
 ['shibu_hachi_box_corner_dome_visible_fragment/output/corner_dome_visible_fragment.glb','corner-dome'],
 ['shibu_hachi_counter_info_placard/shibu_hachi_counter_info_placard.glb','info-placard'],
]) await batchGlb(incoming+src,out+`web/${dest}.glb`);
const placements=[.05,1.05].map(y=>new Matrix4().makeTranslation(-5.94,2.584-.2969922721,-y)
 .multiply(new Matrix4().makeRotationY(-Math.PI/2)));
await batchGlb(incoming+'shibu_hachi_box_display_spotlight/output/shibu_hachi_box_display_spotlight.glb',out+'web/display-spotlights.glb',placements);
// Mounts remain in web/layout.json; spotlights above are baked BOX-local, not world.
