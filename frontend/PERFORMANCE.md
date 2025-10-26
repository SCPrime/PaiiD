# Frontend Performance Optimization

## Bundle Size Reduction

### Wave 5 Optimizations Applied

The following optimizations have been implemented to reduce bundle size and improve page load performance:

#### 1. SWC Minification
- **Enabled**: `swcMinify: true` in `next.config.js`
- **Benefit**: Faster and more efficient minification compared to Terser
- **Impact**: Reduces JavaScript bundle size by removing whitespace, shortening variable names

#### 2. Console Log Removal (Production Only)
- **Configuration**: Removes all `console.log()` statements in production builds
- **Exception**: Keeps `console.error()` and `console.warn()` for debugging
- **Impact**: Reduces bundle size and improves runtime performance

#### 3. Code Splitting Strategy
Webpack configured with intelligent chunk splitting:

- **Vendor Bundle**: All `node_modules` code (priority: 20)
- **D3.js Bundle**: Separate chunk for D3 visualization library (priority: 30, ~200KB)
- **Charts Bundle**: Separate chunk for chart.js, recharts, lightweight-charts (priority: 30)
- **Anthropic SDK Bundle**: Separate chunk for AI features (priority: 30)
- **Common Bundle**: Shared code used in 2+ pages (priority: 10)

**Benefit**: Parallel loading of bundles, better caching, smaller initial load

#### 4. Tree Shaking
- **Optimized**: Unused code elimination enabled
- **Moment.js**: Locale files restricted to English only
- **Package Imports**: Optimized imports for d3, @anthropic-ai/sdk, lodash, date-fns

#### 5. Production Optimizations
- **Source Maps**: Disabled in production (`productionBrowserSourceMaps: false`)
- **CSS Optimization**: Experimental CSS optimization enabled
- **Image Formats**: AVIF and WebP support for better compression

### Bundle Analysis

#### Running Bundle Analyzer

```bash
# Generate bundle analysis report
npm run analyze

# Output: .next/analyze.html (opens automatically in browser)
```

The bundle analyzer provides:
- Interactive treemap of all chunks
- Size breakdown by module
- Identification of large dependencies
- Opportunities for optimization

#### Manual Bundle Inspection

```bash
# After build, check chunk sizes
npm run build
ls -lh .next/static/chunks/

# View detailed build output
npm run build 2>&1 | grep -E "(KB|MB)"
```

### Target Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Total Bundle Size | < 500KB | TBD | Measure after build |
| First Contentful Paint (FCP) | < 1.5s | TBD | Measure with Lighthouse |
| Time to Interactive (TTI) | < 3s | TBD | Measure with Lighthouse |
| Largest Contentful Paint (LCP) | < 2.5s | TBD | Measure with Lighthouse |

### Dynamic Import Candidates

The following components are candidates for lazy loading to reduce initial bundle size:

#### Heavy Components (>50KB)

**RadialMenu.tsx** - D3.js visualization
```typescript
import dynamic from 'next/dynamic';

const RadialMenu = dynamic(() => import('@/components/RadialMenu'), {
  ssr: false,
  loading: () => <div className="loading">Loading menu...</div>
});
```

**Analytics.tsx** - Chart libraries
```typescript
const Analytics = dynamic(() => import('@/components/Analytics'), {
  ssr: false,
  loading: () => <div>Loading analytics...</div>
});
```

**Backtesting.tsx** - Complex calculations
```typescript
const Backtesting = dynamic(() => import('@/components/Backtesting'), {
  ssr: false
});
```

#### Conditional Imports (Admin/Settings Features)

**Settings.tsx** - Load only when settings panel opened
```typescript
const Settings = dynamic(() => import('@/components/Settings'));

function Dashboard() {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <>
      <button onClick={() => setShowSettings(true)}>Settings</button>
      {showSettings && <Settings />}
    </>
  );
}
```

**StrategyBuilderAI.tsx** - Heavy AI features
```typescript
const StrategyBuilderAI = dynamic(() => import('@/components/StrategyBuilderAI'), {
  ssr: false,
  loading: () => <div>Loading strategy builder...</div>
});
```

#### Library-Specific Optimizations

**D3.js** - Import only needed modules
```typescript
// Instead of:
import * as d3 from 'd3';

// Use specific imports:
import { arc, pie, select } from 'd3';

// Or lazy load entire library:
const d3 = await import('d3');
```

**Lodash** - Import individual functions
```typescript
// Instead of:
import _ from 'lodash';

// Use specific imports:
import debounce from 'lodash/debounce';
import throttle from 'lodash/throttle';
```

**Chart.js** - Register only needed components
```typescript
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);
```

### Optimization Checklist

- [x] Enable SWC minification
- [x] Configure code splitting (vendor, d3, charts, anthropic, common)
- [x] Remove console.logs in production
- [x] Disable production source maps
- [x] Add bundle analyzer
- [x] Optimize package imports (d3, lodash, date-fns, @anthropic-ai/sdk)
- [ ] Implement dynamic imports for heavy components
- [ ] Lazy load chart libraries
- [ ] Optimize D3.js imports (use specific modules)
- [ ] Optimize lodash imports (individual functions)
- [ ] Run Lighthouse audit for performance metrics
- [ ] Measure and document actual bundle sizes

### Future Optimizations (Post-Wave 5)

1. **Image Optimization**
   - Implement next/image for all images
   - Use AVIF/WebP formats
   - Lazy load images below fold

2. **Font Optimization**
   - Use next/font for optimal font loading
   - Subset fonts to required characters
   - Preload critical fonts

3. **API Response Caching**
   - Implement SWR with cache strategies
   - Use Redis for server-side caching
   - Add stale-while-revalidate headers

4. **Component Lazy Loading**
   - Implement all dynamic imports listed above
   - Use Intersection Observer for below-fold content
   - Lazy load modal/dialog components

5. **CDN Integration**
   - Move static assets to CDN
   - Use edge caching for API responses
   - Implement geolocation-based routing

### Performance Monitoring

#### Local Development
```bash
# Build and analyze
npm run analyze

# Build and check sizes
npm run build && ls -lh .next/static/chunks/
```

#### Lighthouse Audit
```bash
# Install Lighthouse
npm install -g lighthouse

# Run audit (after starting dev/prod server)
lighthouse http://localhost:3000 --view

# CI mode (JSON output)
lighthouse http://localhost:3000 --output json --output-path ./lighthouse-report.json
```

#### Bundle Size Tracking
```bash
# Add to CI/CD pipeline
npm run build
npx size-limit

# Or use bundlesize package
npx bundlesize
```

### Resources

- [Next.js Bundle Analyzer](https://www.npmjs.com/package/@next/bundle-analyzer)
- [Webpack Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)
- [Web Vitals](https://web.dev/vitals/)
- [Next.js Performance Docs](https://nextjs.org/docs/app/building-your-application/optimizing)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)

### Contact

For questions about performance optimizations, contact the frontend team or refer to the main project README.
