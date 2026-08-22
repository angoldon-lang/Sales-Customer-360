FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=development \
    CI=false

# Install build dependencies
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package.json package-lock.json* ./

# Clean install with legacy peer deps
RUN npm cache clean --force && \
    rm -rf node_modules package-lock.json && \
    npm install --legacy-peer-deps --no-save && \
    npm cache clean --force

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
