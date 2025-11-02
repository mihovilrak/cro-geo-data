# frontend/Dockerfile
FROM node:25.1.0-alpine3.21

WORKDIR /usr/src/app

# Copy package definition
COPY package.json package-lock.json* ./

# Install dependencies
RUN mkdir node_modules \
    && yarn config set cache-folder /tmp/yarn-cache \
    && yarn install --frozen-lockfile --remove-optional --link-duplicates \
    && yarn cache clean

# Copy the rest of the source code
COPY . .

# Expose port
EXPOSE 3000

# Start development server (for development)
# For production, use: RUN npm run build && npm install -g serve && serve -s build -l 3000
CMD ["npm", "start"]

