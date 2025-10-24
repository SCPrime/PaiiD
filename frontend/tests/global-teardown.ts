/**
 * Playwright Global Teardown
 * Runs once after all tests to cleanup test servers and artifacts
 * Version: 1.0.0
 */

import { execSync } from "child_process";
import { existsSync, readdirSync, unlinkSync } from "fs";
import { join } from "path";

/**
 * Stop all test servers gracefully
 */
function stopTestServers(): void {
  console.log("[Global Teardown] Stopping test servers...");

  const testPorts = [3000, 8002];

  for (const port of testPorts) {
    try {
      if (process.platform === "win32") {
        execSync(
          `powershell -Command "Get-NetTCPConnection -LocalPort ${port} -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"`,
          { stdio: "ignore" }
        );
      } else {
        execSync(`lsof -ti:${port} | xargs kill -TERM 2>/dev/null || true`, {
          stdio: "ignore",
        });
      }
      console.log(`  Stopped server on port ${port}`);
    } catch (error) {
      // Ignore if already stopped
    }
  }
}

/**
 * Remove all PID files
 */
function removePidFiles(): void {
  console.log("[Global Teardown] Removing PID files...");

  const pidDirs = [join(__dirname, "..", "..", "backend", ".run"), join(__dirname, "..", ".run")];

  let removed = 0;

  for (const pidDir of pidDirs) {
    if (!existsSync(pidDir)) continue;

    try {
      const files = readdirSync(pidDir);
      for (const file of files) {
        if (file.endsWith(".pid")) {
          unlinkSync(join(pidDir, file));
          removed++;
        }
      }
    } catch (error) {
      console.warn(`  Could not clean ${pidDir}`);
    }
  }

  console.log(`  Removed ${removed} PID file(s)`);
}

/**
 * Archive test artifacts (optional)
 */
function archiveTestArtifacts(): void {
  console.log("[Global Teardown] Test artifacts available:");

  const artifactDirs = [
    { path: join(__dirname, "..", "test-results"), name: "Test Results" },
    { path: join(__dirname, "..", "playwright-report"), name: "HTML Report" },
  ];

  for (const { path, name } of artifactDirs) {
    if (existsSync(path)) {
      console.log(`  ${name}: ${path}`);
    }
  }
}

/**
 * Main global teardown function
 */
async function globalTeardown(): Promise<void> {
  console.log("=".repeat(70));
  console.log("Playwright Global Teardown - Post-Test Cleanup");
  console.log("=".repeat(70));

  // 1. Stop test servers gracefully
  stopTestServers();

  // Wait for servers to shutdown
  await new Promise((resolve) => setTimeout(resolve, 2000));

  // 2. Remove PID files
  removePidFiles();

  // 3. Archive/report artifacts
  archiveTestArtifacts();

  console.log("=".repeat(70));
  console.log("Global Teardown Complete - All test resources cleaned up");
  console.log("=".repeat(70));
  console.log("");
}

export default globalTeardown;
