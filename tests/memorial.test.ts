import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { Group, Mesh, MeshBasicMaterial, MeshStandardMaterial, BoxGeometry } from 'three';
import { NodeIO } from '@gltf-transform/core';
import { loadMemorial } from '../src/world/memorial';
import { applyClassPass, classify, CLASS_COLORS } from '../src/world/look';

const placement = JSON.parse(readFileSync('assets/street/hachiko-memorial/web/placement.json', 'utf8'));

describe('Hachiko memorial replacement', () => {
  it('uses the former panel anchor, once, without moving the adopted statue', () => {
    const surround = JSON.parse(readFileSync('assets/street/hachiko-surround/source/data/layout.json', 'utf8'));
    const statue = JSON.parse(readFileSync('assets/street/hachiko/source/data/layout.json', 'utf8'));
    expect(surround.panel.replaced_by).toBe('street/hachiko-memorial');
    expect(placement.uniform_scale).toBe(1);
    expect(placement.position.every(Number.isFinite)).toBe(true);
    const a = statue.yaw_deg * Math.PI / 180;
    const [x, y] = surround.panel.xy_local;
    expect(x + surround.panel.width_m / 2).toBeLessThan(surround.segments[0].x0 - 0.05);
    const stats = JSON.parse(readFileSync('assets/street/hachiko-surround/source/data/stats.json', 'utf8'));
    expect(stats.items.find((r:{id:string}) => r.id === 'stone-panel').contact_samples).toHaveLength(6);
    expect(placement.position[1]).toBeCloseTo(stats.items.find((r:{id:string}) => r.id === 'stone-panel').anchor_tp - 15, 5);
    expect(placement.position[0]).toBeCloseTo(statue.xy[0] + x * Math.cos(a) - y * Math.sin(a), 5);
    expect(placement.position[2]).toBeCloseTo(-statue.xy[1] - x * Math.sin(a) - y * Math.cos(a), 5);
    expect(placement.yaw_deg).toBe(statue.yaw_deg);
  });

  it('loads and isolates failures', async () => {
    const scene = new Group();
    scene.add(new Mesh(new BoxGeometry(), new MeshStandardMaterial()));
    scene.name = 'hachiko_memorial_bilingual_v001';
    const result = await loadMemorial(async () => scene, async () => placement);
    expect(result.ok).toBe(true);
    expect(scene.position.toArray()).toEqual(placement.position);
    expect(result.stats.meshes).toBe(1);
    applyClassPass(result.root);
    expect(((scene.children[0] as Mesh).material as MeshBasicMaterial).color.getHex()).toBe(CLASS_COLORS.wall);
    const failed = await loadMemorial(async () => { throw Error('unavailable'); }, async () => placement);
    expect(failed.ok).toBe(false);
    expect(failed.root.children).toHaveLength(0);
  });

  it('ships the memorial GLB with a single model root', async () => {
    const root = (await new NodeIO().read('assets/street/hachiko-memorial/web/hachiko-memorial.glb')).getRoot();
    expect(root.listNodes().filter(n => n.getName() === 'hachiko_memorial_bilingual_v001')).toHaveLength(1);
    expect(root.listMeshes().length).toBeGreaterThan(0);
    for (const material of root.listMaterials()) {
      expect(classify(new MeshStandardMaterial({ name: material.getName() }), 'hachiko_memorial')).toBe('wall');
    }
  });
});
