/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Output standalone for Docker deployments
  output: "standalone",

  // Skip type checking for deployment
  typescript: {
    ignoreBuildErrors: true,
  },

  // Skip ESLint during builds (run separately with npm run lint)
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Enable SWC minification (faster than Terser)
  swcMinify: true,

  // Optimize bundle size
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn']
    } : false,
  },

  // Production optimizations
  productionBrowserSourceMaps: false,

  // Image optimization configuration (Phase 2: Performance)
  images: {
    domains: ["cdn.jsdelivr.net", "s3.tradingview.com", "cdnjs.cloudflare.com", "localhost"],
    formats: ["image/avif", "image/webp"], // Modern formats for better compression
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60, // Cache images for at least 60 seconds
  },

  // Webpack optimizations
  webpack: (config, { isServer, webpack }) => {
    // Tree shaking for moment.js locale files (if used)
    config.plugins.push(
      new webpack.ContextReplacementPlugin(/moment[/\\]locale$/, /en/)
    );

    // Analyze bundle in production builds
    if (!isServer && process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          reportFilename: './analyze.html',
          openAnalyzer: true,
        })
      );
    }

    // Optimize chunks
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          // Vendor chunk
          vendor: {
            name: 'vendor',
            chunks: 'all',
            test: /node_modules/,
            priority: 20
          },
          // D3.js separate chunk (large library)
          d3: {
            name: 'd3',
            test: /[\\/]node_modules[\\/]d3/,
            priority: 30
          },
          // Chart libraries separate chunk
          charts: {
            name: 'charts',
            test: /[\\/]node_modules[\\/](chart\.js|react-chartjs-2|recharts|lightweight-charts)/,
            priority: 30
          },
          // Anthropic SDK separate chunk
          anthropic: {
            name: 'anthropic',
            test: /[\\/]node_modules[\\/]@anthropic-ai/,
            priority: 30
          },
          // Common components
          common: {
            name: 'common',
            minChunks: 2,
            priority: 10,
            reuseExistingChunk: true,
            enforce: true
          }
        }
      };
    }

    return config;
  },

  // Experimental features
  experimental: {
    // optimizeCss: true, // Requires critters package - disabled for now
    optimizePackageImports: ['d3', '@anthropic-ai/sdk', 'lodash', 'date-fns']
  },

  async headers() {
    // Environment-aware Content Security Policy
    const isDev = process.env.NODE_ENV === "development";
    const devSources = isDev ? "http://localhost:8001" : "";

    // Production uses stricter CSP than development
    const ContentSecurityPolicy = `
      default-src 'self';
      script-src 'self' ${isDev ? "'unsafe-eval'" : ""} 'unsafe-inline' https://cdn.jsdelivr.net https://s3.tradingview.com https://cdnjs.cloudflare.com;
      style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://s3.tradingview.com;
      connect-src 'self' ${devSources} https://api.anthropic.com https://paiid-backend.onrender.com wss://paiid-backend.onrender.com https://s.tradingview.com;
      img-src 'self' data: blob: https: https://s3.tradingview.com;
      font-src 'self' data: https://s3.tradingview.com;
      object-src 'none';
      frame-src 'self' https://s.tradingview.com;
      base-uri 'self';
      form-action 'self';
      upgrade-insecure-requests;
    `
      .replace(/\s+/g, " ")
      .trim();

    return [
      {
        source: "/(.*)",
        headers: [
          // Prevent MIME-type sniffing
          { key: "X-Content-Type-Options", value: "nosniff" },
          // Control referrer information
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          // Prevent clickjacking
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          // XSS Protection (legacy, but doesn't hurt)
          { key: "X-XSS-Protection", value: "1; mode=block" },
          // Permissions Policy (restrict features)
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=(), interest-cohort=()",
          },
          // Content Security Policy
          { key: "Content-Security-Policy", value: ContentSecurityPolicy },
        ],
      },
    ];
  },
};
module.exports = nextConfig;
