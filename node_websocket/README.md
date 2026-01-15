## node websocket服务端
- 用于处理app端和司机端的websocket连接，以及消息的转发。需要独立部署运行

### 初始化node
- npm init -y

### 安装依赖
- npm install http socket.io redis jsonwebtoken
  
### 启动服务
- 1、node app.js
- 2、使用npm脚本（推荐）启动
  - npm start