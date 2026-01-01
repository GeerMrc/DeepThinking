# DeepThinking-MCP SSE 配置指南

> 版本: 0.1.0
> 更新日期: 2026-01-01
> 适用场景: 远程部署、Web应用集成、多客户端访问

---

## 概述

SSE（Server-Sent Events）是 DeepThinking-MCP 的远程传输模式，适用于需要通过网络访问的场景。

### SSE vs STDIO

| 特性 | SSE 模式 | STDIO 模式 |
|------|----------|------------|
| **适用场景** | 远程服务器、Web应用 | 本地开发、Claude Desktop |
| **通信方式** | HTTP Server-Sent Events | 标准输入/输出 |
| **网络访问** | 支持远程访问 | 仅本地进程 |
| **认证** | 支持 Bearer Token / API Key | 无需认证 |
| **部署方式** | 独立服务器 | 子进程 |

---

## 快速开始

### 1. 启动 SSE 服务器

**无认证（仅用于开发测试）**：
```bash
python -m deep_thinking --transport sse --host 0.0.0.0 --port 8088
```

**使用 Bearer Token 认证（推荐）**：
```bash
python -m deep_thinking \
  --transport sse \
  --host 0.0.0.0 \
  --port 8088 \
  --auth-token "your-secret-token-here"
```

**使用 API Key 认证（推荐）**：
```bash
python -m deep_thinking \
  --transport sse \
  --host 0.0.0.0 \
  --port 8088 \
  --api-key "your-api-key-here"
```

### 2. 验证服务运行

```bash
# 健康检查
curl http://localhost:8088/health

# 预期输出：OK
```

### 3. 访问 SSE 端点

```bash
# 无认证
curl -X POST http://localhost:8088/sse \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'

# Bearer Token 认证
curl -X POST http://localhost:8088/sse \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'

# API Key 认证
curl -X POST http://localhost:8088/sse \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

---

## 认证机制详解

### Bearer Token 认证

**原理**: 使用 HTTP `Authorization: Bearer <token>` 头部传递认证令牌。

**配置方式**：
```bash
# 方式1: CLI 参数
python -m deep_thinking --transport sse --auth-token "my-token"

# 方式2: 环境变量
export DEEP_THINKING_AUTH_TOKEN="my-token"
python -m deep_thinking --transport sse
```

**客户端请求示例**：
```bash
curl -X POST http://localhost:8088/sse \
  -H "Authorization: Bearer my-token" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize"}'
```

**JavaScript 示例**：
```javascript
const response = await fetch('http://localhost:8088/sse', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer my-token',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize'
  })
});
```

### API Key 认证

**原理**: 使用自定义 HTTP 头部 `X-API-Key: <key>` 传递 API 密钥。

**配置方式**：
```bash
# 方式1: CLI 参数
python -m deep_thinking --transport sse --api-key "my-api-key"

# 方式2: 环境变量
export DEEP_THINKING_API_KEY="my-api-key"
python -m deep_thinking --transport sse
```

**客户端请求示例**：
```bash
curl -X POST http://localhost:8088/sse \
  -H "X-API-Key: my-api-key" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize"}'
```

**JavaScript 示例**：
```javascript
const response = await fetch('http://localhost:8088/sse', {
  method: 'POST',
  headers: {
    'X-API-Key': 'my-api-key',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize'
  })
});
```

### 双重认证（同时启用）

可以同时配置 Bearer Token 和 API Key，两种方式任一有效：

```bash
python -m deep_thinking \
  --transport sse \
  --auth-token "my-token" \
  --api-key "my-api-key"
```

---

## 环境变量配置

### 完整环境变量列表

```bash
# 传输配置
export DEEP_THINKING_TRANSPORT=sse
export DEEP_THINKING_HOST=0.0.0.0
export DEEP_THINKING_PORT=8088

# 认证配置（二选一或两者都配置）
export DEEP_THINKING_AUTH_TOKEN="your-secret-token"
export DEEP_THINKING_API_KEY="your-api-key"

# 思考配置
export DEEP_THINKING_MAX_THOUGHTS=50
export DEEP_THINKING_MIN_THOUGHTS=3
export DEEP_THINKING_THOUGHTS_INCREMENT=10

# 存储配置
export DEEP_THINKING_DATA_DIR="/var/lib/deep-thinking"

# 日志配置
export DEEP_THINKING_LOG_LEVEL=INFO
```

### 使用 .env 文件

**创建 `.env` 文件**：
```ini
DEEP_THINKING_TRANSPORT=sse
DEEP_THINKING_HOST=0.0.0.0
DEEP_THINKING_PORT=8088
DEEP_THINKING_AUTH_TOKEN=prod-token-xyz-123
DEEP_THINKING_API_KEY=prod-api-key-abc-456
DEEP_THINKING_LOG_LEVEL=INFO
```

**加载环境变量**：
```bash
# 使用 python-dotenv
pip install python-dotenv

# 启动时加载
python -m dotenv run python -m deep_thinking
```

---

## CLI 启动参数

### 完整参数列表

```bash
python -m deep_thinking --transport sse [OPTIONS]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--host` | string | localhost | 监听地址（0.0.0.0 允许远程访问） |
| `--port` | integer | 8000 | 监听端口 |
| `--auth-token` | string | 无 | Bearer Token 认证 |
| `--api-key` | string | 无 | API Key 认证 |
| `--data-dir` | string | .deep-thinking-mcp/ | 数据存储目录 |
| `--log-level` | string | INFO | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `--max-thoughts` | integer | 50 | 最大思考步骤数（1-10000） |
| `--min-thoughts` | integer | 3 | 最小思考步骤数（1-10000） |
| `--thoughts-increment` | integer | 10 | 思考步骤增量（1-100） |

### 常见启动场景

**开发环境（无认证）**：
```bash
python -m deep_thinking \
  --transport sse \
  --host localhost \
  --port 8088 \
  --log-level DEBUG
```

**生产环境（API Key 认证）**：
```bash
python -m deep_thinking \
  --transport sse \
  --host 0.0.0.0 \
  --port 8088 \
  --api-key "prod-api-key-secure" \
  --log-level INFO
```

**高负载环境（调整配置）**：
```bash
python -m deep_thinking \
  --transport sse \
  --host 0.0.0.0 \
  --port 8088 \
  --api-key "prod-api-key" \
  --max-thoughts 100 \
  --thoughts-increment 20 \
  --log-level WARNING
```

---

## 安全最佳实践

### 1. 认证密钥管理

**✅ 推荐做法**：
- 使用环境变量存储密钥
- 使用 `.env` 文件并添加到 `.gitignore`
- 定期轮换密钥
- 生产环境使用强密钥（至少32字符）

**❌ 避免做法**：
- 在代码中硬编码密钥
- 将密钥提交到版本控制
- 使用弱密钥（如 "123456", "password"）
- 在命令行中明文传递密钥（会被 shell 历史记录）

**生成安全密钥**：
```bash
# 使用 OpenSSL 生成随机密钥
openssl rand -base64 32

# 使用 Python 生成
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. 网络安全

**防火墙配置**：
```bash
# Linux (ufw)
sudo ufw allow 8088/tcp
sudo ufw reload

# Linux (firewalld)
sudo firewall-cmd --permanent --add-port=8088/tcp
sudo firewall-cmd --reload
```

**反向代理配置（Nginx）**：
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /sse {
        proxy_pass http://localhost:8088;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 传递认证头部
        proxy_set_header Authorization $http_authorization;
        proxy_set_header X-API-Key $http_x_api_key;
    }
}
```

### 3. 系统服务配置

**systemd 服务配置**：
```ini
[Unit]
Description=DeepThinking MCP Server (SSE)
After=network.target

[Service]
Type=simple
User=deep-thinking
Group=deep-thinking
WorkingDirectory=/opt/deep-thinking-mcp
Environment="DEEP_THINKING_TRANSPORT=sse"
Environment="DEEP_THINKING_HOST=0.0.0.0"
Environment="DEEP_THINKING_PORT=8088"
Environment="DEEP_THINKING_API_KEY=your-api-key"
Environment="DEEP_THINKING_DATA_DIR=/var/lib/deep-thinking"
Environment="DEEP_THINKING_LOG_LEVEL=INFO"
ExecStart=/usr/bin/python3 -m deep_thinking
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**启动服务**：
```bash
# 安装服务
sudo cp deep-thinking.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable deep-thinking
sudo systemctl start deep-thinking
sudo systemctl status deep-thinking
```

---

## 故障排除

### 问题1: 端口被占用

**错误信息**：
```
OSError: [Errno 48] Address already in use
```

**解决方案**：
```bash
# 查找占用进程
lsof -i :8088

# 终止进程或更换端口
python -m deep_thinking --transport sse --port 8089
```

### 问题2: 认证失败

**错误信息**：
```
HTTP 401: Missing Bearer token
HTTP 403: Invalid API Key
```

**解决方案**：
1. 确认服务器配置了认证（`--auth-token` 或 `--api-key`）
2. 确认客户端请求包含正确的认证头部
3. 检查密钥是否完全匹配（区分大小写）

```bash
# 调试：查看请求头
curl -v -X POST http://localhost:8088/sse \
  -H "Authorization: Bearer my-token" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1}'
```

### 问题3: 无法远程访问

**症状**：本地可以访问，远程无法访问

**解决方案**：
```bash
# 1. 确认监听地址为 0.0.0.0（而非 localhost）
python -m deep_thinking --transport sse --host 0.0.0.0

# 2. 检查防火墙
sudo ufw status
sudo ufw allow 8088/tcp

# 3. 检查云服务器安全组
# 确保入站规则允许 8088 端口
```

### 问题4: SSE 连接断开

**症状**：连接建立后很快断开

**可能原因**：
- 反向代理超时设置过短
- 网络不稳定
- 客户端未正确处理 SSE

**解决方案**：
```nginx
# Nginx 配置增加超时
location /sse {
    proxy_pass http://localhost:8088;
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
}
```

### 问题5: 日志级别设置无效

**解决方案**：
```bash
# 确认使用正确的值
python -m deep_thinking --log-level DEBUG  # 正确
python -m deep_thinking --log-level debug  # 错误（必须大写）

# 有效值：DEBUG, INFO, WARNING, ERROR
```

---

## 性能优化

### 1. 连接数调优

**修改系统限制**：
```bash
# 查看当前限制
ulimit -n

# 临时增加限制
ulimit -n 4096

# 永久增加限制
echo "* soft nofile 4096" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 4096" | sudo tee -a /etc/security/limits.conf
```

### 2. 数据存储优化

**使用更快的存储**：
```bash
# 内存文件系统（开发测试）
export DEEP_THINKING_DATA_DIR=/dev/shm/deep-thinking

# SSD 目录（生产环境）
export DEEP_THINKING_DATA_DIR=/mnt/ssd/deep-thinking
```

---

## 监控与日志

### 查看日志

**systemd 日志**：
```bash
# 实时查看
sudo journalctl -u deep-thinking -f

# 查看最近100行
sudo journalctl -u deep-thinking -n 100
```

**日志级别说明**：
| 级别 | 用途 | 适用场景 |
|------|------|----------|
| DEBUG | 开发调试 | 开发环境、问题排查 |
| INFO | 正常运行 | 生产环境默认 |
| WARNING | 警告信息 | 关注潜在问题 |
| ERROR | 错误信息 | 生产环境、错误追踪 |

---

## 相关资源

- [API 文档](./api.md) - 完整的 MCP 工具 API 参考
- [安装指南](./installation.md) - 安装步骤和配置
- [架构设计](../ARCHITECTURE.md) - 系统架构和技术设计
- [IDE 配置](./ide-config.md) - 各种 IDE 的配置示例

---

## 许可证

MIT License
