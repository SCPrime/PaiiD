"""
Frontend Comprehensive Audit Script
Analyzes frontend codebase for quality, performance, and security issues
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class FrontendAuditor:
    """Comprehensive frontend code auditor"""

    def __init__(self, frontend_dir: str = "frontend"):
        self.frontend_dir = Path(frontend_dir)
        self.issues = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }
        self.metrics = {
            "total_files": 0,
            "total_components": 0,
            "total_hooks": 0,
            "total_lines": 0,
            "typescript_files": 0,
            "javascript_files": 0,
        }
        self.security_issues = []
        self.performance_issues = []
        self.quality_issues = []

    def audit_all(self):
        """Run all audit checks"""
        print("[AUDIT] Starting comprehensive frontend audit...")

        self._audit_file_structure()
        self._audit_typescript_quality()
        self._audit_component_structure()
        self._audit_performance_patterns()
        self._audit_security_patterns()
        self._audit_accessibility()

        return self._generate_report()

    def _audit_file_structure(self):
        """Audit file structure and organization"""
        print("[FILE STRUCTURE] Auditing file structure...")

        for root, dirs, files in os.walk(self.frontend_dir):
            # Skip node_modules and build directories
            dirs[:] = [
                d for d in dirs if d not in ["node_modules", ".next", "out", "dist"]
            ]

            for file in files:
                if file.endswith((".ts", ".tsx", ".js", ".jsx")):
                    self.metrics["total_files"] += 1
                    file_path = Path(root) / file

                    if file.endswith((".ts", ".tsx")):
                        self.metrics["typescript_files"] += 1
                    else:
                        self.metrics["javascript_files"] += 1
                        self.issues["medium"].append(
                            {
                                "type": "file_structure",
                                "severity": "medium",
                                "file": str(file_path),
                                "message": "JavaScript file found - prefer TypeScript for type safety",
                            }
                        )

                    self._audit_file_content(file_path)

    def _audit_file_content(self, file_path: Path):
        """Audit individual file content"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                self.metrics["total_lines"] += len(lines)

                # Check for React components
                if "export" in content and (
                    "function" in content or "const" in content
                ):
                    if "React" in content or "JSX" in content or "<" in content:
                        self.metrics["total_components"] += 1

                # Check for custom hooks
                if re.search(r"function use[A-Z]\w+|const use[A-Z]\w+ =", content):
                    self.metrics["total_hooks"] += 1

                # Security checks
                self._check_security_issues(file_path, content)

                # Performance checks
                self._check_performance_issues(file_path, content)

                # Quality checks
                self._check_quality_issues(file_path, content)

        except Exception as e:
            self.issues["low"].append(
                {
                    "type": "file_read_error",
                    "severity": "low",
                    "file": str(file_path),
                    "message": f"Error reading file: {e}",
                }
            )

    def _check_security_issues(self, file_path: Path, content: str):
        """Check for security vulnerabilities"""

        # Check for dangerouslySetInnerHTML
        if "dangerouslySetInnerHTML" in content:
            self.issues["critical"].append(
                {
                    "type": "security",
                    "severity": "critical",
                    "file": str(file_path),
                    "message": "dangerouslySetInnerHTML usage detected - XSS vulnerability risk",
                    "recommendation": "Use sanitization library or avoid raw HTML",
                }
            )

        # Check for eval() usage
        if re.search(r"\beval\s*\(", content):
            self.issues["critical"].append(
                {
                    "type": "security",
                    "severity": "critical",
                    "file": str(file_path),
                    "message": "eval() usage detected - severe security risk",
                    "recommendation": "Remove eval() and use safe alternatives",
                }
            )

        # Check for localStorage without encryption
        if "localStorage.setItem" in content:
            if "password" in content.lower() or "token" in content.lower():
                self.issues["high"].append(
                    {
                        "type": "security",
                        "severity": "high",
                        "file": str(file_path),
                        "message": "Sensitive data stored in localStorage without encryption",
                        "recommendation": "Use secure storage or encrypt sensitive data",
                    }
                )

        # Check for inline event handlers in JSX
        if re.search(r"on[A-Z]\w+=\{.*?\}", content):
            # This is normal in React, but check for potential XSS
            pass

        # Check for direct window.location usage
        if "window.location.href" in content and "=" in content:
            self.issues["medium"].append(
                {
                    "type": "security",
                    "severity": "medium",
                    "file": str(file_path),
                    "message": "Direct window.location manipulation - potential open redirect",
                    "recommendation": "Use Next.js router for navigation",
                }
            )

    def _check_performance_issues(self, file_path: Path, content: str):
        """Check for performance anti-patterns"""

        # Check for inline function definitions in JSX
        inline_functions = re.findall(
            r"<\w+[^>]*\s+on\w+\s*=\s*\{[^}]*\(.*?\)\s*=>", content
        )
        if len(inline_functions) > 3:
            self.issues["medium"].append(
                {
                    "type": "performance",
                    "severity": "medium",
                    "file": str(file_path),
                    "message": f"Multiple inline function definitions in JSX ({len(inline_functions)} found)",
                    "recommendation": "Use useCallback to memoize event handlers",
                }
            )

        # Check for missing key props in lists
        if re.search(r"\.map\s*\([^)]*\)\s*=>\s*<", content):
            if not re.search(r"key\s*=", content):
                self.issues["high"].append(
                    {
                        "type": "performance",
                        "severity": "high",
                        "file": str(file_path),
                        "message": "Array.map without key prop - impacts performance",
                        "recommendation": "Add unique key prop to mapped elements",
                    }
                )

        # Check for useEffect without dependencies
        if "useEffect" in content:
            # Check for empty dependency array misuse
            empty_deps = content.count("useEffect(") - content.count("useEffect()")
            if empty_deps > 0:
                self.issues["medium"].append(
                    {
                        "type": "performance",
                        "severity": "medium",
                        "file": str(file_path),
                        "message": "useEffect may have missing or incorrect dependencies",
                        "recommendation": "Review useEffect dependencies",
                    }
                )

        # Check for large bundle imports
        if "import * as" in content:
            self.issues["medium"].append(
                {
                    "type": "performance",
                    "severity": "medium",
                    "file": str(file_path),
                    "message": "Wildcard import detected - increases bundle size",
                    "recommendation": "Import only needed exports",
                }
            )

    def _check_quality_issues(self, file_path: Path, content: str):
        """Check for code quality issues"""

        # Check for console.log statements
        if re.search(r"\bconsole\.(log|debug|info)\s*\(", content):
            self.issues["low"].append(
                {
                    "type": "quality",
                    "severity": "low",
                    "file": str(file_path),
                    "message": "console.log statements found",
                    "recommendation": "Remove debug console statements before production",
                }
            )

        # Check for any type usage
        if re.search(r":\s*any\b", content):
            self.issues["medium"].append(
                {
                    "type": "quality",
                    "severity": "medium",
                    "file": str(file_path),
                    "message": "'any' type usage detected - reduces type safety",
                    "recommendation": "Define proper TypeScript types",
                }
            )

        # Check for TODO comments
        todos = re.findall(r"//\s*TODO:", content)
        if todos:
            self.issues["low"].append(
                {
                    "type": "quality",
                    "severity": "low",
                    "file": str(file_path),
                    "message": f"{len(todos)} TODO comments found",
                    "recommendation": "Address TODO items before production",
                }
            )

        # Check for proper error handling
        if "catch" in content:
            if not re.search(r"catch\s*\(\s*\w+\s*:\s*\w+", content):
                self.issues["medium"].append(
                    {
                        "type": "quality",
                        "severity": "medium",
                        "file": str(file_path),
                        "message": "Error handling without type annotation",
                        "recommendation": "Add proper error types to catch blocks",
                    }
                )

    def _audit_typescript_quality(self):
        """Audit TypeScript configuration and usage"""
        print("[TYPESCRIPT] Auditing TypeScript quality...")

        tsconfig_path = self.frontend_dir / "tsconfig.json"
        if tsconfig_path.exists():
            with open(tsconfig_path, "r") as f:
                try:
                    tsconfig = json.load(f)
                    compiler_options = tsconfig.get("compilerOptions", {})

                    # Check for strict mode
                    if not compiler_options.get("strict", False):
                        self.issues["high"].append(
                            {
                                "type": "typescript",
                                "severity": "high",
                                "file": "tsconfig.json",
                                "message": "TypeScript strict mode not enabled",
                                "recommendation": "Enable strict mode for better type safety",
                            }
                        )

                    # Check for noImplicitAny
                    if not compiler_options.get("noImplicitAny", False):
                        self.issues["medium"].append(
                            {
                                "type": "typescript",
                                "severity": "medium",
                                "file": "tsconfig.json",
                                "message": "noImplicitAny not enabled",
                                "recommendation": "Enable noImplicitAny to catch type issues",
                            }
                        )

                except json.JSONDecodeError:
                    self.issues["high"].append(
                        {
                            "type": "typescript",
                            "severity": "high",
                            "file": "tsconfig.json",
                            "message": "Invalid JSON in tsconfig.json",
                        }
                    )

    def _audit_component_structure(self):
        """Audit component organization and structure"""
        print("[COMPONENTS] Auditing component structure...")

        components_dir = self.frontend_dir / "components"
        if components_dir.exists():
            # Check for proper component organization
            component_files = list(components_dir.rglob("*.tsx"))

            for component_file in component_files:
                # Check component naming
                if not component_file.stem[0].isupper():
                    self.issues["low"].append(
                        {
                            "type": "component_structure",
                            "severity": "low",
                            "file": str(component_file),
                            "message": "Component file should start with uppercase",
                            "recommendation": "Follow React naming conventions",
                        }
                    )

    def _audit_performance_patterns(self):
        """Audit for performance optimization patterns"""
        print("[PERFORMANCE] Auditing performance patterns...")

        # Check for dynamic imports
        dynamic_imports = 0
        for root, dirs, files in os.walk(self.frontend_dir):
            dirs[:] = [d for d in dirs if d not in ["node_modules", ".next"]]
            for file in files:
                if file.endswith((".tsx", ".ts")):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if "import(" in content or "dynamic from" in content:
                                dynamic_imports += 1
                    except:
                        pass

        if dynamic_imports == 0:
            self.issues["medium"].append(
                {
                    "type": "performance",
                    "severity": "medium",
                    "file": "global",
                    "message": "No dynamic imports found - missing code splitting",
                    "recommendation": "Implement code splitting with dynamic imports",
                }
            )

    def _audit_security_patterns(self):
        """Audit for security best practices"""
        print("[SECURITY] Auditing security patterns...")

        # Check for environment variable usage
        env_file = self.frontend_dir / ".env.local"
        if not env_file.exists() and not (self.frontend_dir / ".env").exists():
            self.issues["medium"].append(
                {
                    "type": "security",
                    "severity": "medium",
                    "file": "global",
                    "message": "No .env file found for environment variables",
                    "recommendation": "Use environment variables for configuration",
                }
            )

    def _audit_accessibility(self):
        """Audit for accessibility issues"""
        print("[ACCESSIBILITY] Auditing accessibility...")

        for root, dirs, files in os.walk(self.frontend_dir):
            dirs[:] = [d for d in dirs if d not in ["node_modules", ".next"]]
            for file in files:
                if file.endswith(".tsx"):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                            # Check for alt text on images
                            if "<img" in content and "alt=" not in content:
                                self.issues["high"].append(
                                    {
                                        "type": "accessibility",
                                        "severity": "high",
                                        "file": str(file_path),
                                        "message": "Image without alt attribute",
                                        "recommendation": "Add alt text for accessibility",
                                    }
                                )

                            # Check for button elements without text
                            if "<button" in content:
                                # Simple check - could be improved
                                pass
                    except:
                        pass

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        print("\n[REPORT] Generating audit report...")

        total_issues = sum(len(issues) for issues in self.issues.values())

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_issues": total_issues,
                "critical_issues": len(self.issues["critical"]),
                "high_issues": len(self.issues["high"]),
                "medium_issues": len(self.issues["medium"]),
                "low_issues": len(self.issues["low"]),
            },
            "metrics": self.metrics,
            "issues": self.issues,
            "health_score": self._calculate_health_score(),
        }

        return report

    def _calculate_health_score(self) -> int:
        """Calculate overall health score (0-100)"""
        score = 100

        # Deduct points based on severity
        score -= len(self.issues["critical"]) * 10
        score -= len(self.issues["high"]) * 5
        score -= len(self.issues["medium"]) * 2
        score -= len(self.issues["low"]) * 0.5

        return max(0, min(100, int(score)))


def main():
    """Main audit execution"""
    auditor = FrontendAuditor()
    report = auditor.audit_all()

    # Save report
    output_file = Path("BATCH_16_FRONTEND_AUDIT_REPORT.json")
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n[SUCCESS] Audit complete! Report saved to {output_file}")
    print("\n[SUMMARY] Results:")
    print(f"  Health Score: {report['health_score']}/100")
    print(f"  Total Files: {report['metrics']['total_files']}")
    print(f"  Total Issues: {report['summary']['total_issues']}")
    print(f"    - Critical: {report['summary']['critical_issues']}")
    print(f"    - High: {report['summary']['high_issues']}")
    print(f"    - Medium: {report['summary']['medium_issues']}")
    print(f"    - Low: {report['summary']['low_issues']}")


if __name__ == "__main__":
    main()
