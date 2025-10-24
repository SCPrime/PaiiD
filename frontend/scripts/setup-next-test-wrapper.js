/* eslint-disable @typescript-eslint/no-var-requires */
const fs = require("fs");
const path = require("path");

const PROJECT_ROOT = path.resolve(__dirname, "..");
const BIN_DIR = path.join(PROJECT_ROOT, "node_modules", ".bin");
const NEXT_BIN_CMD = path.join(BIN_DIR, "next.cmd");
const REAL_CLI_PATH = path.join(PROJECT_ROOT, "node_modules", "next", "dist", "bin", "next");
const BACKUP_CLI_PATH = `${REAL_CLI_PATH}.original.js`;

const wrapperSource = `#!/usr/bin/env node
const path = require('path');
const { spawnSync } = require('child_process');

const args = process.argv.slice(2);
const projectRoot = process.cwd();

if (args[0] === 'test') {
  const npmExecutable = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  let packageJson;
  try {
    packageJson = require(path.join(projectRoot, 'package.json'));
  } catch (error) {
    console.error('Unable to read package.json for resolving the test script.');
    process.exit(1);
  }

  const scripts = packageJson.scripts || {};
  const preferredScript = scripts['test:ci'] ? 'test:ci' : scripts.test ? 'test' : null;

  if (!preferredScript) {
    console.error('No \`test\` or \`test:ci\` script is defined in package.json.');
    process.exit(1);
  }

  const result = spawnSync(npmExecutable, ['run', preferredScript, '--', ...args.slice(1)], {
    stdio: 'inherit',
    cwd: projectRoot,
    env: process.env,
  });
  process.exit(result.status ?? 1);
}

require(path.join(__dirname, 'next.original.js'));
`;

const cmdWrapperSource = `@ECHO OFF

SETLOCAL

SET "NODE_CMD=node"

"%NODE_CMD%" "%~dp0\\..\\next\\dist\\bin\\next" %*

ENDLOCAL

`;

function ensureFile(filePath, contents, mode) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, contents, { mode });
}

if (!fs.existsSync(REAL_CLI_PATH)) {
  return;
}

if (!fs.existsSync(BACKUP_CLI_PATH)) {
  fs.copyFileSync(REAL_CLI_PATH, BACKUP_CLI_PATH);
}

ensureFile(REAL_CLI_PATH, wrapperSource, 0o755);

if (process.platform === "win32") {
  ensureFile(NEXT_BIN_CMD, cmdWrapperSource, 0o755);
}
