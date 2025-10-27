# Storyboard Canvas User Guide

## Overview

The Storyboard Canvas is a powerful UI refinement tool that allows you to capture screenshots of your PaiiD dashboard, annotate them with feedback and design ideas, and export/share your mockups with your team.

**Think of it as your visual sketchpad for UI improvements** - no design tools required!

---

## Activating Storyboard Mode

### Method 1: Global Hotkey (Recommended)
Press **Ctrl + Shift + S** anywhere in the app to instantly open the Storyboard Canvas.

### Method 2: Floating Button
Click the floating purple **📋 button** in the bottom-right corner of your screen. You can drag this button anywhere you like!

---

## Features

### 1. Screenshot Capture
- **Initial Capture**: Click "Capture Screenshot" to take a snapshot of your current screen
- **The storyboard modal will temporarily hide** to capture a clean screenshot
- Your screenshot will appear in the canvas, ready for annotation

### 2. Annotation Tools

#### Select Tool (↖)
- Default tool for navigating the canvas
- Use when you're not drawing annotations

#### Arrow Tool (→)
- **Best for**: Pointing to specific UI elements with directional feedback
- **How to use**:
  1. Click the "Arrow" button
  2. Click and drag from start point to end point
  3. Release to create arrow
- **Example uses**:
  - "Move this button here →"
  - "This should connect to that section"
  - "User flow goes from here to there"

#### Box Tool (□)
- **Best for**: Highlighting regions or marking areas for changes
- **How to use**:
  1. Click the "Box" button
  2. Click and drag to create a rectangular outline
  3. Release to finalize
- **Example uses**:
  - Outlining a section that needs redesign
  - Marking a new component area
  - Drawing wireframe elements

#### Text Tool (T)
- **Best for**: Adding detailed comments and explanations
- **How to use**:
  1. Click the "Text" button
  2. Click where you want to add text
  3. Type your comment in the popup
  4. Press Enter to add (or Escape to cancel)
- **Example uses**:
  - "This button should say 'Execute Trade' instead"
  - "Add real-time price feed here"
  - "Move this 20px down"

#### Highlight Tool (▮)
- **Best for**: Emphasizing specific areas with translucent color
- **How to use**:
  1. Click the "Highlight" button
  2. Click and drag over the area to highlight
  3. Release to apply semi-transparent overlay
- **Example uses**:
  - Showing which sections need attention
  - Marking "keep this" vs "change this" areas
  - Categorizing feedback by color

### 3. Color Picker
Choose from 6 annotation colors:
- 🔴 **Red** (#ef4444) - Critical changes, errors
- 🟠 **Orange** (#f59e0b) - Warnings, medium priority
- 🟢 **Green** (#10b981) - Positive feedback, "keep this"
- 🔵 **Blue** (#3b82f6) - General notes, information
- 🟣 **Purple** (#8b5cf6) - New feature ideas
- 🌸 **Pink** (#ec4899) - Design/aesthetic feedback

### 4. Undo & Clear
- **Undo (Ctrl+Z)**: Remove the last annotation you added
- **Clear All**: Remove all annotations (requires confirmation)

---

## Version History

### Saving Versions
1. Add your annotations to the screenshot
2. Enter a version title (e.g., "Navigation Redesign v1", "Dark Mode Mockup")
3. Click "Save Current State"
4. Your version is saved to localStorage

### Loading Previous Versions
1. Click "Versions (N)" in the header to open the sidebar
2. Browse through saved versions (newest first)
3. Click "Load" to restore that version
4. The screenshot and all annotations will be restored

### Deleting Versions
- Click "Delete" on any version in the Version History sidebar
- Permanent deletion (no undo)

---

## Exporting & Sharing

### Export as PNG
1. Click "Export PNG" in the header
2. A high-quality PNG image will download to your computer
3. File name format: `storyboard-{timestamp}.png`
4. **Use for**: Sharing via Slack, email, GitHub issues

### Export as PDF
1. Click "Export PDF" in the header
2. A PDF document will download with your annotated screenshot
3. File name format: `storyboard-{timestamp}.pdf`
4. **Use for**: Formal design reviews, documentation, client presentations

### Sharing via Link (Coming Soon)
Currently, versions are saved locally in your browser (localStorage). Future updates will include cloud storage and shareable links.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl + Shift + S** | Open Storyboard Canvas |
| **Ctrl + Z** | Undo last annotation |
| **Escape** | Close Storyboard Canvas |
| **Enter** | Confirm text annotation |

---

## Best Practices

### 1. Use Descriptive Version Titles
❌ Bad: "Version 1", "Screenshot 2"
✅ Good: "Radial Menu - Hover States", "Trade Form - Mobile Layout"

### 2. Combine Tools for Clarity
- Use **arrows** to point + **text** to explain
- Use **highlights** to categorize + **boxes** to group
- Example: Highlight problem areas in red, then add text notes explaining the issue

### 3. Save Versions Frequently
- Save after each major round of annotations
- Think of versions like Git commits - small, focused changes
- Easier to compare "before" and "after" when you have granular versions

### 4. Color Code Your Feedback
Establish a color convention with your team:
- Red = Must fix (bugs, critical UX issues)
- Orange = Should fix (nice-to-have improvements)
- Green = Keep/highlight good design
- Blue = Questions or discussion points
- Purple = New feature ideas
- Pink = Visual/design polish

### 5. Export Before Major Changes
- Export to PNG/PDF before deploying changes
- Keeps a record of "what we were thinking" for future reference
- Useful for design documentation

---

## Common Use Cases

### Use Case 1: UI Bug Reporting
1. Capture screenshot of the bug
2. Use **red arrow** to point to the issue
3. Add **text** annotation: "Prices not updating in real-time"
4. Use **box** to show where the fix should be
5. Export PNG and attach to GitHub issue

### Use Case 2: Design Iteration
1. Capture current design
2. Save as "Current Design"
3. Use **purple highlights** to mark new feature areas
4. Add **text** with feature descriptions
5. Save as "Proposed Design v1"
6. Compare versions in sidebar

### Use Case 3: User Flow Documentation
1. Capture key screens in your workflow
2. Use **arrows** to show user flow
3. Number your arrows (1, 2, 3...) with text annotations
4. Add **boxes** around interactive elements
5. Export PDF as "User Flow Documentation"

### Use Case 4: Client/Stakeholder Feedback
1. Capture demo/prototype screenshot
2. Use **green highlights** on approved sections
3. Use **orange boxes** on sections that need revision
4. Add detailed **text** notes for each revision
5. Export PDF and email to stakeholder

### Use Case 5: Responsive Design Planning
1. Capture desktop view
2. Save as "Desktop Layout"
3. Use **boxes** to show how components will stack on mobile
4. Add **text** with breakpoint notes (e.g., "< 768px: stack vertically")
5. Save as "Mobile Layout Plan"

---

## Tips & Tricks

### Draggable Floating Button
- The 📋 button can be dragged to any corner of your screen
- Hover for a pulse effect
- Position it where it won't block important UI

### Text Annotation Tips
- Keep text concise (1-2 sentences max)
- Use ALL CAPS for emphasis
- Use emojis for quick visual cues (⚠️ 🎨 🔧 💡)

### When to Use Each Tool
- **Arrow**: "This goes here", "User clicks this"
- **Box**: "This whole section needs work", "Add component here"
- **Text**: Detailed explanations, questions, specifications
- **Highlight**: "Focus on this area", "This is good/bad"

### Working with Multiple Annotations
- Add annotations in order (1, 2, 3...) to show sequence
- Use consistent colors for related feedback
- Group annotations spatially (all feedback on header in one area)

---

## Troubleshooting

### Screenshot Capture Fails
- **Issue**: Black screen or error message
- **Solution**: Ensure browser has screenshot permissions
- **Workaround**: Use built-in OS screenshot tool, then paste into image editor

### Annotations Not Appearing
- **Issue**: Click/drag doesn't create annotation
- **Solution**: Ensure you've selected a tool (not "Select" mode)
- **Check**: Look for highlighted tool button

### Versions Not Saving
- **Issue**: "Save Current State" doesn't work
- **Solution**: Check browser localStorage isn't full
- **Workaround**: Export PNG/PDF instead, delete old versions

### Floating Button Not Visible
- **Issue**: Can't find the 📋 button
- **Solution**: Look in bottom-right corner, it may be dragged off-screen
- **Workaround**: Use Ctrl+Shift+S hotkey instead

### Can't Drag Floating Button
- **Issue**: Button won't move
- **Solution**: Click and hold (don't just click)
- **Note**: Button becomes semi-transparent when dragging

---

## Limitations (MVP Version)

The current Storyboard Canvas is an MVP with these limitations:

❌ **Not Yet Available**:
- Drag-and-drop UI component library
- Cloud storage for share links
- Real-time collaboration
- Before/after comparison slider
- Undo history beyond last action
- Shape rotation/resizing after creation

✅ **Available Now**:
- Screenshot capture
- 5 annotation tools
- 6 color options
- Version history (localStorage)
- PNG/PDF export
- Global hotkeys

**Future updates will expand functionality!**

---

## Keyboard Shortcuts Quick Reference

```
Global Hotkeys:
  Ctrl + Shift + S  →  Open Storyboard Canvas
  Ctrl + K          →  Open AI Chat
  Ctrl + T          →  Quick Trade
  Ctrl + P          →  View Positions
  Ctrl + R          →  Research
  Escape            →  Close Modal

Storyboard Shortcuts:
  Ctrl + Z          →  Undo Last Annotation
  Escape            →  Close Storyboard Canvas
  Enter             →  Confirm Text Annotation
```

---

## Feedback & Feature Requests

Have ideas for the Storyboard Canvas? Contact the development team:

- **Bug Reports**: Create a GitHub issue with "Storyboard:" prefix
- **Feature Requests**: Add to project backlog
- **Design Feedback**: Use the storyboard tool itself to show us! 😄

---

## Version History

- **v1.0.0** (Initial Release)
  - Screenshot capture
  - 5 annotation tools (arrow, box, text, highlight, select)
  - 6 color options
  - Version history (localStorage)
  - PNG/PDF export
  - Global hotkey (Ctrl+Shift+S)
  - Draggable floating button

---

## Related Documentation

- [Keyboard Shortcuts Guide](./KEYBOARD_SHORTCUTS.md) (coming soon)
- [UI Design System](./DESIGN_SYSTEM.md) (coming soon)
- [Contributing Guidelines](../CONTRIBUTING.md) (coming soon)

---

**Happy Storyboarding! 🎨📋**
