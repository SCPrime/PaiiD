/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async headers() {
    // Environment-aware Content Security Policy
    const isDev = process.env.NODE_ENV === 'development';
    const devSources = isDev ? 'http://localhost:8001' : '';

    const ContentSecurityPolicy = `
      default-src 'self';
      script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net;
      style-src 'self' 'unsafe-inline';
      connect-src 'self' ${devSources} https://api.anthropic.com https://ai-trader-86a1.onrender.com wss://ai-trader-86a1.onrender.com;
      img-src 'self' data: blob: https:;
      font-src 'self' data:;
      object-src 'self' data:;
      frame-src 'self';
      base-uri 'self';
      form-action 'self';
    `.replace(/\s+/g, ' ').trim();

    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Content-Security-Policy", value: ContentSecurityPolicy }
        ]
      }
    ];
  }
};
module.exports = nextConfig;
