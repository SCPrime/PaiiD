import fs from "fs";
import os from "os";
import path from "path";
const CHROMIUM_NAMES = ["chromium", "chromium-headless-shell"];
const PLATFORM_SUBDIRECTORIES = [
  "chrome-linux",
  "chrome-win",
  "chrome-win64",
  "chrome-mac",
  "chrome-mac-arm64",
];
const EXECUTABLE_NAMES = ["chrome", "chromium", "chrome.exe", "chromium.exe", "headless_shell"];

const localRegistryPaths: string[] = [];

const envRegistry = process.env.PLAYWRIGHT_BROWSERS_PATH;

const projectRoot = process.cwd();

if (envRegistry && envRegistry !== "0") {
  localRegistryPaths.push(path.resolve(envRegistry));
} else if (envRegistry === "0") {
  localRegistryPaths.push(
    path.join(projectRoot, "node_modules", "playwright-core", ".local-browsers")
  );
}

localRegistryPaths.push(path.join(os.homedir(), ".cache", "ms-playwright"));
localRegistryPaths.push(
  path.join(projectRoot, "node_modules", "playwright-core", ".local-browsers")
);
localRegistryPaths.push(
  path.join(projectRoot, "node_modules", "@playwright", "test", ".local-browsers")
);

const enumerateExecutables = (root: string) => {
  if (!fs.existsSync(root)) {
    return [];
  }

  const entries = fs.readdirSync(root, { withFileTypes: true });
  const executables: string[] = [];

  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }

    if (!CHROMIUM_NAMES.some((name) => entry.name.startsWith(`${name}-`))) {
      continue;
    }

    for (const subDir of PLATFORM_SUBDIRECTORIES) {
      for (const executable of EXECUTABLE_NAMES) {
        executables.push(path.join(root, entry.name, subDir, executable));
      }
    }
  }

  return executables;
};

export const hasChromiumBrowser = () => {
  for (const root of localRegistryPaths) {
    const executables = enumerateExecutables(root);
    if (executables.some((executablePath) => fs.existsSync(executablePath))) {
      return true;
    }
  }

  return false;
};
