// Copies each building's web export (assets/buildings/<id>/web/*) and manifest into public/buildings/<id>/.
// The authoring tree under assets/ stays the single source; public/buildings/ is generated and git-ignored.
import { cpSync, existsSync, mkdirSync, readdirSync, rmSync } from 'node:fs';
import { join } from 'node:path';

const root = 'assets/buildings';
const out = 'public/buildings';
rmSync(out, { recursive: true, force: true });
const ids = [];
for (const id of readdirSync(root)) {
  const web = join(root, id, 'web');
  if (!existsSync(web)) continue;
  mkdirSync(join(out, id), { recursive: true });
  cpSync(web, join(out, id), { recursive: true });
  if (existsSync(join(root, id, 'manifest.json'))) cpSync(join(root, id, 'manifest.json'), join(out, id, 'manifest.json'));
  ids.push(id);
}
console.log(`sync-assets: ${ids.join(', ') || '(none)'}`);
