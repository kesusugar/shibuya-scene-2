// Only camera/time may change without navigating. A preset without a pose needs
// a fresh page so its normal initial framing is applied, never the previous pose.
export function reuseKey(query, extra = '') {
  const params = new URLSearchParams(`${query}&${extra}`);
  const pose = params.get('pose')?.split(',').map(Number);
  if (!pose || pose.length !== 7 || !pose.every(Number.isFinite) || pose[6] <= 0) return null;
  params.delete('pose'); params.delete('time'); params.sort();
  return `pose:${params.toString()}`;
}
