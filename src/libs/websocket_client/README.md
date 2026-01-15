## 运行方式 ：
nohup python3 websocket_service.py > websocket.log 2>&1 &

## redis需要安装

## 独立部署websocket服务
- 因flask为多进程模式，所以为保证不重复连接而将websocket服务单独部署,如需要与程序分离时，则将redis_client.py应用于程序中即可，保持与此模块消息通道 一致
- 
## 独立部署方式 
方法1：使用systemd（生产环境推荐）​​
这是最规范的守护进程管理方式，支持开机自启和自动重启。

1. 创建systemd服务文件
sudo vim /etc/systemd/system/websocket.service
内容如下（根据实际路径修改）：
```
[Unit]
Description=WebSocket Service
After=network.target

[Service]
User=your_username  # 改为实际用户
Group=your_group
WorkingDirectory=/path/to/your/project  # 项目根目录
ExecStart=/usr/bin/python3 /path/to/websocket_service.py
Restart=always  # 崩溃自动重启
RestartSec=5s
Environment="PYTHONPATH=/path/to/your/project"  # 如有需要

[Install]
WantedBy=multi-user.target
```

1. 启用并启动服务
```
sudo systemctl daemon-reload
sudo systemctl start websocket
sudo systemctl enable websocket  # 开机自启
```
1. 查看状态和日志
```
sudo systemctl status websocket
journalctl -u websocket -f  # 实时日志
```

## 使用nohup + 重定向（快速测试）
适合临时运行，但不如systemd稳定。
```
cd /path/to/your/project
nohup python3 websocket_service.py > websocket.log 2>&1 &
nohup /www/server/pyporject_evn/cx_travel_venv/bin/python3 websocket_service.py > 2>&1 &
```

websocket.log 重定向标准输出到日志文件
2>&1 将错误输出合并到标准输出
& 后台运行
nohup 防止终端退出时进程被终止

查看运行状态 ：
```
ps aux | grep websocket
tail -f websocket.log  # 查看实时日志
```