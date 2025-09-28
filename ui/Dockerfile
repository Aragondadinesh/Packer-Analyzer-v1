FROM node:20 AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --silent || npm install
COPY . .
RUN npm run build
FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx","-g","daemon off;"]
