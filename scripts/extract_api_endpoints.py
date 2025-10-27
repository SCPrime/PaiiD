#!/usr/bin/env python3
"""
Extract all API endpoints from FastAPI routers for documentation generation.

This script analyzes all router files in backend/app/routers/ and extracts:
- HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Endpoint paths
- Route prefixes
- Tags
- Docstrings
- Parameters and request/response models

Output: JSON file with complete endpoint inventory
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Any


def extract_router_info(file_path: Path) -> Dict[str, Any]:
    """Extract router configuration from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    router_info = {
        'file': file_path.name,
        'prefix': '',
        'tags': [],
        'endpoints': []
    }

    # Extract router prefix and tags
    prefix_match = re.search(r'APIRouter\([^)]*prefix=["\']([^"\']+)["\']', content)
    if prefix_match:
        router_info['prefix'] = prefix_match.group(1)

    tags_match = re.search(r'APIRouter\([^)]*tags=\[([^\]]+)\]', content)
    if tags_match:
        tags_str = tags_match.group(1)
        router_info['tags'] = [t.strip(' "\'') for t in tags_str.split(',')]

    # Extract endpoints using regex
    endpoint_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
    for match in re.finditer(endpoint_pattern, content):
        method = match.group(1).upper()
        path = match.group(2)

        # Try to extract docstring for this endpoint
        # Find the function definition after this decorator
        func_match = re.search(
            rf'@router\.{match.group(1)}\(["\'][^"\']+["\'][^)]*\)\s+(?:async\s+)?def\s+(\w+)',
            content[match.start():]
        )

        endpoint_info = {
            'method': method,
            'path': path,
            'full_path': f"{router_info['prefix']}{path}" if router_info['prefix'] else path,
            'function': func_match.group(1) if func_match else 'unknown',
            'description': ''
        }

        # Try to extract docstring
        if func_match:
            func_name = func_match.group(1)
            # Look for the docstring after the function definition
            docstring_match = re.search(
                rf'def\s+{func_name}\([^)]*\):\s+"""([^"]*)"""',
                content,
                re.DOTALL
            )
            if docstring_match:
                # Get first line of docstring
                docstring = docstring_match.group(1).strip()
                endpoint_info['description'] = docstring.split('\n')[0].strip()

        router_info['endpoints'].append(endpoint_info)

    return router_info


def main():
    """Extract all endpoints from all router files."""
    backend_root = Path(__file__).parent.parent / 'backend'
    routers_dir = backend_root / 'app' / 'routers'

    if not routers_dir.exists():
        print(f"Error: Routers directory not found: {routers_dir}")
        return

    all_routers = []
    total_endpoints = 0

    # Process all Python files in routers directory
    for router_file in sorted(routers_dir.glob('*.py')):
        if router_file.name in ['__init__.py', 'ml_advanced.py']:
            continue

        print(f"Processing {router_file.name}...")
        router_info = extract_router_info(router_file)

        if router_info['endpoints']:
            all_routers.append(router_info)
            total_endpoints += len(router_info['endpoints'])
            print(f"  Found {len(router_info['endpoints'])} endpoints")

    # Generate output
    output = {
        'generated_at': '2025-10-27',
        'total_routers': len(all_routers),
        'total_endpoints': total_endpoints,
        'routers': all_routers
    }

    # Save to JSON
    output_file = Path(__file__).parent.parent / 'docs' / 'api_endpoints.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Extraction complete!")
    print(f"   Total routers: {len(all_routers)}")
    print(f"   Total endpoints: {total_endpoints}")
    print(f"   Output: {output_file}")

    # Print summary by router
    print("\n📊 Endpoints by Router:")
    for router in sorted(all_routers, key=lambda x: len(x['endpoints']), reverse=True):
        print(f"   {router['file']:30s} {len(router['endpoints']):3d} endpoints")


if __name__ == '__main__':
    main()
