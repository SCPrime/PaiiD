from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import json
import os
import shutil

#!/usr/bin/env python3
"""
PaiiD Codebase Optimizer
Cleans, optimizes, and tightens the codebase for production readiness
"""


class CodebaseOptimizer:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.optimization_log = []
        self.stats = {
            "files_processed": 0,
            "files_optimized": 0,
            "space_saved": 0,
            "warnings_fixed": 0
        }

    def log(self, message: str, level: str = "INFO"):
        """Log optimization actions"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.optimization_log.append(log_entry)
        # Use ASCII-safe printing
        safe_message = message.encode('ascii', 'ignore').decode('ascii')
        print(f"[{timestamp}] {level}: {safe_message}")

    def optimize_python_files(self) -> int:
        """Optimize Python files"""
        optimized = 0
        python_files = list(self.root_dir.rglob("*.py"))

        for file_path in python_files:
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_size = len(content)
                optimized_content = self._optimize_python_content(content)

                if len(optimized_content) < original_size:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(optimized_content)

                    space_saved = original_size - len(optimized_content)
                    self.stats["space_saved"] += space_saved
                    self.stats["files_optimized"] += 1
                    optimized += 1

                    self.log(f"Optimized {file_path.name} (-{space_saved} bytes)")

                self.stats["files_processed"] += 1

            except Exception as e:
                self.log(f"Error optimizing {file_path.name}: {e}", "ERROR")

        return optimized

    def _optimize_python_content(self, content: str) -> str:
        """Optimize Python code content"""
        lines = content.split('\n')
        optimized_lines = []

        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()

            # Remove empty lines at end of blocks
            if line.strip() == "" and optimized_lines and optimized_lines[-1].strip() == "":
                continue

            optimized_lines.append(line)

        return '\n'.join(optimized_lines)

    def optimize_typescript_files(self) -> int:
        """Optimize TypeScript/JavaScript files"""
        optimized = 0
        ts_files = list(self.root_dir.rglob("*.{ts,tsx,js,jsx}"))

        for file_path in ts_files:
            if "node_modules" in str(file_path) or ".next" in str(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                original_size = len(content)
                optimized_content = self._optimize_ts_content(content)

                if len(optimized_content) < original_size:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(optimized_content)

                    space_saved = original_size - len(optimized_content)
                    self.stats["space_saved"] += space_saved
                    self.stats["files_optimized"] += 1
                    optimized += 1

                    self.log(f"Optimized {file_path.name} (-{space_saved} bytes)")

                self.stats["files_processed"] += 1

            except Exception as e:
                self.log(f"Error optimizing {file_path.name}: {e}", "ERROR")

        return optimized

    def _optimize_ts_content(self, content: str) -> str:
        """Optimize TypeScript/JavaScript content"""
        lines = content.split('\n')
        optimized_lines = []

        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()

            # Remove empty lines at end of blocks
            if line.strip() == "" and optimized_lines and optimized_lines[-1].strip() == "":
                continue

            optimized_lines.append(line)

        return '\n'.join(optimized_lines)

    def clean_build_artifacts(self) -> int:
        """Clean build artifacts and temporary files"""
        cleaned = 0

        # Common build artifact patterns
        artifact_patterns = [
            "**/__pycache__",
            "**/node_modules",
            "**/.next",
            "**/dist",
            "**/build",
            "**/*.pyc",
            "**/*.pyo",
            "**/.DS_Store",
            "**/Thumbs.db"
        ]

        for pattern in artifact_patterns:
            for artifact_path in self.root_dir.glob(pattern):
                if artifact_path.is_dir():
                    shutil.rmtree(artifact_path, ignore_errors=True)
                    self.log(f"Cleaned directory: {artifact_path}")
                    cleaned += 1
                elif artifact_path.is_file():
                    artifact_path.unlink()
                    self.log(f"Cleaned file: {artifact_path}")
                    cleaned += 1

        return cleaned

    def optimize_imports(self) -> int:
        """Optimize import statements"""
        optimized = 0

        # Python files
        for py_file in self.root_dir.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                optimized_content = self._optimize_python_imports(content)

                if optimized_content != content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(optimized_content)

                    self.log(f"Optimized imports in {py_file.name}")
                    optimized += 1

            except Exception as e:
                self.log(f"Error optimizing imports in {py_file.name}: {e}", "ERROR")

        return optimized

    def _optimize_python_imports(self, content: str) -> str:
        """Optimize Python import statements"""
        lines = content.split('\n')
        import_lines = []
        other_lines = []

        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                import_lines.append(line)
            else:
                other_lines.append(line)

        # Sort imports
        import_lines.sort()

        # Combine imports
        result = []
        if import_lines:
            result.extend(import_lines)
            result.append('')  # Empty line after imports

        result.extend(other_lines)
        return '\n'.join(result)

    def generate_optimization_report(self) -> Dict:
        """Generate optimization report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "log": self.optimization_log,
            "summary": {
                "files_processed": self.stats["files_processed"],
                "files_optimized": self.stats["files_optimized"],
                "space_saved_bytes": self.stats["space_saved"],
                "space_saved_kb": round(self.stats["space_saved"] / 1024, 2),
                "optimization_rate": round(
                    (self.stats["files_optimized"] / max(self.stats["files_processed"], 1)) * 100, 2
                )
            }
        }

        return report

    def run_full_optimization(self):
        """Run complete codebase optimization"""
        self.log("Starting PaiiD Codebase Optimization")
        self.log("=" * 50)

        # Step 1: Clean build artifacts
        self.log("Cleaning build artifacts...")
        cleaned = self.clean_build_artifacts()
        self.log(f"Cleaned {cleaned} build artifacts")

        # Step 2: Optimize Python files
        self.log("Optimizing Python files...")
        py_optimized = self.optimize_python_files()
        self.log(f"Optimized {py_optimized} Python files")

        # Step 3: Optimize TypeScript files
        self.log("Optimizing TypeScript files...")
        ts_optimized = self.optimize_typescript_files()
        self.log(f"Optimized {ts_optimized} TypeScript files")

        # Step 4: Optimize imports
        self.log("Optimizing import statements...")
        imports_optimized = self.optimize_imports()
        self.log(f"Optimized imports in {imports_optimized} files")

        # Generate report
        report = self.generate_optimization_report()

        # Save report
        report_path = self.root_dir / "optimization-report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        self.log("=" * 50)
        self.log("Optimization Complete!")
        self.log(f"Files processed: {report['summary']['files_processed']}")
        self.log(f"Files optimized: {report['summary']['files_optimized']}")
        self.log(f"Space saved: {report['summary']['space_saved_kb']} KB")
        self.log(f"Optimization rate: {report['summary']['optimization_rate']}%")
        self.log(f"Report saved: {report_path}")

        return report

def main():
    """Main optimization function"""
    optimizer = CodebaseOptimizer()
    report = optimizer.run_full_optimization()

    print("\nOptimization Summary:")
    print(f"   Files processed: {report['summary']['files_processed']}")
    print(f"   Files optimized: {report['summary']['files_optimized']}")
    print(f"   Space saved: {report['summary']['space_saved_kb']} KB")
    print(f"   Optimization rate: {report['summary']['optimization_rate']}%")

if __name__ == "__main__":
    main()
