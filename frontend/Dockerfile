# Frontend Dockerfile for PaiiD Trading App

# Stage 1: Build stage
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including devDependencies needed for build)
RUN npm ci

# Copy application code
COPY . .

# Accept build arguments for API tokens (needed for Next.js build)
ARG NEXT_PUBLIC_API_TOKEN
ARG NEXT_PUBLIC_BACKEND_API_BASE_URL
ARG NEXT_PUBLIC_ANTHROPIC_API_KEY

# Set as environment variables for build process
ENV NEXT_PUBLIC_API_TOKEN=$NEXT_PUBLIC_API_TOKEN
ENV NEXT_PUBLIC_BACKEND_API_BASE_URL=$NEXT_PUBLIC_BACKEND_API_BASE_URL
ENV NEXT_PUBLIC_ANTHROPIC_API_KEY=$NEXT_PUBLIC_ANTHROPIC_API_KEY

# Build Next.js for production
RUN npm run build

# Stage 2: Production stage
FROM node:20-alpine AS runner

# Set working directory
WORKDIR /app

# Set NODE_ENV to production
ENV NODE_ENV=production

# Create a non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copy standalone server from builder
# Next.js standalone build structure:
#   - /app/.next/standalone/* -> ./ (contains server.js and runtime)
#   - /app/.next/static -> ./.next/static (static assets NOT in standalone)
#   - /app/public -> ./public (public assets)
# This creates runtime structure: /app/server.js, /app/.next/static/*, /app/public/*
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Accept runtime arguments for API proxy (server-side API routes need these)
ARG API_TOKEN
ARG NEXT_PUBLIC_API_TOKEN
ARG NEXT_PUBLIC_BACKEND_API_BASE_URL
ARG NEXT_PUBLIC_ANTHROPIC_API_KEY

# Set runtime environment variables
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV API_TOKEN=$API_TOKEN
ENV NEXT_PUBLIC_API_TOKEN=$NEXT_PUBLIC_API_TOKEN
ENV NEXT_PUBLIC_BACKEND_API_BASE_URL=$NEXT_PUBLIC_BACKEND_API_BASE_URL
ENV NEXT_PUBLIC_ANTHROPIC_API_KEY=$NEXT_PUBLIC_ANTHROPIC_API_KEY

# Health check - check root path
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Run the standalone server
CMD ["node", "server.js"]
