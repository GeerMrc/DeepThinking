# DeepThinking MCP 安装与配置指南

> 版本: 0.2.2
> 更新日期: 2026-01-08

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

> ⚠️ **重要提示**: Deep-Thinking-MCP 目前**未发布到 PyPI**。
>
> **可用安装方式**：
> - **开发模式**：从源码以可编辑模式安装（推荐用于开发测试）
> - **Wheel 文件**：从源码构建后安装（推荐用于生产环境）

### 开发模式安装 ⭐ （开发环境推荐）

直接从源代码以可编辑模式安装。

#### 使用虚拟环境（最佳实践）

```bash
# 1. 进入项目目录
cd Deep-Thinking-MCP

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

#### 使用 uv（更快）

```bash
# 安装 uv（如果未安装）
pip install uv

# 进入项目目录
cd Deep-Thinking-MCP

# 以开发模式安装
uv pip install -e .
```

**开发模式的优势**：
- ✅ 代码修改立即生效，无需重新安装
- ✅ 指向源代码目录，而非复制文件
- ✅ 适合开发和测试
- ✅ 可以使用 `git pull` 更新代码

---

### Wheel 文件安装（生产环境推荐）

从源码构建 Wheel 文件后安装。

#### 构建和安装

```bash
# 1. 进入项目目录
cd Deep-Thinking-MCP

# 2. 安装构建工具
pip install build

# 3. 构建 Wheel 文件
python -m build

# 4. 安装 Wheel 文件
pip install dist/deepthinking-*.whl
```

#### 使用 uv 构建（更快）

```bash
# 1. 进入项目目录
cd Deep-Thinking-MCP

# 2. 使用 uv 构建
uv build

# 3. 安装 Wheel 文件
uv pip install dist/deepthinking-*.whl
```

---

## 验证安装

### 检查安装

```bash
# 检查是否安装成功
python -c "import deep_thinking; print('✅ 安装成功')"

# 查看帮助信息
python -m deep_thinking --help
```

### 运行测试

```bash
# 运行测试套件
pytest

# 查看测试覆盖率
pytest --cov=deep_thinking --cov-report=html
```

---

## 快速配置

### 1. 创建配置文件

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
nano .env
```

### 2. 基础配置

```bash
# .env 文件内容
DEEP_THINKING_TRANSPORT=stdio
DEEP_THINKING_LOG_LEVEL=INFO
```

### 3. 启动服务器

```bash
# STDIO 模式（本地）
python -m deep_thinking

# SSE 模式（远程）
python -m deep_thinking --transport sse
```

详细的配置选项请参考：[配置参数参考](./configuration.md)

---

## IDE 集成配置

### Claude Desktop

配置示例：

```json
{
  "mcpServers": {
    "deepthinking": {
      "command": "python",
      "args": ["-m", "deep_thinking"],
      "env": {
        "DEEP_THINKING_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

详细的 IDE 配置请参考：[IDE 集成配置](./ide-config.md)

### Claude Code

```bash
# 添加 MCP 服务器
claude mcp add deepthinking stdio python -m deep_thinking
```

详细的 Claude Code 配置请参考：[Claude Code 配置指南](./claude-code-config.md)

---

## SSE 远程模式配置

适用于远程服务器部署场景。

### 基础配置

```bash
# .env 文件
DEEP_THINKING_TRANSPORT=sse
DEEP_THINKING_HOST=localhost
DEEP_THINKING_PORT=8000
```

### 认证配置（可选）

```bash
# Bearer Token 认证
DEEP_THINKING_AUTH_TOKEN=your-secret-token-here

# API Key 认证
DEEP_THINKING_API_KEY=your-api-key-here
```

详细的 SSE 配置请参考：[SSE 配置指南](./sse-guide.md)

---

## 升级与卸载

### 升级

**开发模式**：
```bash
# 拉取最新代码
git pull

# 重新安装（如果依赖有变化）
pip install -e .
```

**Wheel 安装**：
```bash
# 构建新版本
python -m build

# 强制重新安装
pip install --force-reinstall dist/deepthinking-*.whl
```

### 卸载

```bash
pip uninstall deep-thinking-mcp
```

---

## 故障排除

### 安装问题

**问题：Python 版本不兼容**
```
错误：Python 3.10 或更高版本 required
解决：升级 Python 版本
```

**问题：依赖安装失败**
```bash
# 更新 pip
pip install --upgrade pip

# 清除缓存重试
pip install --no-cache-dir -e .
```

### 运行问题

**问题：模块未找到**
```bash
# 确认安装位置
pip show deep-thinking-mcp

# 重新安装
pip install --force-reinstall -e .
```

**问题：权限错误**
```bash
# 使用用户安装
pip install --user -e .
```

---

## 下一步

- 📖 阅读 [用户指南](./user_guide.md) 了解如何使用
- ⚙️ 查看 [配置参数参考](./configuration.md) 了解所有配置选项
- 🔌 参考 [IDE 集成配置](./ide-config.md) 在你的 IDE 中配置
- 🌐 阅读 [SSE 配置指南](./sse-guide.md) 了解远程部署

---

## 相关文档

- [配置参数参考](./configuration.md) - 完整的环境变量配置
- [IDE 集成配置](./ide-config.md) - 各种 IDE 的配置示例
- [SSE 配置指南](./sse-guide.md) - SSE 远程模式详细配置
- [数据迁移指南](./MIGRATION.md) - 数据迁移和备份说明
- [用户指南](./user_guide.md) - 使用指南和最佳实践
