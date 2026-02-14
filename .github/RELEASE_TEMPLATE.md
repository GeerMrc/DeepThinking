# Release v${VERSION}

## 🚀 DeepThinking MCP v${VERSION} - ${TITLE}

### ✨ 主要变更

${CHANGES}

### 📦 安装方式

**从 PyPI 安装（推荐）**
```bash
pip install DeepThinking
```

**使用 uv 安装（更快）**
```bash
uv pip install DeepThinking
```

**开发模式安装**
```bash
git clone https://github.com/GeerMrc/DeepThinking.git
cd DeepThinking
pip install -e ".[dev]"
```

### 📊 质量指标

- **代码覆盖率**: ${COVERAGE}
- **测试通过**: ${TESTS} ✅
- **Ruff 代码检查**: 全部通过 ✅

### 🎯 核心特性

- **双传输模式**: STDIO（本地）和 SSE（远程）
- **六种思考类型**: 常规💭、修订🔄、分支🌿、对比⚖️、逆向🔙、假设🤔
- **三阶段执行模型**: 思考 → 工具调用 → 分析
- **会话管理**: 创建/查询/删除/恢复思考会话
- **任务管理**: 完整的任务清单管理功能
- **模板系统**: 预设思考框架（问题求解、决策、分析）
- **多格式导出**: JSON/Markdown/HTML/Text
- **可视化**: Mermaid 流程图/ASCII/树状结构

### 📝 完整变更日志

详见 [CHANGELOG.md](https://github.com/GeerMrc/DeepThinking/blob/master/CHANGELOG.md)

### 🔗 相关链接

- **文档**: [docs/README.md](https://github.com/GeerMrc/DeepThinking/blob/master/docs/README.md)
- **安装指南**: [docs/installation.md](https://github.com/GeerMrc/DeepThinking/blob/master/docs/installation.md)
- **配置参考**: [docs/configuration.md](https://github.com/GeerMrc/DeepThinking/blob/master/docs/configuration.md)
- **API 文档**: [docs/api.md](https://github.com/GeerMrc/DeepThinking/blob/master/docs/api.md)

---

**发布日期**: ${DATE}  
**PyPI 包名**: DeepThinking  
**许可证**: MIT
