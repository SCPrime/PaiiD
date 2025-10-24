#!/usr/bin/env python3
"""
Simple HTTP server to serve the internal PyPI mirror for testing.
This is useful for local development and verification.

For production, use a proper HTTP server (nginx, Apache) or
a dedicated package index server (Artifactory, Nexus, devpi).

Usage:
    python serve-mirror.py [--port PORT] [--host HOST]

Example:
    python serve-mirror.py --port 8080 --host 0.0.0.0
"""

import argparse
import http.server
import os
import socketserver
from pathlib import Path


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with reduced logging."""

    def log_message(self, format, *args):
        """Only log errors and package downloads."""
        # Only log if it's a package download or error
        if self.path.endswith(('.whl', '.tar.gz')) or args[1][0] in ('4', '5'):
            print(f"{self.address_string()} - {format % args}")


def main():
    parser = argparse.ArgumentParser(
        description="Serve PaiiD internal PyPI mirror"
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port to serve on (default: 8080)'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )

    args = parser.parse_args()

    # Change to the simple/ directory
    script_dir = Path(__file__).parent
    mirror_dir = script_dir.parent / 'simple'

    if not mirror_dir.exists():
        print(f"❌ Error: Mirror directory not found: {mirror_dir}")
        print("   Run download-packages.sh first to populate the mirror.")
        return 1

    os.chdir(mirror_dir)

    # Count packages
    package_dirs = [d for d in mirror_dir.iterdir() if d.is_dir()]
    package_count = len(package_dirs)

    print("=" * 60)
    print("🚀 PaiiD Internal PyPI Mirror Server")
    print("=" * 60)
    print(f"📂 Serving: {mirror_dir}")
    print(f"📦 Packages: {package_count}")
    print(f"🌐 URL: http://{args.host}:{args.port}/")
    print(f"🔗 Index: http://{args.host}:{args.port}/simple")
    print("=" * 60)
    print("\nTo use this mirror with pip:")
    print(f"  pip install --index-url http://{args.host}:{args.port}/ pip-audit")
    print("\nOr set environment variable:")
    print(f"  export PIP_INDEX_URL=http://{args.host}:{args.port}/")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()

    # Create and start server
    try:
        with socketserver.TCPServer(
            (args.host, args.port),
            QuietHTTPRequestHandler
        ) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        return 0
    except OSError as e:
        print(f"\n❌ Error: {e}")
        if "Address already in use" in str(e):
            print(f"   Port {args.port} is already in use. Try a different port.")
        return 1


if __name__ == '__main__':
    exit(main())
