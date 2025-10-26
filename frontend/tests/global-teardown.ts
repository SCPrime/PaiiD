/**
 * Playwright Global Teardown
 * Runs once after all tests to cleanup test servers and artifacts
 * Version: 1.0.0
 */

/* eslint-disable no-console */
import { execSync } from "child_process";
import { existsSync, readdirSync, unlinkSync } from "fs";
import { join } from "path";

/**
 * Stop all test servers gracefully with PID tracking
 */
async function stopTestServers(): Promise<void> {
  console.log("[Global Teardown] Stopping test servers...");

  const testPorts = [3000, 8002];

  for (const port of testPorts) {
    try {
      let pids: number[] = [];
      
      if (process.platform === "win32") {
        // Windows - get PIDs first
        const getPidsCmd = `powershell -Command "Get-NetTCPConnection -LocalPort ${port} -State Listen -ErrorAction SilentlyContinue | ForEach-Object { $_.OwningProcess }"`;
        try {
          const result = execSync(getPidsCmd, { encoding: "utf8", timeout: 10000 });
          pids = result.trim().split("\n").filter(pid => pid.trim()).map(pid => parseInt(pid.trim()));
        } catch (error) {
          // Port not in use
        }
        
        if (pids.length > 0) {
          // Try graceful shutdown first (SIGTERM)
          const gracefulCmd = `powershell -Command "Get-NetTCPConnection -LocalPort ${port} -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue }"`;
          execSync(gracefulCmd, { stdio: "ignore", timeout: 5000 });
          
          // Wait for graceful shutdown
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          // Check if still running, force kill if needed
          try {
            const stillRunning = execSync(getPidsCmd, { encoding: "utf8", timeout: 5000 });
            if (stillRunning.trim()) {
              const forceCmd = `powershell -Command "Get-NetTCPConnection -LocalPort ${port} -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"`;
              execSync(forceCmd, { stdio: "ignore", timeout: 5000 });
            }
          } catch (error) {
            // All processes stopped
          }
        }
      } else {
        // Unix/Linux/Mac - get PIDs first
        try {
          const result = execSync(`lsof -ti:${port}`, { encoding: "utf8", timeout: 10000 });
          pids = result.trim().split("\n").filter(pid => pid.trim()).map(pid => parseInt(pid.trim()));
          
          if (pids.length > 0) {
            // Try graceful shutdown first (SIGTERM)
            execSync(`lsof -ti:${port} | xargs kill -TERM 2>/dev/null || true`, {
              stdio: "ignore",
              timeout: 5000,
            });
            
            // Wait for graceful shutdown
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Check if still running, force kill if needed
            try {
              const stillRunning = execSync(`lsof -ti:${port}`, { encoding: "utf8", timeout: 5000 });
              if (stillRunning.trim()) {
                execSync(`lsof -ti:${port} | xargs kill -9 2>/dev/null || true`, {
                  stdio: "ignore",
                  timeout: 5000,
                });
              }
            } catch (error) {
              // All processes stopped
            }
          }
        } catch (error) {
          // Port not in use
        }
      }
      
      if (pids.length > 0) {
        console.log(`  Stopped server on port ${port} (killed PIDs: ${pids.join(", ")})`);
      } else {
        console.log(`  Port ${port} was not in use`);
      }
    } catch (error) {
      console.log(`  Error stopping server on port ${port}: ${error}`);
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
  await stopTestServers();

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
