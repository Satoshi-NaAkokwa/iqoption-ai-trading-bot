# Multi-stage Dockerfile for Solana Marketing Suite
# Optimized for production deployment

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Stage 2: Production
FROM node:18-alpine

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache \
    tini \
    curl

# Create non-root user
RUN addgroup -g 1001 -S solana && \
    adduser -S -D -H -u 1001 -s /sbin/nologin -G solana -g solana solana

# Copy node modules from builder
COPY --from=builder --chown=solana:solana /app/node_modules ./node_modules

# Copy application files
COPY --chown=solana:solana . .

# Create necessary directories
RUN mkdir -p logs data cache config && \
    chown -R solana:solana logs data cache config

# Set environment variables
ENV NODE_ENV=production \
    LOG_LEVEL=info \
    LOG_FORMAT=json

# Switch to non-root user
USER solana

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose port for analytics dashboard
EXPOSE 3000

# Use tini as PID 1 for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Default command (can be overridden)
CMD ["node", "scripts/agent-analytics.js", "server", "--port", "3000"]