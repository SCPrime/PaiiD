#!/usr/bin/env python3
"""
Documentation Index Generator
Creates a comprehensive index of all active documentation in the codebase.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict


class DocumentationIndexGenerator:
    def __init__(self, base_dir: Path, inventory_csv: Path):
        self.base_dir = base_dir
        self.inventory_csv = inventory_csv
        self.active_docs = []
        self.categories = {
            "Setup & Installation": [],
            "API Documentation": [],
            "Operations & Deployment": [],
            "Architecture & Design": [],
            "Development Guides": [],
            "Testing & Quality": [],
            "Troubleshooting": [],
            "Project Management": [],
            "Other": [],
        }

    def load_active_documentation(self):
        """Load all active documentation files from inventory."""
        print("Loading active documentation files...")

        with open(self.inventory_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (
                    row["category"] == "Documentation"
                    and row["status"] == "current"
                    and row["extension"] == ".md"
                ):
                    self.active_docs.append(row)

        print(f"Found {len(self.active_docs)} active documentation files")
        return self.active_docs

    def categorize_document(self, file_info: Dict) -> str:
        """Categorize a document based on its name and content."""
        path = file_info["path"].lower()
        name = Path(file_info["path"]).name.lower()

        # Setup & Installation
        if any(
            keyword in path
            for keyword in [
                "setup",
                "install",
                "configuration",
                "config",
                "environment",
                "requirements",
                "dependencies",
                "quick-start",
                "getting-started",
            ]
        ):
            return "Setup & Installation"

        # API Documentation
        if any(
            keyword in path
            for keyword in ["api", "endpoint", "swagger", "openapi", "rest", "graphql"]
        ):
            return "API Documentation"

        # Operations & Deployment
        if any(
            keyword in path
            for keyword in [
                "deploy",
                "deployment",
                "production",
                "operations",
                "ops",
                "monitoring",
                "health",
                "status",
                "maintenance",
                "backup",
                "security",
                "auth",
                "authentication",
                "jwt",
                "redis",
            ]
        ):
            return "Operations & Deployment"

        # Architecture & Design
        if any(
            keyword in path
            for keyword in [
                "architecture",
                "design",
                "component",
                "structure",
                "schema",
                "database",
                "model",
                "entity",
                "migration",
            ]
        ):
            return "Architecture & Design"

        # Development Guides
        if any(
            keyword in path
            for keyword in [
                "development",
                "dev",
                "coding",
                "style",
                "guidelines",
                "workflow",
                "git",
                "commit",
                "pull",
                "review",
                "contributing",
            ]
        ):
            return "Development Guides"

        # Testing & Quality
        if any(
            keyword in path
            for keyword in [
                "test",
                "testing",
                "quality",
                "audit",
                "lint",
                "coverage",
                "validation",
                "verification",
                "checklist",
            ]
        ):
            return "Testing & Quality"

        # Troubleshooting
        if any(
            keyword in path
            for keyword in [
                "troubleshoot",
                "debug",
                "issue",
                "problem",
                "fix",
                "error",
                "bug",
                "incident",
                "report",
            ]
        ):
            return "Troubleshooting"

        # Project Management
        if any(
            keyword in path
            for keyword in [
                "project",
                "management",
                "plan",
                "roadmap",
                "status",
                "progress",
                "task",
                "workflow",
                "process",
                "methodology",
            ]
        ):
            return "Project Management"

        return "Other"

    def analyze_document_content(self, file_path: Path) -> Dict:
        """Analyze document content for metadata."""
        analysis = {
            "title": "",
            "description": "",
            "last_modified": "",
            "size": 0,
            "lines": 0,
            "has_toc": False,
            "has_links": False,
            "sections": [],
        }

        try:
            if not file_path.exists():
                return analysis

            # Get file stats
            stat = file_path.stat()
            analysis["size"] = stat.st_size
            analysis["last_modified"] = datetime.fromtimestamp(stat.st_mtime).strftime(
                "%Y-%m-%d"
            )

            # Read content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
                analysis["lines"] = len(lines)

                # Extract title (first # heading)
                for line in lines:
                    if line.startswith("# "):
                        analysis["title"] = line[2:].strip()
                        break

                # Extract description (first paragraph after title)
                in_description = False
                description_lines = []
                for line in lines:
                    if line.startswith("# "):
                        in_description = True
                        continue
                    elif in_description and line.strip():
                        if line.startswith("#"):
                            break
                        description_lines.append(line.strip())
                        if len(description_lines) >= 3:
                            break

                if description_lines:
                    analysis["description"] = " ".join(description_lines)[:200] + "..."

                # Check for table of contents
                analysis["has_toc"] = (
                    "## Table of Contents" in content or "## Contents" in content
                )

                # Check for links
                analysis["has_links"] = (
                    "[" in content and "]" in content and "(" in content
                )

                # Extract sections
                for line in lines:
                    if line.startswith("## "):
                        section = line[3:].strip()
                        if section and not section.startswith("#"):
                            analysis["sections"].append(section)

        except Exception as e:
            analysis["description"] = f"Error analyzing: {str(e)}"

        return analysis

    def generate_index(self):
        """Generate the documentation index."""
        print("Generating documentation index...")

        # Categorize all documents
        for doc in self.active_docs:
            category = self.categorize_document(doc)
            self.categories[category].append(doc)

        # Generate markdown content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        content = f"""# Documentation Index
**Generated**: {timestamp}  
**Total Active Documents**: {len(self.active_docs)}

This index provides a comprehensive overview of all active documentation in the PaiiD project. Documents are organized by category for easy navigation.

---

## Quick Navigation

"""

        # Add category links
        for category in self.categories.keys():
            if self.categories[category]:
                anchor = category.lower().replace(" ", "-").replace("&", "and")
                content += f"- [{category}](#{anchor}) ({len(self.categories[category])} docs)\n"

        content += "\n---\n\n"

        # Generate content for each category
        for category, docs in self.categories.items():
            if not docs:
                continue

            anchor = category.lower().replace(" ", "-").replace("&", "and")
            content += f"## {category} {{#{anchor}}}\n\n"

            if len(docs) == 0:
                content += "*No documents in this category.*\n\n"
                continue

            # Sort docs by name
            docs.sort(key=lambda x: x["path"])

            for doc in docs:
                file_path = self.base_dir / doc["path"]
                analysis = self.analyze_document_content(file_path)

                # Format document entry
                content += f"### [{Path(doc['path']).name}]({doc['path']})\n"

                if analysis["title"]:
                    content += f"**Title**: {analysis['title']}\n\n"

                if analysis["description"]:
                    content += f"**Description**: {analysis['description']}\n\n"

                # Add metadata
                metadata = []
                if analysis["last_modified"]:
                    metadata.append(f"Last Modified: {analysis['last_modified']}")
                if analysis["size"]:
                    metadata.append(f"Size: {analysis['size']} bytes")
                if analysis["lines"]:
                    metadata.append(f"Lines: {analysis['lines']}")

                if metadata:
                    content += f"**Metadata**: {' | '.join(metadata)}\n\n"

                # Add sections if available
                if analysis["sections"]:
                    content += f"**Sections**: {', '.join(analysis['sections'][:5])}"
                    if len(analysis["sections"]) > 5:
                        content += f" (and {len(analysis['sections']) - 5} more)"
                    content += "\n\n"

                # Add features
                features = []
                if analysis["has_toc"]:
                    features.append("Table of Contents")
                if analysis["has_links"]:
                    features.append("Internal Links")
                if doc["references"] and int(doc["references"]) > 0:
                    features.append(f"Referenced ({doc['references']} times)")

                if features:
                    content += f"**Features**: {' | '.join(features)}\n\n"

                content += "---\n\n"

        # Add summary statistics
        content += """## Summary Statistics

| Category | Documents | Total Size |
|----------|-----------|------------|
"""

        total_size = 0
        for category, docs in self.categories.items():
            if docs:
                category_size = sum(int(doc["size"]) for doc in docs)
                total_size += category_size
                content += (
                    f"| {category} | {len(docs)} | {category_size / 1024:.1f} KB |\n"
                )

        content += f"| **Total** | **{len(self.active_docs)}** | **{total_size / 1024:.1f} KB** |\n\n"

        # Add maintenance notes
        content += """## Maintenance Notes

### Adding New Documentation
1. Place new documentation in appropriate directory
2. Use descriptive filenames
3. Include title and description in document
4. Add table of contents for longer documents
5. Update this index after adding new docs

### Updating This Index
Run the documentation index generator:
```bash
python scripts/documentation-index-generator.py
```

### Documentation Standards
- Use clear, descriptive titles
- Include brief descriptions
- Add table of contents for documents >500 lines
- Use consistent formatting
- Link related documents
- Keep content up to date

---

*This index is automatically generated. For questions about specific documents, refer to the individual files or contact the project maintainers.*
"""

        return content

    def save_index(self, content: str):
        """Save the documentation index."""
        index_path = self.base_dir / "DOCUMENTATION_INDEX.md"

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Documentation index saved: {index_path}")
        return index_path

    def run(self):
        """Run the documentation index generator."""
        print("=" * 80)
        print("DOCUMENTATION INDEX GENERATOR")
        print("=" * 80)

        # Load active documentation
        self.load_active_documentation()

        if not self.active_docs:
            print("No active documentation files found!")
            return

        # Generate index
        content = self.generate_index()

        # Save index
        index_path = self.save_index(content)

        print("\nIndex generated successfully!")
        print(f"Total documents indexed: {len(self.active_docs)}")
        print(f"Categories: {len([c for c in self.categories.values() if c])}")
        print(f"Output: {index_path}")


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate documentation index")
    parser.add_argument(
        "--inventory",
        type=str,
        default="codebase-inventory.csv",
        help="Path to inventory CSV file",
    )

    args = parser.parse_args()

    base_dir = Path(r"C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD")
    inventory_path = base_dir / args.inventory

    if not inventory_path.exists():
        print(f"Error: Inventory file not found: {inventory_path}")
        return 1

    # Run generator
    generator = DocumentationIndexGenerator(base_dir, inventory_path)
    generator.run()

    return 0


if __name__ == "__main__":
    exit(main())
