FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=development

# Install build dependencies
RUN apk add --no-cache python3 make g++

# Remove old lock file if it exists and install fresh
RUN rm -f package-lock.json

COPY package.json ./
RUN npm install --legacy-peer-deps

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
