const WebSocket = require('ws');
const http = require('http');
const url = require('url');
const querystring = require('querystring');

// 存储客户端连接，client_id 为键，ws 和 token 为值
const clients = new Map();

// 创建 HTTP 服务器
const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('WebSocket Server is running');
});

// 创建 WebSocket 服务器
const wss = new WebSocket.Server({ 
    server,
    headers: {
      'Access-Control-Allow-Origin': '*' // 或具体域名
  }
});

// 设置心跳超时定时器
function startHeartbeatTimeout(clientId) {
  const client = clients.get(clientId);
  if (client) {
      // 清除之前的定时器
      if (client.heartbeat) clearTimeout(client.heartbeat);

      // 设置新的定时器，120秒后关闭连接
      client.heartbeat = setTimeout(() => {
          console.log(`Client ${clientId} heartbeat timeout, closing connection`);
          if (client.ws.readyState === WebSocket.OPEN) {
            client.ws.close(); // 关闭连接
          }
          clients.delete(clientId);
      }, 120000); // 120秒
  }
}

wss.on('connection', (ws, req) => {
    // 解析查询参数
    const parsedUrl = url.parse(req.url);
    const queryParams = querystring.parse(parsedUrl.query);
    
    const clientId = queryParams.client_id;
    const token = queryParams.token;
    
    if (!clientId || !token) {
        // ws.send('client_id is required or token is required');
        ws.close();
        return;
    }
    
    console.log(`检测到客户端连接, client_id: ${clientId}`);
    clients.set(clientId, { ws, token });
    console.log(`数量为：`,clients.size)

    //startHeartbeatTimeout(clientId);

    ws.on('message', (message) => {
        console.log(`Received message from ${clientId}: ${message}`);
        
        try {
            const data = JSON.parse(message);
            // 心跳包处理
            if (data.flag === 'ping') {
                ws.send('pong');
                //startHeartbeatTimeout(clientId); // 收到 ping 后重置心跳定时器
                return;
            }
            
            // 检查消息是否包含目标客户端token
            if (!data.target_token) {
              const client = clients.get(clientId);
              console.log(`data no target_token close ${clientId}`)
              //if (client && client.heartbeat) clearTimeout(client.heartbeat)
                clients.delete(clientId);
                ws.close();
            }
            if(data.target_token == 'all'){
                sendMessageToAllClient(data)
                return;
            }
            else if(data.target_token == 'driver'){
                sendMessageToAllDriverClient(data)
                return;
            }
            
            console.log(`data: ${JSON.stringify(data)}`)
            // 发送消息给目标客户端
            sendMessageToTargetClient(data.target_token, data);
            
        } catch (e) {
            console.error(`Error processing message: ${e}`);
        }
    });
    
    ws.on('close', () => {
        console.log(`Client ${clientId} disconnected`);
        clients.delete(clientId);
    });
    
    ws.on('error', (err) => {
        console.error(`WebSocket error for client ${clientId}: ${err}`);
        clients.delete(clientId);
    });
});

/**​
 * 发送消息给指定token的客户端
 * @param {string} targetToken 目标客户端token
 * @param {object} message 消息内容
 */
function sendMessageToTargetClient(targetToken, message) {
    console.log(`Sending message to client ${targetToken}:`, message);
    const messageStr = JSON.stringify(message);

    for (const [clientId, client] of clients.entries()) {
        if (client.token === targetToken) {
            try{
                client.ws.send(messageStr);
                console.log(`Sent message to ${clientId}: ${messageStr}`);
            }
            catch(e){
                console.error(`Error sending message to ${clientId}: ${e}`);
                clients.delete(clientId);
            }
        }
    }
}

/**​
 * 发送消息给所有客户端
 * @param {object} message 消息内容
 */
function sendMessageToAllClient(message) {
    const messageStr = JSON.stringify(message);
    
    for (const [clientId, client] of clients.entries()) {
        try {
            client.ws.send(messageStr);
            console.log(`Sent message to ${clientId}: ${messageStr}`);
        } catch (e) {
            console.error(`Error sending message to ${clientId}: ${e}`);
            clients.delete(clientId);
        }
    }
}
/**
 * 发给所有司机
 **/
function sendMessageToAllDriverClient(message){
    const messageStr = JSON.stringify(message);
    
    for (const [clientId, client] of clients.entries()) {
        console.log(clientId,clientId)
        if(clientId.indexOf('driver_') == -1){
            continue
        }
        try {
            client.ws.send(messageStr);
            console.log(`Sent message to ${clientId}: ${messageStr}`);
        } catch (e) {
            console.error(`Error sending message to ${clientId}: ${e}`);
            clients.delete(clientId);
        }
    }
}
/**​
 * 发送消息给指定客户端
 * @param {string} clientId 客户端ID
 * @param {object} message 消息内容
 */
function sendMessageToClient(clientId, message) {
    try {
        const messageStr = JSON.stringify(message);
        const client = clients.get(clientId);
        
        if (client && client.ws.readyState === WebSocket.OPEN) {
            client.ws.send(messageStr);
            console.log(`Sent message to ${clientId}: ${messageStr}`);
        }
    } catch (e) {
        console.error(`Error sending message to ${clientId}: ${e}`);
        clients.delete(clientId);
    }
}

/**​
 * 通知调度人员有订单无司机接单
 * @param {string} orderId 订单ID
 */
function sendMessageToDispatch(orderId) {
    // 实现逻辑
}

// 启动服务器
const PORT = process.env.PORT || 8088;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on port ${PORT}`);
});
