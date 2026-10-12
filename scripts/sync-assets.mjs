// Copies each building's web export (assets/buildings/<id>/web/*) and manifest into public/buildings/<id>/, and each
// ground tile (assets/ground/<id>/web/*) into public/ground/<id>/.
// The authoring tree under assets/ stays the single source; public/buildings/ and public/ground/ are generated and git-ignored.
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
const gids = [];
rmSync('public/ground', { recursive: true, force: true });
if (existsSync('assets/ground')) for (const id of readdirSync('assets/ground')) {
  const web = join('assets/ground', id, 'web');
  if (!existsSync(web)) continue;
  mkdirSync(join('public/ground', id), { recursive: true });
  cpSync(web, join('public/ground', id), { recursive: true });
  if (existsSync(join('assets/ground', id, 'manifest.json'))) cpSync(join('assets/ground', id, 'manifest.json'), join('public/ground', id, 'manifest.json'));
  gids.push(id);
}
console.log(`sync-assets: ${ids.join(', ') || '(none)'}; ground: ${gids.join(', ') || '(none)'}`);
