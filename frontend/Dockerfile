# ============================================
# Frontend Dockerfile
# Vue 3 + Nginx
# ============================================

# Build stage
FROM node:20-alpine AS builder

# Build arguments for environment variables
ARG VITE_API_BASE_URL

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application with environment variable
RUN if [ -n "$VITE_API_BASE_URL" ]; then \
      echo "VITE_API_BASE_URL is set to: $VITE_API_BASE_URL"; \
    else \
      echo "VITE_API_BASE_URL is empty, using relative paths"; \
    fi
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
