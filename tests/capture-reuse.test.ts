import { describe, expect, it } from 'vitest';
// @ts-expect-error Small Node capture utility has no declaration file.
import { reuseKey } from '../scripts/capture-reuse.mjs';
describe('capture navigation', () => {
  it('reuses only valid explicit poses with the same scene configuration', () => {
    const a = reuseKey('time=day&pose=1,2,3,0,0,0,55');
    expect(a).toBe(reuseKey('time=night&pose=4,5,6,0,0,0,60'));
    expect(reuseKey('time=day')).toBeNull();
    expect(reuseKey('pose=1,2,no,0,0,0,55')).toBeNull();
    expect(reuseKey('pose=1,2,3,0,0,0,55&pass=class')).not.toBe(a);
    expect(reuseKey('pose=1,2,3,0,0,0,55', 'reartree=off')).not.toBe(a);
  });
});
