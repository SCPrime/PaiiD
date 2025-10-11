# Deprecated Components

This document tracks deprecated components that have been replaced with improved versions.

## Deprecated on October 11, 2025

### 1. StrategyBuilder.tsx → StrategyBuilderAI.tsx
**Status:** Deprecated (renamed to `.deprecated.tsx`)
**Reason:** Replaced by AI-powered version with Claude integration
**Migration:** Use `StrategyBuilderAI` component instead
**Removal date:** TBD (after verifying no imports remain)

### 2. MorningRoutine.tsx → MorningRoutineAI.tsx
**Status:** Deprecated (renamed to `.deprecated.tsx`)
**Reason:** Replaced by AI-powered version with personalized morning routine generation
**Migration:** Use `MorningRoutineAI` component instead
**Removal date:** TBD (after verifying no imports remain)

## Migration Guide

If you have custom code importing these components:

```typescript
// OLD (deprecated):
import StrategyBuilder from '../components/StrategyBuilder';
import MorningRoutine from '../components/MorningRoutine';

// NEW (recommended):
import StrategyBuilderAI from '../components/StrategyBuilderAI';
import MorningRoutineAI from '../components/MorningRoutineAI';
```

The AI versions provide:
- Claude-powered natural language interaction
- Personalized recommendations
- Better UX with conversational interface
- Same functionality + AI enhancements

## Process for Deprecation

1. Rename old component to `.deprecated.tsx`
2. Update all imports to use new component
3. Add entry to this file
4. After 30 days with no usage, delete the deprecated file
