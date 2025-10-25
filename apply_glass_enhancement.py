import re

#!/usr/bin/env python3
"""
Apply Premium Glass Morphism Enhancement to RadialMenu.tsx
Batch implementation of all visual improvements
"""


def apply_enhancements():
    file_path = 'frontend/components/RadialMenu.tsx'

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("🎨 Applying Premium Glass Morphism Enhancements...")

    # ========== LAYER 1: Enhanced Shadow Filter ==========
    print("📦 Layer 1: Enhancing shadow filters...")

    old_shadow = r'''    // ====== SVG FILTERS ======

    // Normal shadow filter
    const normalShadow = defs
      \.append\("filter"\)
      \.attr\("id", "normalShadow"\)
      \.attr\("height", "150%"\)
      \.attr\("width", "150%"\);
    normalShadow\.append\("feGaussianBlur"\)\.attr\("in", "SourceAlpha"\)\.attr\("stdDeviation", "3"\);
    normalShadow\.append\("feOffset"\)\.attr\("dx", "0"\)\.attr\("dy", "2"\)\.attr\("result", "offsetblur"\);
    normalShadow
      \.append\("feComponentTransfer"\)
      \.append\("feFuncA"\)
      \.attr\("type", "linear"\)
      \.attr\("slope", "0\.4"\);
    const normalMerge = normalShadow\.append\("feMerge"\);
    normalMerge\.append\("feMergeNode"\);
    normalMerge\.append\("feMergeNode"\)\.attr\("in", "SourceGraphic"\);'''

    new_shadow = '''    // ====== SVG FILTERS ======
    // 🎨 PREMIUM GLASS MORPHISM: Professional depth and refinement

    // Enhanced shadow filter (3-layer depth system)
    const normalShadow = defs
      .append("filter")
      .attr("id", "normalShadow")
      .attr("height", "200%")
      .attr("width", "200%")
      .attr("x", "-50%")
      .attr("y", "-50%");

    // Layer 1: Primary drop shadow
    normalShadow
      .append("feGaussianBlur")
      .attr("in", "SourceAlpha")
      .attr("stdDeviation", "4")
      .attr("result", "blur1");
    normalShadow.append("feOffset").attr("in", "blur1").attr("dx", "0").attr("dy", "3").attr("result", "dropShadow");
    normalShadow
      .append("feFlood")
      .attr("flood-color", "#000000")
      .attr("flood-opacity", "0.3")
      .attr("result", "dropColor");
    normalShadow
      .append("feComposite")
      .attr("in", "dropColor")
      .attr("in2", "dropShadow")
      .attr("operator", "in")
      .attr("result", "shadow1");

    // Layer 2: Ambient shadow
    normalShadow
      .append("feGaussianBlur")
      .attr("in", "SourceAlpha")
      .attr("stdDeviation", "8")
      .attr("result", "blur2");
    normalShadow
      .append("feFlood")
      .attr("flood-color", "#000000")
      .attr("flood-opacity", "0.15")
      .attr("result", "ambientColor");
    normalShadow
      .append("feComposite")
      .attr("in", "ambientColor")
      .attr("in2", "blur2")
      .attr("operator", "in")
      .attr("result", "shadow2");

    // Layer 3: Edge highlight
    normalShadow
      .append("feGaussianBlur")
      .attr("in", "SourceAlpha")
      .attr("stdDeviation", "1")
      .attr("result", "edgeBlur");
    normalShadow
      .append("feFlood")
      .attr("flood-color", "#ffffff")
      .attr("flood-opacity", "0.08")
      .attr("result", "edgeColor");
    normalShadow
      .append("feComposite")
      .attr("in", "edgeColor")
      .attr("in2", "edgeBlur")
      .attr("operator", "in")
      .attr("result", "edgeHighlight");

    // Composite all layers
    const normalMerge = normalShadow.append("feMerge");
    normalMerge.append("feMergeNode").attr("in", "shadow2");
    normalMerge.append("feMergeNode").attr("in", "shadow1");
    normalMerge.append("feMergeNode").attr("in", "SourceGraphic");
    normalMerge.append("feMergeNode").attr("in", "edgeHighlight");'''

    content = re.sub(old_shadow, new_shadow, content, flags=re.DOTALL)

    # Save
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Layer 1 complete: Enhanced shadow filters applied!")
    print(f"📄 File updated: {file_path}")
    print("🎯 Next: Test with 'npm run dev' in frontend/")

if __name__ == "__main__":
    apply_enhancements()
