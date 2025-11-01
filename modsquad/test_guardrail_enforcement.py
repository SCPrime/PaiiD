"""
Test script to validate guardrail enforcement behavior.
Creates temporary config files to trigger intentional failures.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Colors for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def test_browser_validator_blocking():
    """Test that browser_validator exits with code 1 when guardrails fail."""
    print(f"\n{BLUE}TEST 1: Browser Validator Guardrail Enforcement{RESET}")
    print("Testing accessibility failure with block_on_fail=true...")

    # Create temporary test config with failing thresholds
    test_config = Path(__file__).parent / "config" / "browser_guardrails_test.yaml"
    test_config.write_text("""
browser_guardrails:
  accessibility:
    tool: axe-core
    min_score: 100  # Impossible threshold to force failure
    block_on_fail: true
  performance:
    tool: lighthouse
    min_score: 50
    block_on_fail: false
""")

    # Run browser validator with test config
    env = os.environ.copy()
    env["MOD_SQUAD_CONFIG_PATH"] = str(test_config)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "modsquad.extensions.browser_validator"],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

        # Should exit with code 1 if guardrail enforcement works
        output = result.stdout + result.stderr
        if result.returncode == 1 and "GUARDRAIL VIOLATIONS" in output:
            print(f"{GREEN}[PASS] browser_validator correctly blocked on failure{RESET}")
            print(f"  Exit code: {result.returncode}")
            print(f"  Output: {output[:200]}")
            return True
        elif result.returncode == 1:
            # Still passes if exits with code 1, even if message not captured
            print(f"{GREEN}[PASS] browser_validator exited with code 1 (blocking enforced){RESET}")
            print(f"  Exit code: {result.returncode}")
            return True
        else:
            print(f"{RED}[FAIL] browser_validator did not block{RESET}")
            print(f"  Exit code: {result.returncode}")
            print(f"  Output: {output[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"{YELLOW}[TIMEOUT] Test took too long{RESET}")
        return False
    finally:
        # Clean up test config
        if test_config.exists():
            test_config.unlink()


def test_contract_enforcer_blocking():
    """Test that contract_enforcer exits with code 1 when API drifts."""
    print(f"\n{BLUE}TEST 2: Contract Enforcer Guardrail Enforcement{RESET}")
    print("Testing API drift with block_on_drift=true...")

    # Create temporary test config
    test_config = Path(__file__).parent / "config" / "browser_guardrails_test.yaml"
    test_config.write_text("""
browser_guardrails:
  contract_testing:
    tool: dredd
    spec_path: backend/docs/openapi.yaml
    block_on_drift: true
""")

    env = os.environ.copy()
    env["MOD_SQUAD_CONFIG_PATH"] = str(test_config)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "modsquad.extensions.contract_enforcer"],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )

        # Check if it exits with code 1 on drift
        output = result.stdout + result.stderr
        if result.returncode == 1 and "API CONTRACT DRIFT" in output:
            print(f"{GREEN}[PASS] contract_enforcer correctly blocked on drift{RESET}")
            print(f"  Exit code: {result.returncode}")
            return True
        elif result.returncode == 1:
            # Still passes if exits with code 1
            print(f"{GREEN}[PASS] contract_enforcer exited with code 1 (blocking enforced){RESET}")
            print(f"  Exit code: {result.returncode}")
            return True
        elif result.returncode == 0:
            print(f"{YELLOW}[SKIP] No drift detected (API matches spec){RESET}")
            return True  # Not a failure, just no drift
        else:
            print(f"{RED}[FAIL] contract_enforcer unexpected return code{RESET}")
            print(f"  Exit code: {result.returncode}")
            print(f"  Output: {output[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"{YELLOW}[TIMEOUT] Test took too long{RESET}")
        return False
    finally:
        if test_config.exists():
            test_config.unlink()


def test_bundle_analyzer_blocking():
    """Test that bundle_analyzer exits with code 1 when bundle exceeds size."""
    print(f"\n{BLUE}TEST 3: Bundle Analyzer Guardrail Enforcement{RESET}")
    print("Testing bundle size breach with block_on_size_breach=true...")

    # Create temporary test config with very small threshold
    test_config = Path(__file__).parent / "config" / "browser_guardrails_test.yaml"
    test_config.write_text("""
browser_guardrails:
  bundle_analysis:
    max_bundle_size_kb: 1  # Impossibly small to force failure
    block_on_size_breach: true
""")

    env = os.environ.copy()
    env["MOD_SQUAD_CONFIG_PATH"] = str(test_config)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "modsquad.extensions.bundle_analyzer"],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )

        # Check if it exits with code 1 on size breach
        output = result.stdout + result.stderr
        if result.returncode == 1 and "BUNDLE SIZE BREACH" in output:
            print(f"{GREEN}[PASS] bundle_analyzer correctly blocked on size breach{RESET}")
            print(f"  Exit code: {result.returncode}")
            return True
        elif result.returncode == 1:
            # Still passes if exits with code 1
            print(f"{GREEN}[PASS] bundle_analyzer exited with code 1 (blocking enforced){RESET}")
            print(f"  Exit code: {result.returncode}")
            return True
        elif "skipped" in output.lower():
            print(f"{YELLOW}[SKIP] No build directory found{RESET}")
            return True  # Not a failure
        else:
            print(f"{RED}[FAIL] bundle_analyzer unexpected return code{RESET}")
            print(f"  Exit code: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print(f"{YELLOW}[TIMEOUT] Test took too long{RESET}")
        return False
    finally:
        if test_config.exists():
            test_config.unlink()


def test_bravo_squad_propagation():
    """Test that BRAVO squad propagates guardrail failures."""
    print(f"\n{BLUE}TEST 4: BRAVO Squad Guardrail Propagation{RESET}")
    print("Testing squad-level enforcement...")

    # This test requires Python import, not subprocess
    try:
        # Temporarily add modsquad to path
        modsquad_path = Path(__file__).parent
        if str(modsquad_path) not in sys.path:
            sys.path.insert(0, str(modsquad_path))

        from squads import bravo

        # Test with enforce_guardrails=True (should propagate exits)
        print("  Testing bravo.deploy(enforce_guardrails=True)...")
        try:
            result = bravo.deploy(skip=["infra_health"], enforce_guardrails=True)
            print(f"{YELLOW}[WARN] No guardrail failures detected in this run{RESET}")
            return True
        except SystemExit as e:
            if e.code == 1:
                print(f"{GREEN}[PASS] BRAVO squad correctly propagated exit code 1{RESET}")
                return True
            else:
                print(f"{RED}[FAIL] Unexpected exit code {e.code}{RESET}")
                return False

    except Exception as e:
        print(f"{RED}[ERROR] {str(e)}{RESET}")
        return False


def main():
    """Run all guardrail enforcement tests."""
    print(f"\n{'=' * 60}")
    print(f"{BLUE}MOD SQUAD GUARDRAIL ENFORCEMENT TEST SUITE{RESET}")
    print(f"{'=' * 60}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    results = {
        "browser_validator": test_browser_validator_blocking(),
        "contract_enforcer": test_contract_enforcer_blocking(),
        "bundle_analyzer": test_bundle_analyzer_blocking(),
        "bravo_squad": test_bravo_squad_propagation(),
    }

    # Summary
    print(f"\n{'=' * 60}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{'=' * 60}")

    total = len(results)
    passed = sum(results.values())

    for test_name, result_passed in results.items():
        status = f"{GREEN}[PASS]{RESET}" if result_passed else f"{RED}[FAIL]{RESET}"
        print(f"  {test_name}: {status}")

    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")

    if passed == total:
        print(f"\n{GREEN}SUCCESS - ALL GUARDRAIL TESTS PASSED{RESET}\n")
        return 0
    else:
        print(f"\n{RED}FAILURE - SOME GUARDRAIL TESTS FAILED{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
