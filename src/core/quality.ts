/** Quality presets, picked with ?q=low|medium|high (default medium). Measured on the owner's PC, not assumed. */
export type QualityName = 'low' | 'medium' | 'high';

export interface Quality {
  name: QualityName;
  maxDpr: number;
  antialias: boolean;
  shadows: boolean;
  shadowMapSize: number;
  bloom: boolean;
  /** screen-space ambient occlusion (GTAO): contact shadows at wall bases, corners and under furniture */
  ao: boolean;
}

export const QUALITIES: Record<QualityName, Quality> = {
  low: { name: 'low', maxDpr: 1, antialias: false, shadows: false, shadowMapSize: 1024, bloom: false, ao: false },
  medium: { name: 'medium', maxDpr: 1.25, antialias: true, shadows: true, shadowMapSize: 2048, bloom: true, ao: true },
  high: { name: 'high', maxDpr: 2, antialias: true, shadows: true, shadowMapSize: 4096, bloom: true, ao: true },
};

export function pickQuality(param: string | null): Quality {
  return QUALITIES[(param ?? 'medium') as QualityName] ?? QUALITIES.medium;
}
