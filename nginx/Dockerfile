FROM nginx:1.24.0

# Nginx 설정 파일 복사
COPY nginx/nginx.conf /etc/nginx/nginx.conf

COPY --from=build /app/build /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;", "-c", "/etc/nginx/nginx.conf"]

