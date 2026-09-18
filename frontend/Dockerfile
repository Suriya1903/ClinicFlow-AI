# Stage 1: Build the React application
FROM node:24-alpine AS builder

WORKDIR /app

# Copy package files first for better Docker layer caching
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source code
COPY frontend/ ./

# Build the production application
RUN npm run build


# Stage 2: Serve the application using Nginx
FROM nginx:alpine

# Remove the default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy the React production build
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy Nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]