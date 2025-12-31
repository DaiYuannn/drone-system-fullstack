#!/usr/bin/env node
// Cross-platform clean for ./dist (CommonJS)
const fs = require('fs');
const path = require('path');

const dist = path.resolve(process.cwd(), 'dist');
if (fs.existsSync(dist)) {
  fs.rmSync(dist, { recursive: true, force: true });
  console.log('[clean] removed dist');
} else {
  console.log('[clean] dist not found, skip');
}
