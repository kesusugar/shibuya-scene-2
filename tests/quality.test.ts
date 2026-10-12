import { describe, expect, it } from 'vitest';
import { pickQuality, QUALITIES } from '../src/core/quality';

describe('quality presets', () => {
  it('defaults to medium and ignores unknown names', () => {
    expect(pickQuality(null).name).toBe('medium');
    expect(pickQuality('ultra').name).toBe('medium');
    expect(pickQuality('low').name).toBe('low');
  });
  it('low is strictly cheaper than high', () => {
    expect(QUALITIES.low.maxDpr).toBeLessThan(QUALITIES.high.maxDpr);
    expect(QUALITIES.low.shadows).toBe(false);
    expect(QUALITIES.low.bloom).toBe(false);
  });
});
