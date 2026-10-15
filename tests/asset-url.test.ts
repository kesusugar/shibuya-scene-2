import {it,expect} from 'vitest';
import {assetUrl} from '../src/core/asset-url';
it('loads static scene assets under a Pages project path without double prefixes',()=>{
 expect(assetUrl('/buildings/qfront/qfront.glb','/shibuya-scene-2/')).toBe('/shibuya-scene-2/buildings/qfront/qfront.glb');
 expect(assetUrl('/shibuya-scene-2/env/day.hdr','/shibuya-scene-2/')).toBe('/shibuya-scene-2/env/day.hdr');
 expect(assetUrl('/ground/core/a.glb','/')).toBe('/ground/core/a.glb');
});
it('does not rewrite embedded textures, external or relative paths',()=>{
 for(const url of ['blob:https://example.org/1','data:image/png;base64,123','https://example.org/a','//example.org/a','image.png'])expect(assetUrl(url,'/project/')).toBe(url);
});
