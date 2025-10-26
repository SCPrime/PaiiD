/**
 * Playwright Global Setup
 * Runs once before all tests to ensure clean test environment
 * Version: 1.0.0
 */

/* eslint-disable no-console */
import { execSync } from "child_process";
import { existsSync, readdirSync, unlinkSync } from "fs";
import { join } from "path";

/**
 * Kill processes on specific ports (cross-platform) with PID tracking
 */
async function killPort(port: number): Promise<void> {
  console.log(`[Global Setup] Cleaning up port ${port}...`);

  try {
    let pids: number[] = [];
    
    if (process.platform === "win32") {
      // Windows - get PIDs first
      const getPidsCmd = `powershell -Command "Get-NetTCPConnection -LocalPort ${port} -State Listen -ErrorAction SilentlyContinue | ForEach-Object { $_.OwningProcess }"`;
      const result = execSync(getPidsCmd, { encoding: "utf8", timeout: 10000 });
      pids = result.trim().split("\n").filter(pid => pid.trim()).map(pid => parseInt(pid.trim()));
      
      if (pids.length > 0) {
        // Kill processes
        const killCmd = `powershell -Command "Get-NetTCPConnection -LocalPort ${port} -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"`;
        execSync(killCmd, { stdio: "ignore", timeout: 10000 });
      }
    } else {
      // Unix/Linux/Mac - get PIDs first
      try {
        const result = execSync(`lsof -ti:${port}`, { encoding: "utf8", timeout: 10000 });
        pids = result.trim().split("\n").filter(pid => pid.trim()).map(pid => parseInt(pid.trim()));
        
        if (pids.length > 0) {
          execSync(`lsof -ti:${port} | xargs kill -9 2>/dev/null || true`, {
            stdio: "ignore",
            timeout: 10000,
          });
        }
      } catch (error) {
        // Port not in use
      }
    }
    
    if (pids.length > 0) {
      console.log(`  Port ${port} cleared (killed PIDs: ${pids.join(", ")})`);
    } else {
      console.log(`  Port ${port} was not in use`);
    }
  } catch (error) {
    console.log(`  Port ${port} cleanup failed: ${error}`);
  }
}

/**
 * Clean up PID files from previous test runs
 */
function cleanupPidFiles(): void {
  console.log("[Global Setup] Cleaning up PID files...");

  const pidDirs = [join(__dirname, "..", "..", "backend", ".run"), join(__dirname, "..", ".run")];

  let cleaned = 0;

  for (const pidDir of pidDirs) {
    if (!existsSync(pidDir)) {
      continue;
    }

    try {
      const files = readdirSync(pidDir);
      for (const file of files) {
        if (file.endsWith(".pid")) {
          const pidFile = join(pidDir, file);
          unlinkSync(pidFile);
          cleaned++;
        }
      }
    } catch (error) {
      console.warn(`  Warning: Could not clean PID directory ${pidDir}`);
    }
  }

  console.log(`  Cleaned up ${cleaned} PID file(s)`);
}

/**
 * Validate environment configuration
 */
function validateEnvironment(): void {
  console.log("[Global Setup] Validating environment...");

  // Check critical environment variables
  const requiredVars = ["NEXT_PUBLIC_BACKEND_API_BASE_URL", "NEXT_PUBLIC_API_TOKEN"];

  const missing: string[] = [];

  for (const varName of requiredVars) {
    if (!process.env[varName]) {
      missing.push(varName);
    }
  }

  if (missing.length > 0) {
    console.warn(`  Warning: Missing environment variables: ${missing.join(", ")}`);
    console.warn("  Tests may fail without proper configuration");
  } else {
    console.log("  Environment configuration valid");
  }
}

/**
 * Main global setup function
 */
async function globalSetup(): Promise<void> {
  console.log("=".repeat(70));
  console.log("Playwright Global Setup - Pre-Test Cleanup");
  console.log("=".repeat(70));

  // 1. Clean up test ports (3000, 3001, 3002, 3003, 8000, 8001, 8002)
  const testPorts = [3000, 3001, 3002, 3003, 8000, 8001, 8002];
  for (const port of testPorts) {
    await killPort(port);
  }

  // Wait for ports to fully release
  await new Promise((resolve) => setTimeout(resolve, 2000));

  // 2. Clean up PID files
  cleanupPidFiles();

  // 3. Validate environment
  validateEnvironment();

  console.log("=".repeat(70));
  console.log("Global Setup Complete - Test environment is clean");
  console.log("=".repeat(70));
  console.log("");
}

export default globalSetup;
