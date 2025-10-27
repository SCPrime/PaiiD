# Storyboard Canvas - Quick Start Guide

## TL;DR - 30 Second Guide

1. Press **Ctrl + Shift + S** (or click the purple 📋 button)
2. Click **"Capture Screenshot"**
3. Select a tool (Arrow, Box, Text, Highlight)
4. Click and drag on the screenshot to annotate
5. Click **"Export PNG"** to save

**That's it!** You're now annotating your UI.

---

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Storyboard Canvas          [Versions] [Export PNG] [Export PDF] [Close] │
│  Capture, annotate, and refine your UI ideas                     │
├──────────────┬──────────────────────────────────┬────────────────┤
│              │                                  │                │
│  Tools       │        Canvas                    │   Versions     │
│  ────────    │                                  │   (optional)   │
│              │  [Your screenshot appears here]  │                │
│  ↖ Select    │                                  │   ┌──────────┐ │
│  → Arrow     │  Click and drag to annotate      │   │ Version 1│ │
│  □ Box       │                                  │   │ [image]  │ │
│  T Text      │  Annotations appear as you draw  │   │ Load Del │ │
│  ▮ Highlight │                                  │   └──────────┘ │
│              │                                  │                │
│  Colors:     │                                  │   ┌──────────┐ │
│  🔴🟠🟢🔵🟣🌸    │                                  │   │ Version 2│ │
│              │                                  │   │ [image]  │ │
│  [Undo]      │                                  │   │ Load Del │ │
│  [Clear All] │                                  │   └──────────┘ │
│              │                                  │                │
│  Save Version│                                  │                │
│  [Title...]  │                                  │                │
│  [Save]      │                                  │                │
│              │                                  │                │
└──────────────┴──────────────────────────────────┴────────────────┘
```

---

## The 5 Tools Explained

### 1. Select Tool (↖)
**When to use:** When you're done drawing and want to navigate
- Click to switch back to normal cursor
- No drawing happens in this mode

### 2. Arrow Tool (→)
**When to use:** Point to specific UI elements
- Click and drag from start → end
- Creates directional arrow with arrowhead
- **Best for:** "Move this here", "User clicks this"

```
Example:
   Start here → [Button]
                   ↓
              "User clicks"
```

### 3. Box Tool (□)
**When to use:** Highlight regions or mark areas
- Click and drag to create rectangle outline
- **Best for:** "This section needs redesign", "Add component here"

```
Example:
   ┌─────────────────┐
   │  Redesign this  │
   │     section     │
   └─────────────────┘
```

### 4. Text Tool (T)
**When to use:** Add detailed comments
- Click where you want text
- Type in popup, press Enter
- **Best for:** Detailed feedback, specifications, questions

```
Example:
   "Change button text to 'Execute Trade'"
   "Add real-time price feed here"
   "Move this 20px down"
```

### 5. Highlight Tool (▮)
**When to use:** Emphasize specific areas
- Click and drag to create translucent overlay
- **Best for:** "Focus on this", color-coding feedback

```
Example:
   ▓▓▓▓▓▓▓▓▓▓▓▓
   ▓ Important ▓
   ▓▓▓▓▓▓▓▓▓▓▓▓
```

---

## Workflow Examples

### Quick Bug Report (30 seconds)
1. Press **Ctrl+Shift+S**
2. Click **Capture Screenshot**
3. Select **Arrow** tool (red color)
4. Point arrow at bug
5. Select **Text** tool
6. Click near arrow, type: "Prices not updating"
7. Press **Enter**
8. Click **Export PNG**
9. Attach to bug report

### Design Iteration (2 minutes)
1. Press **Ctrl+Shift+S**
2. Click **Capture Screenshot**
3. Enter version title: "Current Design"
4. Click **Save Current State**
5. Select **Highlight** tool (purple color)
6. Highlight areas for new features
7. Select **Text** tool
8. Add feature descriptions
9. Enter version title: "Proposed Design v1"
10. Click **Save Current State**
11. Click **Versions** to compare

### Client Feedback (5 minutes)
1. Press **Ctrl+Shift+S**
2. Click **Capture Screenshot**
3. Use **green highlights** on approved sections
4. Use **orange boxes** on sections needing revision
5. Use **text** annotations for detailed notes
6. Click **Export PDF**
7. Email PDF to client

---

## Color Coding Best Practices

Establish a convention with your team:

| Color | Meaning | Example Use |
|-------|---------|-------------|
| 🔴 Red | Must fix (critical) | Bugs, broken features, UX blockers |
| 🟠 Orange | Should fix (medium) | Nice-to-have improvements |
| 🟢 Green | Keep/approve | Good design, highlight strengths |
| 🔵 Blue | Questions | Discussion points, need clarification |
| 🟣 Purple | New features | Ideas, future enhancements |
| 🌸 Pink | Design polish | Visual/aesthetic feedback |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Ctrl + Shift + S** | Open storyboard |
| **Ctrl + Z** | Undo last annotation |
| **Escape** | Close storyboard |
| **Enter** | Confirm text annotation |

---

## Common Questions

### Q: Where are my versions saved?
**A:** In your browser's localStorage (local to this computer). Future updates will add cloud storage.

### Q: Can I edit annotations after creating them?
**A:** Not in MVP. Use Undo (Ctrl+Z) to remove and redraw.

### Q: What's the max file size for versions?
**A:** Browser localStorage is ~5-10MB. Save ~20-50 versions depending on screenshot size.

### Q: Can I share storyboards with my team?
**A:** Export PNG/PDF and share via email/Slack. Native sharing coming in Phase 2.

### Q: Does this work on mobile?
**A:** Not optimized for mobile yet. Desktop Chrome/Edge recommended.

---

## Tips for Great Annotations

### 1. Layer Your Feedback
- Start with **highlights** to categorize
- Add **arrows** to point
- Finish with **text** for details

### 2. Number Your Annotations
Use text annotations with numbers:
```
1 → Click here first
2 → Then this opens
3 → Finally user sees this
```

### 3. Use Consistent Colors
Don't switch colors randomly. Pick a color per category:
- Red = bugs
- Orange = improvements
- Purple = new features

### 4. Keep Text Concise
❌ "This button needs to be bigger and should have better colors and maybe a different font"
✅ "Increase button size 20%. Use accent color."

### 5. Save Versions Early and Often
Like Git commits, save small incremental changes:
- ✅ "Header feedback"
- ✅ "Navigation improvements"
- ✅ "Trade form redesign"

---

## Troubleshooting

### Screenshot is blank or black
- Ensure browser has permissions
- Try closing/reopening storyboard (Ctrl+Shift+S twice)
- Use OS screenshot tool as fallback

### Annotations not appearing
- Check you've selected a tool (not "Select")
- Look for highlighted tool button on left sidebar

### Can't drag floating button
- Click and **hold** (don't just tap)
- Button becomes semi-transparent when dragging

### Version save fails
- LocalStorage may be full (delete old versions)
- Export important versions as PNG/PDF backup

---

## What's Next?

After mastering the basics:
1. Read full guide: `docs/STORYBOARD_USER_GUIDE.md`
2. Try all 5 annotation tools
3. Experiment with color coding
4. Save and compare versions
5. Export to PNG/PDF
6. Share with your team!

---

**Pro tip:** Use Ctrl+Shift+S as a "quick sketch pad" during live calls. Capture → Annotate → Export in under 60 seconds.

---

**Need help?** See full documentation in `docs/STORYBOARD_USER_GUIDE.md`
