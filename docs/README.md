# DeepThinking MCP 文档索引

> DeepThinking MCP - 提供顺序思考、会话管理和状态持久化功能的深度思考服务器

欢迎来到 DeepThinking MCP 文档中心！本文档提供完整的文档导航和快速开始指南。

---

## 🚀 快速开始

### 5分钟快速安装

**方式1：使用 pip 安装**（推荐）

```bash
pip install deep-thinking-mcp
```

**方式2：使用 uv 安装**

```bash
uv pip install deep-thinking-mcp
```

**方式3：开发模式安装**

```bash
git clone https://github.com/your-repo/Deep-Thinking-MCP.git
cd Deep-Thinking-MCP
pip install -e .
```

详细安装指南请参考：[安装指南](./installation.md)

### 快速配置

**1. 创建配置文件**

```bash
cp .env.example .env
```

**2. 编辑配置**

```bash
# 使用默认配置即可启动
DEEP_THINKING_TRANSPORT=stdio
```

**3. 验证安装**

```bash
python -m deep_thinking --help
```

详细配置请参考：[配置参数参考](./configuration.md)

---

## 📚 完整文档导航

### 安装与配置

| 文档 | 描述 | 适合人群 |
|------|------|---------|
| [安装指南](./installation.md) | 详细的安装和配置说明 | 新用户 |
| [配置参数参考](./configuration.md) | 所有环境变量的完整参考 | 高级用户 |
| [IDE集成配置](./ide-config.md) | 各种IDE的集成配置示例 | IDE用户 |
| [SSE配置指南](./sse-guide.md) | SSE模式远程部署指南 | 运维人员 |
| [数据迁移指南](./MIGRATION.md) | 数据迁移和备份说明 | 升级用户 |

### 使用指南

| 文档 | 描述 | 适合人群 |
|------|------|---------|
| [用户指南](./user_guide.md) | 完整的使用指南和最佳实践 | 所有用户 |
| [API参考](./api.md) | 所有MCP工具的完整API文档 | 开发者 |
| [工作流机制](./WORKFLOW_MECHANISM.md) | 思考工作流的内部机制 | 高级用户 |

### 技术文档

| 文档 | 描述 | 适合人群 |
|------|------|---------|
| [架构设计](../ARCHITECTURE.md) | 系统架构和设计文档 | 架构师 |
| [工作流可视化](./WORKFLOW_VISUALIZATION.md) | 思考流程的可视化说明 | 高级用户 |
| [异步同步分析](./ASYNC_SYNC_ANALYSIS.md) | 异步与同步模式的分析 | 开发者 |

### 开发指南

| 文档 | 描述 | 适合人群 |
|------|------|---------|
| [开发流程规范](./DEVELOPMENT_WORKFLOW.md) | 标准化的开发流程规范 | 贡献者 |
| [开发标准](./DEVELOPMENT_STANDARDS.md) | 代码规范和质量标准 | 贡献者 |
| [测试指南](./TESTING.md) | 测试规范和覆盖率要求 | 贡献者 |
| [发布指南](./PUBLISHING.md) | PyPI发布流程和规范 | 维护者 |

---

## 🎯 按场景查找

### 我想快速安装和开始使用

**推荐路径**：
1. [安装指南](./installation.md) - 选择安装方式
2. [配置参数参考](./configuration.md) - 基础配置
3. [用户指南](./user_guide.md) - 学习使用

### 我想了解所有配置选项

**推荐路径**：
1. [配置参数参考](./configuration.md) - 完整的参数列表
2. [.env.example](../.env.example) - 配置示例

### 我想在IDE中使用

**推荐路径**：
1. [IDE集成配置](./ide-config.md) - 选择你的IDE
2. [配置参数参考](./configuration.md) - 环境变量配置

### 我想部署到远程服务器

**推荐路径**：
1. [SSE配置指南](./sse-guide.md) - 远程部署配置
2. [配置参数参考](./configuration.md) - 认证和端口配置

### 我想升级到新版本

**推荐路径**：
1. [CHANGELOG](../CHANGELOG.md) - 版本变更记录
2. [数据迁移指南](./MIGRATION.md) - 数据迁移说明

### 我想参与开发

**推荐路径**：
1. [开发流程规范](./DEVELOPMENT_WORKFLOW.md) - 开发流程
2. [开发标准](./DEVELOPMENT_STANDARDS.md) - 代码规范
3. [测试指南](./TESTING.md) - 测试要求

### 我想了解API和工具

**推荐路径**：
1. [API参考](./api.md) - 完整的API文档
2. [架构设计](../ARCHITECTURE.md) - 系统架构

---

## 🔍 常见问题

### 如何配置环境变量？

请参考：[配置参数参考 - 环境变量配置方式](./configuration.md#环境变量配置方式)

### 如何修改数据存储路径？

请参考：[配置参数参考 - 存储配置](./configuration.md#存储配置)

### 如何配置SSE远程模式？

请参考：[SSE配置指南](./sse-guide.md)

### 如何在不同IDE中配置？

请参考：[IDE集成配置](./ide-config.md)

### 如何迁移旧数据？

请参考：[数据迁移指南](./MIGRATION.md)

### 代码覆盖率是多少？

当前代码覆盖率：**89.36%**（详见 [开发流程规范](./DEVELOPMENT_WORKFLOW.md)）

---

## 📊 项目统计

| 指标 | 数值 |
|------|------|
| 当前版本 | v0.2.3 |
| MCP工具数量 | 17个 |
| 环境变量数量 | 11个 |
| 代码覆盖率 | 89.36% |
| 文档总数 | 22个 |

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出改进建议！

**贡献流程**：
1. 阅读 [开发流程规范](./DEVELOPMENT_WORKFLOW.md)
2. 遵循 [开发标准](./DEVELOPMENT_STANDARDS.md)
3. 提交 Pull Request

---

## 📞 获取帮助

- **文档问题**：查看本文档或相关文档
- **Bug报告**：[GitHub Issues](https://github.com/your-repo/Deep-Thinking-MCP/issues)
- **功能请求**：[GitHub Discussions](https://github.com/your-repo/Deep-Thinking-MCP/discussions)

---

## 📝 文档更新记录

- **2026-01-08**: v0.2.3 版本文档更新，项目质量审核和版本统一
- **2026-01-02**: v0.2.0 版本文档更新
- **2026-01-01**: v0.1.0 首次发布

---

> **提示**：这是 DeepThinking MCP 的文档索引页面。如果你不知道从哪里开始，建议先阅读 [安装指南](./installation.md) 和 [用户指南](./user_guide.md)。
