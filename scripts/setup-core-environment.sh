#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/toolchains/node-download /workspace/toolchains/bin /workspace/setup-tools /workspace/.config/blender/4.2
cd /workspace/toolchains/node-download
if [ ! -f node-v22.22.2-linux-x64.tar.xz ]; then
  curl --fail --silent --show-error https://nodejs.org/dist/v22.22.2/node-v22.22.2-linux-x64.tar.xz -o node-v22.22.2-linux-x64.tar.xz
fi
curl --fail --silent --show-error https://nodejs.org/dist/v22.22.2/SHASUMS256.txt -o SHASUMS256.txt
sha256sum --check --ignore-missing SHASUMS256.txt
tar -xf node-v22.22.2-linux-x64.tar.xz -C /workspace/toolchains
PATH=/workspace/toolchains/node-v22.22.2-linux-x64/bin:$PATH npm install --prefix /workspace/toolchains/npm-10.9.7 npm@10.9.7 --cache /workspace/.npm
cd /workspace/toolchains
if [ ! -f blender-4.2.3-linux-x64.tar.xz ]; then
  curl --fail --silent --show-error https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz -o blender-4.2.3-linux-x64.tar.xz
fi
curl --fail --silent --show-error https://download.blender.org/release/Blender4.2/blender-4.2.3.sha256 -o blender-4.2.3.sha256
sha256sum --check --ignore-missing blender-4.2.3.sha256
tar -xf blender-4.2.3-linux-x64.tar.xz
export UV_CACHE_DIR=/workspace/.cache/uv
export UV_PYTHON_INSTALL_DIR=/workspace/toolchains/python
export UV_PYTHON_BIN_DIR=/workspace/toolchains/bin
uv python install 3.11.15
if [ ! -x /workspace/toolchains/core-python311/bin/python ]; then
  uv venv --python /workspace/toolchains/python/cpython-3.11.15-linux-x86_64-gnu/bin/python3.11 /workspace/toolchains/core-python311
fi
uv pip install --python /workspace/toolchains/core-python311/bin/python numpy==2.4.6 Pillow==12.3.0 shapely==2.0.6 scipy==1.17.1
cat > /workspace/toolchains/bin/blender <<'WRAPPER'
#!/usr/bin/env bash
export BLENDER_USER_RESOURCES=/workspace/.config/blender/4.2
exec /workspace/toolchains/blender-4.2.3-linux-x64/blender "$@"
WRAPPER
chmod +x /workspace/toolchains/bin/blender
cat > /workspace/setup-tools/core-env.sh <<'ACTIVATE'
export PATH="/workspace/toolchains/bin:/workspace/toolchains/npm-10.9.7/node_modules/.bin:/workspace/toolchains/node-v22.22.2-linux-x64/bin:/workspace/toolchains/core-python311/bin:$PATH"
export PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright
ACTIVATE
source /workspace/setup-tools/core-env.sh
cd /workspace/shibuya-scene-2
node --version
npm --version
python3 --version
npm ci --cache /workspace/.npm
npm run sync-assets
npx playwright install chromium
