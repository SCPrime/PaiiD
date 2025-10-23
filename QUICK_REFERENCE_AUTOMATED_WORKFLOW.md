# Quick Reference: Automated Dual-AI Workflow
## One-Page Cheat Sheet

---

## 🚀 Run Workflow (One Command)

```powershell
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD
.\dual-ai-orchestrator.ps1 -UserRequest "Your feature description"
```

---

## 📋 Three-Phase Process

| Phase | AI | You Do | Time |
|-------|----|---------|---------:|
| **1. Planning** | Claude Code (me) | Paste prompt in terminal | 5 min |
| **2. Execution** | Cursor AI (ChatGPT) | Paste prompt in Cursor (Ctrl+L) | 30-60 min |
| **3. Review** | Claude Code (me) | Paste prompt in terminal | 10 min |

**Total: 45-75 minutes** (vs 3-4 hours manual)

---

## 🎯 Labor Division

### Claude (High-Level Planning)
- ✅ Architecture design
- ✅ Breaking down complex tasks
- ✅ Technical decisions
- ✅ Security review
- ✅ Final approval
- ❌ Never writes code directly

### ChatGPT (Code Execution)
- ✅ Code implementation
- ✅ Running tests
- ✅ Fixing errors
- ✅ Logic checking
- ✅ Refactoring
- ❌ Never makes architecture decisions

---

## 📁 Workflow Files

| File | Created By | Purpose |
|------|------------|---------|
| `IMPLEMENTATION_PLAN.md` | Claude | Detailed specs for ChatGPT |
| `EXECUTION_LOG.md` | ChatGPT | Progress tracking |
| `REVIEW_RESULTS.md` | Claude | Final approval/feedback |

---

## 🎬 Example Usage

```powershell
# Simple feature
.\dual-ai-orchestrator.ps1 -UserRequest "Add loading spinner to options chain"

# Complex feature
.\dual-ai-orchestrator.ps1 -UserRequest "Add real-time Greeks calculation"

# With auto-commit
.\dual-ai-orchestrator.ps1 -UserRequest "Fix 500 error" -AutoCommit

# Manual mode (step-by-step)
.\dual-ai-orchestrator.ps1 -UserRequest "Feature" -Mode manual
```

---

## ⚡ Quick Commands

```powershell
# View current plan
cat IMPLEMENTATION_PLAN.md

# Check execution progress
cat EXECUTION_LOG.md

# See review results
cat REVIEW_RESULTS.md

# Clean up after commit
rm IMPLEMENTATION_PLAN.md, EXECUTION_LOG.md, REVIEW_RESULTS.md
```

---

## 🎯 Good User Requests

**✅ Good (Specific):**
```
"Add Greeks (delta, gamma, theta, vega) display to options chain"
"Fix 500 error on /api/options/OPTT endpoint"
"Refactor RadialMenu to use composition pattern"
```

**❌ Bad (Too vague):**
```
"Make it better"
"Fix bugs"
"Add features"
```

---

## 🔧 Options

| Flag | Effect |
|------|--------|
| `-UserRequest "..."` | Required: What to build |
| `-Mode auto` | Fully automatic (default) |
| `-Mode semi` | Pause at each phase |
| `-Mode manual` | Step-by-step with confirmations |
| `-AutoCommit` | Auto git commit when approved |
| `-SkipTests` | Skip test execution (faster but risky) |

---

## 🚨 When to Escalate

**ChatGPT escalates to Claude if:**
- Architecture decision needed
- Security concern found
- Specification unclear
- Breaking change required

**You'll see in EXECUTION_LOG.md:**
```
🚨 ESCALATE TO CLAUDE: [Question]
```

---

## ✅ Success Indicators

**Working well:**
- Plans complete in < 10 min
- 80%+ tasks succeed without escalation
- Tests pass on first or second try
- Reviews approve most code
- Development 50-60% faster

**Needs adjustment:**
- Frequent escalations
- Tests failing repeatedly
- Reviews rejecting often
- No time savings

---

## 📊 Typical Timeline

```
00:00 - Start orchestrator
00:01 - Claude planning prompt appears
00:05 - IMPLEMENTATION_PLAN.md created
00:06 - ChatGPT execution prompt appears
01:00 - ChatGPT completes all tasks
01:01 - Claude review prompt appears
01:10 - REVIEW_RESULTS.md created (APPROVED)
01:11 - Ready to commit!
```

---

## 🎓 First-Time Setup

```powershell
# 1. Navigate to project
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD

# 2. Verify files exist
ls .cursor/rules/dual-ai-automation.md
ls dual-ai-orchestrator.ps1

# 3. Run test workflow
.\dual-ai-orchestrator.ps1 -UserRequest "Add TypeScript interface for TradingSignal"

# 4. Watch it work!
```

---

## 💡 Pro Tips

1. **Be specific** in user requests
2. **Let it run** - don't intervene unless asked
3. **Trust ChatGPT** to fix errors (it will retry 3x)
4. **Review the logs** - learn from each workflow
5. **Adjust templates** based on your project needs

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| Orchestrator won't run | `cd` to project root first |
| Cursor doesn't open | Open manually: `cursor .` |
| Plan not created | Paste prompt in Claude Code terminal |
| Execution stalled | Check EXECUTION_LOG.md for escalations |
| Tests failing | ChatGPT will retry 3x automatically |

---

## 📞 Help

**Documentation:**
- Full guide: `AUTOMATED_WORKFLOW_GUIDE.md`
- Task assignment: `TASK_ASSIGNMENT_WORKFLOW.md`
- MCP setup: `MCP_VERIFICATION_REPORT.md`

**Files:**
- Rules: `.cursor/rules/dual-ai-automation.md`
- Templates: `.cursor/workflows/*.md`
- Orchestrator: `dual-ai-orchestrator.ps1`

---

## 🎯 Today's Quick Start

```powershell
# Copy and run this NOW:
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD
.\dual-ai-orchestrator.ps1 -UserRequest "Add loading spinner to options chain component"
```

**Then watch:**
1. Claude creates plan (5 min)
2. ChatGPT implements (15 min)
3. Claude reviews (5 min)
4. Done! (25 min total)

---

**Print this page and keep it handy!** 📋

---

**Created:** October 22, 2025
**Status:** Ready to use
**Next:** Run your first automated workflow! 🚀
