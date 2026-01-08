# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **docs**: 新增文档索引 (docs/README.md) - 完整的文档导航和快速开始指南
- **docs**: 新增统一配置指南 (docs/configuration.md) - 所有环境变量的完整参考
- **scripts**: 新增配置参数文档生成脚本 (scripts/generate_config_docs.py) - 从代码自动生成配置文档

### Changed
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
