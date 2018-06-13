FROM nginx:1.10.1

COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf
COPY media.conf /etc/nginx/conf.d/media.conf
COPY thumbnail.conf /etc/nginx/conf.d/thumbnail.conf

COPY custom_404.html /usr/share/nginx/html/custom_404.html

WORKDIR /etc/nginx/
