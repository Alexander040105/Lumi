# LUMI Nginx reverse proxy — serves frontend and proxies API
FROM nginx:alpine

COPY deploy/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Frontend dist will be mounted or copied at runtime
COPY react-frontend/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
