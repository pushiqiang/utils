
## 使用Nginx代理s3，动态生成缩略图并缓存

通过 {domain}/{uri}?s={size}实现获取指定大小缩略图

原图：`localhost/u/1523562/avatar`

缩略图：`localhost/u/1523562/avatar?s=200`

缩略图：`localhost/u/1523562/avatar?s=100`


## docker启动

docker-compose up -d --build


## 实现

### nginx.conf

```
# 加载image-filter模块, 顶级域，最前
load_module /etc/nginx/modules/ngx_http_image_filter_module.so;

...
...
...

include /etc/nginx/conf.d/*.conf;

```



### media.conf

/etc/nginx/conf.d/media.conf


```

server {
    listen 80;
    listen [::]:80;

    server_tokens off;
    server_name  localhost; # 你的域名

    location / {
        set $backend 'your.s3.bucket_name.s3.amazonaws.com';

        proxy_cache s3cache;
        proxy_cache_key "$host$uri$is_args$arg_s";   # 需要优化

        # cache successful responses for 24 hours
        proxy_cache_valid  200 302  24h;
        # cache missing responses for 1 minutes
        proxy_cache_valid  403 404 415 1m;

        proxy_redirect off;
        # need to set the hot to be $backend here so s3 static website hosting service knows what bucket to use
        proxy_set_header        Host $backend;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        add_header              X-Cache-Status $upstream_cache_status;
        proxy_hide_header       x-amz-id-2;
        proxy_hide_header       x-amz-request-id;
        proxy_hide_header       Set-Cookie;
        proxy_ignore_headers    "Set-Cookie";
        proxy_intercept_errors on;

        # 暂时使用 google dns, 如果用ec2的机器，可以用aws提供的dns，这样速度更快
        resolver 8.8.8.8;
        resolver_timeout 5s;

        # querystring带有合法的 s 参数的请求代理到缩略图服务器
        if ($arg_s ~* "^([0-9]+)$"){
            proxy_pass  http://127.0.0.1:10199;
        }

        proxy_pass http://$backend;
    }
}

```

### thumbnail.conf

/etc/nginx/conf.d/thumbnail.conf

```

server {
    listen 10199;

    server_tokens off;
    server_name  127.0.0.1;

    image_filter_buffer 100M;   # 设置读取图像缓冲的最大大小，超过则415错误。

    location / {
        set $backend 'your.s3.bucket_name.s3.amazonaws.com';

        proxy_redirect off;
        # need to set the hot to be $backend here so s3 static website hosting service knows what bucket to use
        proxy_set_header        Host $backend;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        add_header              X-Cache-Status $upstream_cache_status;
        proxy_hide_header       x-amz-id-2;
        proxy_hide_header       x-amz-request-id;
        proxy_hide_header       Set-Cookie;
        proxy_ignore_headers    "Set-Cookie";
        proxy_intercept_errors on;

        # 暂时使用 google dns, 如果用ec2的机器，可以用aws提供的dns，这样速度更快
        resolver 8.8.8.8;
        resolver_timeout 5s;

        image_filter resize $arg_s $arg_s;

        proxy_pass http://$backend;

        allow 127.0.0.1;
        deny all;
    }
}

```
