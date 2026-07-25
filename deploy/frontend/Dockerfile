# LUMI Frontend — multi-stage Dockerfile
# Node 20 build + nginx serve

FROM node:20-slim AS builder

WORKDIR /build

COPY react-frontend/package.json react-frontend/package-lock.json ./
RUN npm ci

COPY react-frontend/ ./
RUN npm run build

# ---------- runtime stage ----------
FROM nginx:alpine

COPY --from=builder /build/dist /usr/share/nginx/html
COPY deploy/nginx/frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
