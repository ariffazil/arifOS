# Static site served by nginx
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Create nginx config directly - no variable substitution needed
# Railway sets PORT env var, we'll use 8080 as default
RUN printf 'server {\n\
    listen 8080;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    location /health {\n\
        access_log off;\n\
        return 200 "healthy\n";\n\
        add_header Content-Type text/plain;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

# Copy all portfolio files to nginx html directory
COPY . /usr/share/nginx/html

# Ensure index.html exists and is readable
RUN chmod 644 /usr/share/nginx/html/index.html && \
    ls -la /usr/share/nginx/html/

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
