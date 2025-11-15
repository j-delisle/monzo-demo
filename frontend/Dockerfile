FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN npm run build

EXPOSE 3000

# Use a simple HTTP server to serve the built files
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]