# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

## [0.2.4] - 2026-02-14

### Added
- **Interleaved Thinking**: 新增三阶段执行模型
  - 支持 `phase` 参数（thinking/tool_call/analysis）
  - 自动阶段推断 (`infer_phase_from_lists`)
- **工具调用追踪**: 支持 1:N 思考-工具调用映射
  - 每个思考步骤可关联多个工具调用
  - 工具调用记录持久化存储
- **资源控制配置**:
  - `DEEP_THINKING_MAX_TOOL_CALLS`: 会话总工具调用次数上限 (默认100)
  - `DEEP_THINKING_MAX_TOOL_CALLS_PER_THOUGHT`: 每步骤工具调用次数上限 (默认10)
- **结果缓存支持**: 工具调用结果缓存标记 (`from_cache`)
- **分支思考可视化增强**: 改进 Mermaid/ASCII/Tree 三种格式的可视化输出

### Changed
- **sequential_thinking 工具扩展**:
  - 新增 `phase`, `toolCalls`, `toolResults` 参数
  - 支持 `needsMoreThoughts` 动态调整思考步骤数
- **SessionStatistics 扩展**:
  - 新增 `phase_distribution` 字段
  - 新增 `cached_tool_calls` 字段
  - 新增 `update_from_tool_calls()` 方法

### Fixed
- 修复 `update_from_thoughts()` 未计算 `phase_distribution` 的问题
- 修复 CLAUDE.md 环境变量表缺失 `DEEP_THINKING_THOUGHTS_INCREMENT` 参数

## [0.2.3] - 2026-01-10

### Added
- 项目质量审核和文档优化
- 版本号统一管理

### Changed
- 更新所有文档版本号至 0.2.3
- 更新 README.md 中的 wheel 安装示例版本号

### Fixed
- 修复 src/deep_thinking/__init__.py 版本号不一致问题（从 0.2.0 更新为 0.2.3）
- 修复 docs/user_guide.md 版本号过时问题（从 0.1.0 更新为 0.2.3）
- 修复 docs/sse-guide.md 版本号过时问题（从 0.1.0 更新为 0.2.3）
- 修复 docs/ide-config.md 版本号不一致问题（从 1.0.0 更新为 0.2.3）
- 修复 pytest-asyncio 事件循环冲突（MultipleEventLoopsRequestedError）
  - 移除8个测试类的 `loop_scope="class"` 装饰器参数
  - 使用默认函数作用域事件循环
  - 452个测试全部通过

### Changed
- 清理项目临时文件和目录（约193MB）
  - 删除 Python 字节码缓存（__pycache__、*.pyc）
  - 删除测试缓存（.pytest_cache、.mypy_cache）
  - 删除测试虚拟环境（test_install_venv、test_env）
  - 删除非核心目录（autonomous-coding、claude-code-docs）
  - 删除临时文档文件
- 更新 .gitignore 文件，添加临时文件过滤规则

### Documentation
- 更新用户指南版本号（0.1.0 → 0.2.3）
- 更新SSE配置指南版本号（0.1.0 → 0.2.3）
- 更新所有文档版本信息至 0.2.3

---

## [Unreleased]

### Added
- **docs**: 新增文档索引 (docs/README.md) - 完整的文档导航和快速开始指南
- **docs**: 新增统一配置指南 (docs/configuration.md) - 所有环境变量的完整参考
- **scripts**: 新增配置参数文档生成脚本 (scripts/generate_config_docs.py) - 从代码自动生成配置文档
- **docs**: 在 claude-code-config.md 和 ide-config.md 中添加完整配置快速参考章节
- **config**: 在 .env.example 中添加 DEEP_THINKING_DESCRIPTION 配置示例

### Changed
- **config**: 更新 DEEP_THINKING_DESCRIPTION 默认值描述
  - 添加"高级思维编排引擎"定位
  - 添加"适合处理多步骤、跨工具的复杂任务"使用场景
  - 新默认值："深度思考MCP服务器 - 高级思维编排引擎，提供顺序思考,适合处理多步骤、跨工具的复杂任务,会话管理和状态持久化功能"
- **docs**: 精简配置文档，消除冗余内容
  - installation.md: 1011行 → 317行 (-69%)
  - claude-code-config.md: 1063行 → 313行 (-71%)
  - ide-config.md: 681行 → 274行 (-60%)
  - 总计减少约2000-2500行冗余内容
- **docs**: 重构文档结构，使用交叉引用替代重复内容
- **docs**: 更新根目录 README.md，添加新文档链接和分组导航

### Fixed
- **docs**: 统一配置参数描述，确保与代码100%一致
- **docs**: 消除文档间的重复配置示例

---

## [0.2.2] - 2026-01-08

### Added
- 项目审核和文档优化
- 统一配置参数说明

### Changed
- 修复默认描述不一致（统一为"深度思考MCP服务器 - 提供顺序思考、会话管理和状态持久化功能"）
- 统一SSE端口号（从8088改为8000）
- 统一HOST值表述（从127.0.0.1改为localhost）
- 更新installation.md中的默认描述

### Fixed
- 修复README.md中的默认描述不一致
- 修复ide-config.md中的默认描述不一致
- 修复installation.md中的SSE端口号不一致
- 修复installation.md中的HOST值表述不一致

## [0.2.0] - 2026-01-02

### Added
- 新增对比思考（Comparison Thinking）类型
- 新增逆向思考（Reverse Thinking）类型
- 新增假设思考（Hypothetical Thinking）类型
- 支持思考步骤动态调整（needsMoreThoughts）
- 支持通过环境变量自定义服务器描述

### Changed
- 优化思考类型系统架构
- 改进测试覆盖率到90%+
- 更新API文档

## [0.1.0] - 2026-01-02

### Added
- 首次正式发布
- 实现顺序思考工具
- 实现会话管理功能
- 实现任务管理功能
- 实现模板系统
- 实现导出和可视化功能
- 实现双传输模式（STDIO/SSE）
- 完整的测试覆盖（356个测试）
