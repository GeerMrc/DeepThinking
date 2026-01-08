# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
