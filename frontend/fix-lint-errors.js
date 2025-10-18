#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

// List of file fixes
const fixes = [
  // RadialMenu.tsx - Fix unused variables
  {
    file: "components/RadialMenu.tsx",
    replacements: [
      {
        from: "const [hoveredWorkflow, setHoveredWorkflow] = useState<Workflow | null>(null);",
        to: "const [_hoveredWorkflow, setHoveredWorkflow] = useState<Workflow | null>(null);",
      },
      {
        from: "const [showAIChat, setShowAIChat] = useState(false);",
        to: "const [_showAIChat, setShowAIChat] = useState(false);",
      },
    ],
  },

  // index.tsx - Remove unused imports
  {
    file: "pages/index.tsx",
    replacements: [
      {
        from: "import PositionsTable from '../components/PositionsTable';",
        to: "",
      },
      {
        from: "import ResearchDashboardSimple from '../components/ResearchDashboardSimple';",
        to: "",
      },
      {
        from: "import ProposalReview from '../components/trading/ProposalReview';",
        to: "",
      },
      {
        from: "import UserSetup from '../components/UserSetup';",
        to: "",
      },
      {
        from: "import TradingJournal from '../components/TradingJournal';",
        to: "",
      },
      {
        from: "import RiskDashboard from '../components/RiskDashboard';",
        to: "",
      },
      {
        from: "import { isUserLoggedIn, initializeSession } from '../lib/userManagement';",
        to: "import { initializeSession } from '../lib/userManagement';",
      },
      {
        from: "const breakpoint = useBreakpoint();",
        to: "",
      },
    ],
  },

  // StrategyBuilderAI.tsx - Remove @ts-nocheck and fix unused imports
  {
    file: "components/StrategyBuilderAI.tsx",
    replacements: [
      {
        from: "// @ts-nocheck\n",
        to: "",
      },
      {
        from: "  TrendingUp,",
        to: "",
      },
      {
        from: "  GlassInput,",
        to: "",
      },
      {
        from: "const data = await response.json();",
        to: "const _data = await response.json();",
      },
      {
        from: 'Strategy validation passed with "',
        to: "Strategy validation passed with &quot;",
      },
      {
        from: '" warnings',
        to: "&quot; warnings",
      },
    ],
  },

  // TemplateCustomizationModal.tsx - Fix unused imports
  {
    file: "components/TemplateCustomizationModal.tsx",
    replacements: [
      {
        from: "  GlassCard,",
        to: "",
      },
      {
        from: "  GlassInput,",
        to: "",
      },
      {
        from: "const data = await response.json();",
        to: "const _data = await response.json();",
      },
      {
        from: "You've customized",
        to: "You&apos;ve customized",
      },
    ],
  },

  // TradingJournal.tsx - Remove unused imports
  {
    file: "components/TradingJournal.tsx",
    replacements: [
      {
        from: "  Filter,",
        to: "",
      },
      {
        from: "  Search,",
        to: "",
      },
      {
        from: "  TrendingUp,",
        to: "",
      },
      {
        from: "  TrendingDown,",
        to: "",
      },
      {
        from: "import { Card, Button, Badge, Select } from './ui';",
        to: "import { Card, Button, Badge } from './ui';",
      },
    ],
  },

  // UserSetup.tsx - Fix quotes and unused import
  {
    file: "components/UserSetup.tsx",
    replacements: [
      {
        from: "import { Shield, TrendingUp, Target, Activity, Clock, AlertTriangle, Rocket, CheckCircle } from 'lucide-react';",
        to: "import { Shield, TrendingUp, Target, Activity, Clock, AlertTriangle, CheckCircle } from 'lucide-react';",
      },
      {
        from: "I'm a ",
        to: "I&apos;m a ",
      },
      {
        from: "I've been trading for ",
        to: "I&apos;ve been trading for ",
      },
      {
        from: "I'd like to ",
        to: "I&apos;d like to ",
      },
    ],
  },

  // UserSetupAI.tsx - Fix quotes and require statement
  {
    file: "components/UserSetupAI.tsx",
    replacements: [
      {
        from: "const user = getCurrentUser();",
        to: "const _user = getCurrentUser();",
      },
      {
        from: "I'm ",
        to: "I&apos;m ",
      },
      {
        from: "I'm looking",
        to: "I&apos;m looking",
      },
      {
        from: "const UserSetup = require('./UserSetup').default;",
        to: "import UserSetup from './UserSetup';",
      },
    ],
  },

  // PLComparisonChart.tsx - Fix unused imports
  {
    file: "components/trading/PLComparisonChart.tsx",
    replacements: [
      {
        from: "  ISeriesApi,",
        to: "",
      },
      {
        from: "function formatTooltipValue(value: number, position: any): string {",
        to: "function formatTooltipValue(value: number, _position: any): string {",
      },
      {
        from: "function formatComparisonTooltip(value: number, comparison: any): string {",
        to: "function formatComparisonTooltip(value: number, _comparison: any): string {",
      },
    ],
  },
];

// Apply fixes
fixes.forEach(({ file, replacements }) => {
  const filePath = path.join(__dirname, file);

  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  Skipping ${file} - file not found`);
    return;
  }

  let content = fs.readFileSync(filePath, "utf8");
  let changed = false;

  replacements.forEach(({ from, to }) => {
    if (content.includes(from)) {
      content = content.replace(from, to);
      changed = true;
    }
  });

  if (changed) {
    fs.writeFileSync(filePath, content, "utf8");
    console.log(`✓ Fixed ${file}`);
  } else {
    console.log(`- No changes needed for ${file}`);
  }
});

console.log("\n✓ All fixes applied!");
