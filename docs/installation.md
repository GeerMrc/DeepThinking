# DeepThinking-MCP 安装与配置指南

> 版本: 0.1.0
> 更新日期: 2025-12-31

---

## 系统要求

### 最低要求

| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 10+, macOS 10.15+, Linux |
| **Python** | 3.10 或更高版本 |
| **内存** | 512 MB 可用内存 |
| **磁盘空间** | 50 MB 可用空间 |

### 推荐配置

| 组件 | 推荐 |
|------|------|
| **Python** | 3.11 或更高 |
| **内存** | 1 GB 或更多 |
| **磁盘空间** | 100 MB 或更多 |

---

## 安装方法

> ⚠️ **重要提示**: deep-thinking-mcp **目前未发布到 PyPI**。
>
> 以下方法1和方法2仅在未来包发布到PyPI后可用。
>
> **当前请使用方法3（开发模式安装）**。

---

### 方法1: 使用 pip 安装

> ⚠️ **待包发布到PyPI后可用**

```bash
pip install deep-thinking-mcp
```

#### 升级到最新版本

```bash
pip install --upgrade deep-thinking-mcp
```

#### 卸载

```bash
pip uninstall deep-thinking-mcp
```

---

### 方法2: 使用 uv 安装（推荐）⚡

> ⚠️ **待包发布到PyPI后可用**

[uv](https://github.com/astral-sh/uv) 是一个极速的 Python 包管理器，比 pip 快 10-100 倍。

#### 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip 安装
pip install uv
```

#### 使用 uv 安装 DeepThinking-MCP

```bash
# 全局安装
uv pip install deep-thinking-mcp

# 或在项目中安装
uv pip install deep-thinking-mcp
```

#### 升级到最新版本

```bash
uv pip install --upgrade deep-thinking-mcp
```

#### 卸载

```bash
uv pip uninstall deep-thinking-mcp
```

**为什么选择 uv？**
- 🚀 **极快速度**: 比 pip 快 10-100 倍
- 🔒 **更安全**: 内置依赖锁定和冲突解决
- 📦 **一体化**: 包管理、虚拟环境、脚本运行于一体
- 💡 **现代设计**: Rust 编写，兼容 pip 的所有功能

---

### 方法3: 开发模式安装 ⭐ （推荐，当前可用）

这是**当前唯一可用的安装方式**，直接从源代码安装。

#### 方式3A: 使用 uv（推荐）

```bash
# 进入项目目录
cd /path/to/Deep-Thinking-MCP

# 以开发模式安装
uv pip install -e .
```

#### 方式3B: 使用 pip

```bash
# 进入项目目录
cd /path/to/Deep-Thinking-MCP

# 以开发模式安装
pip install -e .
```

#### 方式3C: 使用虚拟环境（最佳实践）

```bash
# 1. 进入项目目录
cd /path/to/Deep-Thinking-MCP

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 4. 以开发模式安装
pip install -e .
```

**什么是开发模式（Editable）？**

- ✅ 代码修改立即生效，无需重新安装
- ✅ 指向源代码目录，而非复制文件
- ✅ 适合开发和测试
- ✅ 可以使用 `git pull` 更新代码

#### 验证安装

```bash
# 检查是否安装成功
python -c "import deep_thinking; print('✅ 安装成功')"

# 查看版本信息
python -m deep_thinking --help
```

---

### 重新安装（重装）

如果遇到问题需要重新安装：

#### 步骤1: 完全卸载

```bash
# 卸载包
uv pip uninstall deep-thinking-mcp
# 或
pip uninstall deep-thinking-mcp

# 清理Python缓存
find /path/to/Deep-Thinking-MCP -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# 清理构建文件
find /path/to/Deep-Thinking-MCP -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
```

#### 步骤2: 重新安装

```bash
# 重新以开发模式安装
uv pip install -e /path/to/Deep-Thinking-MCP

# 验证安装
python -m deep_thinking --help
```

---

### 从源码安装（仅阅读参考）

> ⚠️ 此节仅用于理解项目结构，实际安装请使用上面的"方法3"

#### 1. 克隆仓库

#### 1. 克隆仓库

```bash
git clone https://github.com/your-org/deep-thinking-mcp.git
cd deep-thinking-mcp
```

#### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install -e .
```

---

### 方法4: 使用 Poetry 安装（开发模式）

```bash
# 安装 Poetry
pip install poetry

# 克隆仓库
git clone https://github.com/your-org/deep-thinking-mcp.git
cd deep-thinking-mcp

# 安装依赖
poetry install
```

---

## 验证安装

安装完成后，运行以下命令验证：

```bash
python -m deep_thinking --help
```

预期输出：

```
DeepThinking-MCP 服务器

用法: python -m deep_thinking [OPTIONS]

选项:
  --mode TEXT       传输模式: stdio 或 sse (默认: stdio)
  --host TEXT       SSE 模式监听地址 (默认: 127.0.0.1)
  --port INTEGER    SSE 模式监听端口 (默认: 8088)
  --storage-dir TEXT 数据存储目录 (默认: ~/.deep-thinking/)
  --log-level TEXT  日志级别: DEBUG/INFO/WARNING/ERROR (默认: INFO)
  --help            显示帮助信息
```

---

## 配置 Claude Desktop

DeepThinking-MCP 需要与 Claude Desktop 配合使用。

### 1. 找到配置文件

配置文件位置：

| 操作系统 | 配置文件路径 |
|---------|-------------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%/Claude/claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

### 2. 编辑配置文件

在配置文件中添加 MCP 服务器配置：

#### STDIO 模式配置（推荐）

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": [
        "-m",
        "deep_thinking",
        "--mode",
        "stdio"
      ]
    }
  }
}
```

#### SSE 模式配置

首先启动 SSE 服务器：

```bash
python -m deep_thinking --mode sse --host 127.0.0.1 --port 8088
```

然后在配置文件中添加：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "url": "http://127.0.0.1:8088/sse",
      "transport": "sse"
    }
  }
}
```

### 3. 自定义存储目录

如果需要自定义数据存储目录：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": [
        "-m",
        "deep_thinking",
        "--transport",
        "stdio",
        "--data-dir",
        "/path/to/custom/storage"
      ]
    }
  }
}
```

### 4. 调整日志级别

开发时可以启用详细日志：

```json
{
  "mcpServers": {
    "deep-thinking": {
      "command": "python",
      "args": [
        "-m",
        "deep_thinking",
        "--transport",
        "stdio",
        "--log-level",
        "DEBUG"
      ]
    }
  }
}
```

---

## 环境变量配置

您也可以通过环境变量配置 DeepThinking-MCP：

| 环境变量 | 描述 | 默认值 |
|---------|------|-------|
| **传输配置** | | |
| `DEEP_THINKING_TRANSPORT` | 传输模式 (stdio/sse) | stdio |
| `DEEP_THINKING_HOST` | SSE 监听地址 | 127.0.0.1 |
| `DEEP_THINKING_PORT` | SSE 监听端口 | 8000 |
| **认证配置** | | |
| `DEEP_THINKING_AUTH_TOKEN` | Bearer Token（SSE 认证） | 无 |
| `DEEP_THINKING_API_KEY` | API Key（SSE 认证） | 无 |
| **存储配置** | | |
| `DEEP_THINKING_DATA_DIR` | 数据存储目录 | ./.deep-thinking-mcp/ |
| **思考配置** | | |
| `DEEP_THINKING_MAX_THOUGHTS` | 最大思考步骤数（推荐 50，支持 1-10000） | 50 |
| `DEEP_THINKING_MIN_THOUGHTS` | 最小思考步骤数（推荐 3，支持 1-10000） | 3 |
| `DEEP_THINKING_THOUGHTS_INCREMENT` | 思考步骤增量（needsMoreThoughts，支持 1-100） | 10 |
| **日志配置** | | |
| `DEEP_THINKING_LOG_LEVEL` | 日志级别 (DEBUG/INFO/WARNING/ERROR) | INFO |

### 设置环境变量

#### macOS/Linux

```bash
# 临时设置
export DEEP_THINKING_DATA_DIR="/path/to/storage"
export DEEP_THINKING_LOG_LEVEL="DEBUG"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export DEEP_THINKING_DATA_DIR="/path/to/storage"' >> ~/.bashrc
echo 'export DEEP_THINKING_LOG_LEVEL="DEBUG"' >> ~/.bashrc
```

#### Windows

```cmd
# 临时设置
set DEEP_THINKING_DATA_DIR=C:\path\to\storage
set DEEP_THINKING_LOG_LEVEL=DEBUG

# 永久设置（系统环境变量）
# 1. 打开"系统属性" -> "高级" -> "环境变量"
# 2. 添加新的用户变量或系统变量
```

---

## 数据存储

### 存储目录结构

**默认存储目录：项目本地** `./.deep-thinking-mcp/`

```
./.deep-thinking-mcp/
├── sessions/              # 会话数据
│   ├── .index.json       # 会话索引文件
│   └── *.json            # 各会话文件
├── .backups/             # 自动备份目录
└── .gitignore            # 防止数据提交到版本控制
```

**旧版本存储目录（向后兼容）**: `~/.deep-thinking-mcp/`

### 存储路径优先级

1. **环境变量** `DEEP_THINKING_DATA_DIR`
2. **CLI参数** `--data-dir`
3. **默认值** 项目本地目录 `.deep-thinking-mcp/`

### 数据迁移

从旧版本（`~/.deep-thinking-mcp/`）升级时，系统会自动：
- 检测旧数据目录
- 创建自动备份
- 迁移数据到新位置
- 创建迁移标记文件

详见 [MIGRATION.md](./MIGRATION.md)。

### 数据备份

自动备份在每次修改前创建。

手动备份：

```bash
# 备份整个数据目录
cp -r .deep-thinking-mcp .deep-thinking-mcp.backup.$(date +%Y%m%d)

# 只备份会话数据
cp -r .deep-thinking-mcp/sessions .deep-thinking-mcp/sessions.backup.$(date +%Y%m%d)
```

### 数据恢复

从备份恢复：

```bash
# 恢复整个数据目录
rm -rf .deep-thinking-mcp
cp -r .deep-thinking-mcp.backup.20251231 .deep-thinking-mcp

# 从备份目录恢复
cp -r ~/.deep-thinking-mcp/backups/migration_backup_*/* .deep-thinking-mcp/sessions/
```

---

## 运行模式

### STDIO 模式

适用于 Claude Desktop 和本地应用。

**启动命令**：

```bash
python -m deep_thinking --mode stdio
```

**特点**：
- 通过标准输入/输出通信
- 由 Claude Desktop 自动启动
- 无需手动启动服务

---

### SSE 模式

适用于 Web 应用和远程访问。

**启动命令**：

```bash
python -m deep_thinking --mode sse --host 0.0.0.0 --port 8088
```

**访问地址**：

- SSE 端点：`http://localhost:8088/sse`
- 健康检查：`http://localhost:8088/health`

**特点**：
- 通过 HTTP Server-Sent Events 通信
- 需要手动启动服务
- 支持远程访问

**使用 systemd 管理（Linux）**：

创建服务文件 `/etc/systemd/system/deep-thinking.service`：

```ini
[Unit]
Description=DeepThinking MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/deep-thinking-mcp
ExecStart=/usr/bin/python3 -m deep_thinking --mode sse --host 0.0.0.0 --port 8088
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable deep-thinking
sudo systemctl start deep-thinking
sudo systemctl status deep-thinking
```

---

## 防火墙配置

### SSE 模式端口开放

如果需要远程访问 SSE 服务器，需要开放防火墙端口。

#### macOS

```bash
# 允许传入连接到端口 8088
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/bin/python3
```

#### Linux (ufw)

```bash
sudo ufw allow 8088/tcp
sudo ufw reload
```

#### Linux (firewalld)

```bash
sudo firewall-cmd --permanent --add-port=8088/tcp
sudo firewall-cmd --reload
```

#### Windows

1. 打开"Windows Defender 防火墙" -> "高级设置"
2. 创建入站规则，允许端口 8088

---

## 故障排除

### 问题1: 导入错误

**错误信息**：`ModuleNotFoundError: No module named 'deep_thinking'`

**解决方案**：

1. 确认安装成功：`pip list | grep deep-thinking`
2. 重新安装：`pip install --force-reinstall deep-thinking-mcp`
3. 检查 Python 路径：`which python` 和 `pip --version` 是否匹配

---

### 问题2: 权限错误

**错误信息**：`PermissionError: [Errno 13] Permission denied`

**解决方案**：

1. 检查存储目录权限：`ls -la ~/.deep-thinking/`
2. 修改权限：`chmod 755 ~/.deep-thinking/`
3. 使用 `--storage-dir` 指定有权限的目录

---

### 问题3: 端口被占用

**错误信息**：`Address already in use`

**解决方案**：

1. 查找占用进程：`lsof -i :8088`（macOS/Linux）或 `netstat -ano | findstr 8088`（Windows）
2. 终止进程或更换端口：`--port 8089`

---

### 问题4: Claude Desktop 无法连接

**解决方案**：

1. 确认配置文件路径正确
2. 确认配置文件 JSON 格式正确
3. 重启 Claude Desktop
4. 检查 Claude Desktop 日志：`~/Library/Logs/Claude/`（macOS）

---

### 问题5: SSE 模式无法访问

**解决方案**：

1. 确认服务已启动：`curl http://localhost:8088/health`
2. 检查防火墙设置
3. 确认监听地址：`--host 0.0.0.0` 允许远程访问

---

## 升级指南

### 从旧版本升级

```bash
# 备份数据
cp -r ~/.deep-thinking ~/.deep-thinking.backup

# 升级包
pip install --upgrade deep-thinking-mcp

# 验证升级
python -m deep_thinking --help
```

### 数据迁移

数据格式向前兼容，旧版本数据可以直接使用。

如有问题，从备份恢复：

```bash
rm -rf ~/.deep-thinking
cp -r ~/.deep-thinking.backup ~/.deep-thinking
```

---

## 卸载

### 完全卸载

```bash
# 1. 卸载 Python 包
pip uninstall deep-thinking-mcp

# 2. 删除数据目录（可选）
rm -rf ~/.deep-thinking

# 3. 删除 Claude Desktop 配置（可选）
# 编辑 claude_desktop_config.json，删除 deep-thinking 服务器配置
```

---

## 开发环境设置

### 使用虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_tools/test_sequential_thinking.py

# 查看测试覆盖率
pytest --cov=deep_thinking --cov-report=html
```

### 代码检查

```bash
# 代码格式检查
ruff check .

# 自动修复
ruff check --fix .

# 类型检查
mypy src/deep_thinking
```

---

## 相关资源

### 安装与配置
- [PyPI 发布指南](./PUBLISHING.md) - 如何发布到PyPI
- [API 文档](./api.md)
- [用户指南](./user_guide.md)

### 开发文档
- [架构设计文档](../ARCHITECTURE.md)
- [开发指南](./DEVELOPMENT.md)
- [贡献指南](../CONTRIBUTING.md)

### 支持
- [GitHub Issues](https://github.com/your-org/deep-thinking-mcp/issues)
- [更新日志](../CHANGELOG.md)

---

## 许可证

MIT License
