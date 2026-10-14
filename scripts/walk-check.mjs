// QA: scripted walks in the real scene (statue, kiosk, kerb, plaza). node scripts/walk-check.mjs <base> <out.json>
import { chromium } from 'playwright';
import { writeFileSync } from 'node:fs';
const [base, out] = process.argv.slice(2);
const walks = {
  into_statue: [11.6, -44.0, 0, -1, 40],          // from the plaza straight at Hachiko (statue centre ~11.57,-48.69)
  into_kiosk: [34.5, -36.0, 0, -1, 60],            // at the kiosk candidate (27..42, -53..-39)
  road_to_kerb: [6.5, -2.0, 1, -1.35, 120],        // crossing centre to the station-side pavement over the kerb
  across_plaza: [20, -25, 1, -1, 80],
};
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: 400, height: 300 } });
await p.goto(`${base}/?capture&time=day`); await p.waitForFunction(() => window.__viewer?.ready, null, { timeout: 400000 });
const res = {};
for (const [k, a] of Object.entries(walks)) {
  const r = await p.evaluate((a) => window.__viewer.walkTest(...a), a);
  const zs = (r.path ?? []).map((q) => q[2]); let maxJump = 0;
  for (let i = 1; i < zs.length; i++) maxJump = Math.max(maxJump, Math.abs(zs[i] - zs[i - 1]));
  res[k] = { steps: r.path?.length ?? 0, stoppedAt: r.stoppedAt, maxStepChange_m: +maxJump.toFixed(3), minZ: zs.length ? Math.min(...zs) : null };
  console.log(k, JSON.stringify(res[k]));
}
writeFileSync(out, JSON.stringify(res, null, 2)); await b.close();
