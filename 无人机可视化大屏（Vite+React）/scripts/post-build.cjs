#!/usr/bin/env node
// Cross-platform post build: copy package.json to dist and create a build flag (CommonJS)
const fs = require('fs');
const path = require('path');

const root = process.cwd();
const dist = path.resolve(root, 'dist');
const flagFile = path.resolve(dist, 'build.flag');
const pkgSrc = path.resolve(root, 'package.json');
const pkgDst = path.resolve(dist, 'package.json');

if (!fs.existsSync(dist)) {
  console.error('[post-build] dist directory does not exist, run build first.');
  process.exit(1);
}

fs.copyFileSync(pkgSrc, pkgDst);
fs.writeFileSync(flagFile, `${new Date().toISOString()}\n`);
console.log('[post-build] copied package.json and wrote build.flag');
