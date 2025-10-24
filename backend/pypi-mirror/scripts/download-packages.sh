#!/bin/bash
# Download pip-audit and all its dependencies to the local mirror
# This script should be run once to populate the mirror with packages

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIRROR_DIR="$(dirname "$SCRIPT_DIR")/simple"

echo "=== PaiiD Internal PyPI Mirror Setup ==="
echo "Mirror directory: $MIRROR_DIR"
echo ""

# Create temporary directory for downloads
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "📦 Downloading pip-audit and dependencies..."

# Download pip-audit and all dependencies using pip download
pip download \
    --dest "$TEMP_DIR" \
    --no-cache-dir \
    pip-audit

echo ""
echo "📋 Downloaded packages:"
ls -lh "$TEMP_DIR"

echo ""
echo "🔧 Organizing packages into mirror structure..."

# Process each package
for package in "$TEMP_DIR"/*.{whl,tar.gz}; do
    if [ -f "$package" ]; then
        filename=$(basename "$package")

        # Extract package name (everything before the version number)
        # Handle both wheel (.whl) and source (.tar.gz) formats
        if [[ "$filename" == *.whl ]]; then
            # Wheel format: package_name-version-py3-none-any.whl
            pkg_name=$(echo "$filename" | sed 's/-[0-9].*//' | tr '_' '-' | tr '[:upper:]' '[:lower:]')
        else
            # Source format: package-name-version.tar.gz
            pkg_name=$(echo "$filename" | sed 's/-[0-9].*//' | tr '_' '-' | tr '[:upper:]' '[:lower:]')
        fi

        # Create package directory if it doesn't exist
        pkg_dir="$MIRROR_DIR/$pkg_name"
        mkdir -p "$pkg_dir"

        # Copy package file
        cp "$package" "$pkg_dir/"
        echo "  ✓ $pkg_name: $filename"
    fi
done

echo ""
echo "🌐 Generating simple repository index files..."

# Generate index.html for each package directory
for pkg_dir in "$MIRROR_DIR"/*; do
    if [ -d "$pkg_dir" ]; then
        pkg_name=$(basename "$pkg_dir")
        index_file="$pkg_dir/index.html"

        echo "<!DOCTYPE html>" > "$index_file"
        echo "<html>" >> "$index_file"
        echo "<head><title>Links for $pkg_name</title></head>" >> "$index_file"
        echo "<body><h1>Links for $pkg_name</h1>" >> "$index_file"

        # Add links to all package files
        for pkg_file in "$pkg_dir"/*.{whl,tar.gz}; do
            if [ -f "$pkg_file" ]; then
                filename=$(basename "$pkg_file")
                echo "<a href=\"$filename\">$filename</a><br/>" >> "$index_file"
            fi
        done

        echo "</body></html>" >> "$index_file"
        echo "  ✓ Generated index for $pkg_name"
    fi
done

# Generate root index.html
root_index="$MIRROR_DIR/index.html"
echo "<!DOCTYPE html>" > "$root_index"
echo "<html>" >> "$root_index"
echo "<head><title>PaiiD Internal PyPI Mirror</title></head>" >> "$root_index"
echo "<body><h1>Simple Index</h1>" >> "$root_index"

for pkg_dir in "$MIRROR_DIR"/*; do
    if [ -d "$pkg_dir" ]; then
        pkg_name=$(basename "$pkg_dir")
        echo "<a href=\"$pkg_name/\">$pkg_name</a><br/>" >> "$root_index"
    fi
done

echo "</body></html>" >> "$root_index"

echo ""
echo "✅ Mirror setup complete!"
echo ""
echo "📊 Summary:"
echo "  - Total packages: $(find "$MIRROR_DIR" -maxdepth 1 -type d | wc -l | xargs)"
echo "  - Total files: $(find "$MIRROR_DIR" -name '*.whl' -o -name '*.tar.gz' | wc -l)"
echo "  - Mirror size: $(du -sh "$MIRROR_DIR" | cut -f1)"
echo ""
echo "🚀 Next steps:"
echo "  1. Test the mirror: cd $SCRIPT_DIR && python serve-mirror.py"
echo "  2. Configure pip: See ../pip.conf or set PIP_INDEX_URL"
echo "  3. Test installation: pip install --index-url http://localhost:8080/simple pip-audit"
