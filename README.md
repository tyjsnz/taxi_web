# Web端项目文档
## 项目介绍
- 本项目为出租车预约系统，包括乘客端、司机端、管理员端三部分
- 乘客端：乘客可以在小程序中预约出租车，查看订单状态，取消订单等
- 司机端：司机可以在小程序中登录，查看订单状态，接受订单，完成订单等
- 管理员端：管理员可以在网页中登录，管理乘客、司机、订单等
- 管理后台系统：https://github.com/tyjsnz/taxi_web.git
- 微信小程序乘客端：https://github.com/tyjsnz/taxi_wxmini.git

## 项目数据库
- 目录下：database/ls_taxt.sql

## websocket消息服务器
- 使用了独立的消息服务，采用node来实现，参见项目同级目录的node_websocket项目，要node独立启动

## websocket消息客户端
- src/libs/websocket_service.py为项目redis消息订阅服务，需要至路径下进行独立启动,项目中的消息推送到redis中，websocket_service.py为消息订阅服务，将redis中的消息推送给node_websocket的websocket服务器，通过服务端来转发给乘客及司机客户端，项目启动时需要启动
```
python3 websocket_service.py
```
如在本地测试，则要更改websocket_service.py中的socket服务地址为ws://127.0.0.1:8080?client_id=11flask_backend&token=your_secret_token，如在服务端则使用127.0.0.1:8080?client_id=11flask_backend&token=your_secret_token即可
  
## websocket消息订阅服务
- src/common/websocket_manager.py为项目消息推送服务，封装使用redis来完成消息推送
- driver_find_libs.py为定时任务服务，封装使用apscheduler完成定时任务，因任务为多进程，所以需要在其中使用redis来完成消息推送

## 自动任务
- 1、定时任务,到以下目录运行独立任务：
  - service/ScheduleService.py


# Android项目文档
- 听单语音采用了讯飞语音合成

# websocket消息服务器
- 使用了独立的消息服务，采用node来实现，参见项目同级目录的node_websocket项目，要node独立启动
- 1、运行websocket服务器
```
nohup node server.js > app.log 2>&1 &
```
- 2、运行websocket客户端
```
cd /www/wwwroot/web/src/libs/websocket_client/
./run.sh
```
- 3、启动自动服务
```
cd /www/wwwroot/web/src/service/
./run.sh
```

# 小程序端websocket连接方式为wss，注意ws不能连接
```
wss://ws.flacn.net/ws/ 必须以此开头
wss://ws.flacn.net/ws/?client_id=11flask_backend&token=your_secret_token
```

### nginx中需要配置反向代理
```
server
{
    listen 80;
    listen 443 ssl http2 ;
    server_name wxapp.flacn.net;
    index index.html index.htm default.htm default.html;
    root /www/wwwroot/web;

    #SSL-START SSL相关配置
    #error_page 404/404.html;
    ssl_certificate    /www/server/panel/vhost/cert/web/fullchain.pem;
    ssl_certificate_key    /www/server/panel/vhost/cert/web/privkey.pem;
    ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    add_header Strict-Transport-Security "max-age=31536000";
    error_page 497  https://$host$request_uri;

    
    #SSL-END

    #ERROR-PAGE-START  错误页相关配置
    #error_page 404 /404.html;
    #error_page 502 /502.html;
    #ERROR-PAGE-END


    #REWRITE-START 伪静态相关配置
    include /www/server/panel/vhost/rewrite/python_web.conf;
    #REWRITE-END

    #禁止访问的文件或目录
    location ~ ^/(\.user.ini|\.htaccess|\.git|\.svn|\.project|LICENSE|README.md|package.json|package-lock.json|\.env) {
        return 404;
    }

    #一键申请SSL证书验证目录相关设置
    location /.well-known/ {
        root /www/wwwroot/java_node_ssl;
    }

    #禁止在证书验证目录放入敏感文件
    if ( $uri ~ "^/\.well-known/.*\.(php|jsp|py|js|css|lua|ts|go|zip|tar\.gz|rar|7z|sql|bak)$" ) {
        return 403;
    }

    # HTTP反向代理相关配置开始 >>>
    location ~ /purge(/.*) {
        proxy_cache_purge cache_one 127.0.0.1$request_uri$is_args$args;
    }

    location /ws/ {
        # 反向代理到后端WS服务
        proxy_pass http://127.0.0.1:8088;
        
        # WebSocket协议升级关键配置
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;  # 建议修改此项[6,7](@ref)
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 长连接超时设置（防止断开）[4](@ref)
        proxy_connect_timeout 60s;
        proxy_read_timeout 86400s;  # 保持长连接
        proxy_send_timeout 86400s;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host 127.0.0.1:$server_port;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header REMOTE-HOST $remote_addr;
        add_header X-Cache $upstream_cache_status;
        proxy_set_header X-Host $host:$server_port;
        proxy_set_header X-Scheme $scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 86400s;
        proxy_send_timeout 30s;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    
    # HTTP反向代理相关配置结束 <<<

    access_log  /www/wwwlogs/web.log;
    error_log  /www/wwwlogs/web.error.log;
}
```