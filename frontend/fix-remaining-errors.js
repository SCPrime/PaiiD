#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const fixes = {
  // Fix all unescaped quotes in one go
  'components/StrategyBuilder.deprecated.tsx': [
    {from: 'Customize "template" strategies', to: 'Customize &quot;template&quot; strategies'},
    {from: 'Design your own "custom" strategies', to: 'Design your own &quot;custom&quot; strategies'},
  ],
  'components/StrategyBuilderAI.tsx': [
    {from: '//@ts-nocheck', to: ''},
    {from: '// @ts-nocheck', to: ''},
    {from: 'import { TrendingUp,', to: 'import {'},
    {from: 'GlassCard, GlassInput,', to: 'GlassCard,'},
    {from: 'const data = await response', to: 'const _data = await response'},
    {from: ' with "', to: ' with &quot;'},
    {from: '" warnings', to: '&quot; warnings'},
  ],
  'components/TemplateCustomizationModal.tsx': [
    {from: 'import { GlassCard, GlassButton, GlassInput, theme }', to: 'import { GlassButton, theme }'},
    {from: "You've customized", to: 'You&apos;ve customized'},
  ],
  'components/UserSetup.tsx': [
    {from: ', Rocket,', to: ','},
    {from: "I'm a", to: 'I&apos;m a'},
    {from: "I've been trading for", to: 'I&apos;ve been trading for'},
    {from: "I'd like to", to: 'I&apos;d like to'},
  ],
  'components/UserSetupAI.tsx': [
    {from: 'const user = getCurrentUser();', to: 'const _user = getCurrentUser();'},
    {from: "I'm ", to: 'I&apos;m '},
    {from: "I'm looking", to: 'I&apos;m looking'},
    {from: "import UserSetup from './UserSetup';", to: ''},
  ],
  'components/trading/PLComparisonChart.tsx': [
    {from: ', ISeriesApi,', to: ','},
    {from: '(value: number, position: any)', to: '(value: number, _position: any)'},
    {from: '(value: number, comparison: any)', to: '(value: number, _comparison: any)'},
  ],
  'components/trading/PLSummaryDashboard.tsx': [
    {from: 'function DashboardCard({ title, children, period }: {', to: 'function DashboardCard({ title, children, period: _period }: {'},
  ],
  'components/trading/ProposalReview.tsx': [
    {from: 'import { getCurrentUser }', to: 'import { _getCurrentUser: getCurrentUser }'},
  ],
  'components/trading/StrategyBuilder.tsx': [
    {from: 'import type { Strategy, ValidationResult, ValidationError, ValidationWarning }', to: 'import type { Strategy, ValidationResult }'},
  ],
  'components/trading/StrategySuggestionsModal.tsx': [
    {from: "don't align", to: 'don&apos;t align'},
  ],
  'components/trading/TodaySchedule.tsx': [
    {from: "Today's Schedule", to: 'Today&apos;s Schedule'},
  ],
  'pages/index.tsx': [
    {from: 'import { useBreakpoint, useIsMobile }', to: 'import { useIsMobile }'},
  ],
  'strategies/validator.ts': [
    {from: 'import { Strategy,', to: 'import {'},
    {from: 'function validateUniverse(u: any, errors: ValidationError[], warnings: ValidationWarning[])', to: 'function validateUniverse(u: any, errors: ValidationError[], _warnings: ValidationWarning[])'},
    {from: 'function validateEntry(e: any, errors: ValidationError[], warnings: ValidationWarning[])', to: 'function validateEntry(e: any, errors: ValidationError[], _warnings: ValidationWarning[])'},
    {from: 'function validateExits(e: any, errors: ValidationError[], warnings: ValidationWarning[])', to: 'function validateExits(e: any, errors: ValidationError[], _warnings: ValidationWarning[])'},
    {from: 'function validateRisk(r: any, errors: ValidationError[], warnings: ValidationWarning[])', to: 'function validateRisk(r: any, errors: ValidationError[], _warnings: ValidationWarning[])'},
    {from: 'function validateAutomation(a: any, errors: ValidationError[], warnings: ValidationWarning[])', to: 'function validateAutomation(a: any, errors: ValidationError[], _warnings: ValidationWarning[])'},
  ],
};

// Apply fixes
Object.entries(fixes).forEach(([file, replacements]) => {
  const filePath = path.join(__dirname, file);

  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  Skipping ${file} - file not found`);
    return;
  }

  let content = fs.readFileSync(filePath, 'utf8');
  let changed = false;

  replacements.forEach(({from, to}) => {
    const regex = new RegExp(from.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
    if (regex.test(content)) {
      content = content.replace(regex, to);
      changed = true;
    }
  });

  if (changed) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✓ Fixed ${file}`);
  } else {
    console.log(`- No changes for ${file}`);
  }
});

console.log('\n✓ All remaining fixes applied!');
