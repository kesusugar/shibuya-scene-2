// QA: names of the assets under screen points. node scripts/pick.mjs <base> "<query>" W H x,y x,y ...
import { chromium } from 'playwright';
const [base, q, W, H, ...pts] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: +W, height: +H } });
await p.goto(`${base}/?capture&${q}`); await p.waitForFunction(() => window.__viewer?.ready, null, { timeout: 400000 });
for (const s of pts) { const [x, y] = s.split(',').map(Number); console.log(s, JSON.stringify(await p.evaluate(([x, y]) => window.__viewer.pick(x, y), [x, y]))); }
await b.close();
