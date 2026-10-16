import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { BoxGeometry, Group, Mesh, MeshBasicMaterial, MeshStandardMaterial } from 'three';
import { NodeIO } from '@gltf-transform/core';
import { loadRearTree } from '../src/world/rearTree';
import { applyClassPass, classify, CLASS_COLORS } from '../src/world/look';

const placement = JSON.parse(readFileSync('assets/street/hachiko-rear-tree/web/placement.json', 'utf8'));

describe('one Hachiko rear tree', () => {
  it('is behind and left of the statue and stays separate from the six Core trees', () => {
    const statue = JSON.parse(readFileSync('assets/street/hachiko/source/data/layout.json', 'utf8'));
    const street = JSON.parse(readFileSync('assets/street/core/source/data/street_input.json', 'utf8'));
    const trees = street.features.filter((f: {kind: string}) => f.kind === 'tree');
    expect(trees).toHaveLength(6);
    const [x, up, south] = placement.position;
    expect(x).toBeLessThan(statue.xy[0] - 3);
    expect(-south).toBeGreaterThan(statue.xy[1] + 2);
    expect(Math.min(...trees.map((t: {point: number[]}) => Math.hypot(x - t.point[0], -south - t.point[1])))).toBeGreaterThan(10);
    expect(up).toBeGreaterThan(0.4);
    expect(up).toBeLessThan(0.45);
    expect(placement.uniform_scale).toBe(1);
  });

  it('loads into the normal scene, classifies as vegetation and isolates a missing GLB', async () => {
    const scene = new Group();
    scene.name = 'hachiko_rear_tree_candidate_v001';
    scene.add(new Mesh(new BoxGeometry(), new MeshStandardMaterial({name: 'A08_original_brown_grey_lenticel_bark'})));
    const result = await loadRearTree(async () => scene, async () => placement);
    expect(result.ok).toBe(true);
    expect(scene.position.toArray()).toEqual(placement.position);
    applyClassPass(result.root);
    expect(((scene.children[0] as Mesh).material as MeshBasicMaterial).color.getHex()).toBe(CLASS_COLORS.vegetation);
    const failed = await loadRearTree(async () => { throw Error('missing tree'); }, async () => placement);
    expect(failed.ok).toBe(false);
    expect(failed.root.children).toHaveLength(0);
  });

  it('ships only one A08 root with the authored bark and leaf materials', async () => {
    const root = (await new NodeIO().read('assets/street/hachiko-rear-tree/web/hachiko-rear-tree.glb')).getRoot();
    expect(root.listNodes().filter(n => n.getName() === 'hachiko_rear_tree_candidate_v001')).toHaveLength(1);
    expect(root.listMeshes()).toHaveLength(3);
    for (const material of root.listMaterials()) {
      expect(classify(new MeshStandardMaterial({name: material.getName()}), 'rear_tree')).toBe('vegetation');
    }
  });
});
