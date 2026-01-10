.PHONY: help install dev test lint format typecheck clean build check publish publish-test release

# 默认目标
.DEFAULT_GOAL := help

# 项目配置
PROJECT_NAME := DeepThinking
PYTHON := python3
VENV := .venv/bin
UV := uv

# 颜色输出
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

## help: 显示此帮助信息
help:
	@echo "$(BLUE)DeepThinking MCP - 发布自动化工具$(NC)"
	@echo ""
	@echo "$(GREEN)可用命令:$(NC)"
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## /  /' | column -t -s ':'
	@echo ""

## install: 安装项目依赖
install:
	@echo "$(BLUE)安装依赖...$(NC)"
	$(UV) pip install -e ".[dev]"

## dev: 以开发模式安装
dev:
	@echo "$(BLUE)开发模式安装...$(NC)"
	$(UV) pip install -e ".[dev]"

## test: 运行测试套件
test:
	@echo "$(BLUE)运行测试...$(NC)"
	$(VENV)/pytest -v --cov=deep_thinking --cov-report=term-missing --cov-report=html

## test-unit: 仅运行单元测试
test-unit:
	@echo "$(BLUE)运行单元测试...$(NC)"
	$(VENV)/pytest tests/ -v -m "not integration"

## test-integration: 仅运行集成测试
test-integration:
	@echo "$(BLUE)运行集成测试...$(NC)"
	$(VENV)/pytest tests/ -v -m "integration"

## lint: 运行代码检查
lint:
	@echo "$(BLUE)检查代码质量...$(NC)"
	$(VENV)/ruff check src/ tests/

## format: 格式化代码
format:
	@echo "$(BLUE)格式化代码...$(NC)"
	$(VENV)/ruff format src/ tests/

## format-check: 检查代码格式
format-check:
	@echo "$(BLUE)检查代码格式...$(NC)"
	$(VENV)/ruff format --check src/ tests/

## typecheck: 运行类型检查
typecheck:
	@echo "$(BLUE)运行类型检查...$(NC)"
	$(VENV)/mypy src/deep_thinking/

## check: 运行所有检查（测试 + 代码质量 + 类型）
check: test lint format-check typecheck
	@echo "$(GREEN)✓ 所有检查通过！$(NC)"

## clean: 清理构建产物
clean:
	@echo "$(BLUE)清理构建文件...$(NC)"
	rm -rf dist/ build/ *.egg-info .pytest_cache .ruff_cache .mypy_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ 清理完成$(NC)"

## build: 构建 PyPI 分发包
build: clean
	@echo "$(BLUE)构建分发包...$(NC)"
	$(VENV)/python -m build
	@echo "$(GREEN)✓ 构建完成$(NC)"
	@ls -lh dist/

## verify: 验证分发包元数据
verify: build
	@echo "$(BLUE)验证分发包...$(NC)"
	$(VENV)/twine check dist/*
	@echo "$(GREEN)✓ 验证通过$(NC)"

## release-check: 完整的发布前检查
release-check: format lint typecheck test
	@echo "$(GREEN)✓ 发布前检查完成！$(NC)"

## publish-test: 发布到 TestPyPI
publish-test: verify
	@echo "$(YELLOW)发布到 TestPyPI...$(NC)"
	@echo "请确保已设置 TWINE_USERNAME 和 TWINE_PASSWORD 环境变量"
	$(VENV)/twine upload --repository testpypi dist/*

## publish: 发布到 PyPI
publish: verify
	@echo "$(YELLOW)发布到 PyPI...$(NC)"
	@echo "请确保已设置 TWINE_USERNAME 和 TWINE_PASSWORD 环境变量"
	$(VENV)/twine upload dist/*

## release: 完整的发布流程（检查 + 构建 + 发布）
release: release-check build publish
	@echo "$(GREEN)✓ 发布完成！$(NC)"

## version-patch: 增加补丁版本 (0.2.3 -> 0.2.4)
version-patch:
	@echo "$(BLUE)增加补丁版本...$(NC)"
	@$(VENV)/python scripts/bump_version.py patch

## version-minor: 增加次版本 (0.2.3 -> 0.3.0)
version-minor:
	@echo "$(BLUE)增加次版本...$(NC)"
	@$(VENV)/python scripts/bump_version.py minor

## version-major: 增加主版本 (0.2.3 -> 1.0.0)
version-major:
	@echo "$(BLUE)增加主版本...$(NC)"
	@$(VENV)/python scripts/bump_version.py major

## setup-release: 发布准备（更新 CHANGELOG、Git tag）
setup-release:
	@echo "$(YELLOW)发布准备...$(NC)"
	@echo "1. 请更新 CHANGELOG.md"
	@echo "2. 请更新 pyproject.toml 中的版本号（如需要）"
	@echo "3. 运行: git add -A && git commit -m 'chore: prepare for release vX.X.X'"
	@echo "4. 运行: git tag vX.X.X"
	@echo "5. 运行: make release"

## docs-serve: 启动文档服务器
docs-serve:
	@echo "$(BLUE)启动文档服务器...$(NC)"
	@echo "文档地址: http://localhost:8000"
	@cd docs && $(VENV)/python -m http.server 8000

## benchmark: 运行性能基准测试
benchmark:
	@echo "$(BLUE)运行基准测试...$(NC)"
	$(VENV)/pytest tests/benchmarks/ -v --benchmark-only

## all: 完整的工作流（格式化 + 检查 + 测试 + 构建）
all: format lint typecheck test build
	@echo "$(GREEN)✓ 完整工作流完成！$(NC)"

## setup-token: 配置全局 PyPI Token（一次配置，所有项目通用）
setup-token:
	@echo "$(YELLOW)配置全局 PyPI Token...$(NC)"
	@echo "$(BLUE)用法: make setup-token TOKEN=pypi-...$(NC)"
	@if [ -z "$(TOKEN)" ]; then \
		echo "$(RED)错误: 请提供 TOKEN 参数$(NC)"; \
		echo "$(YELLOW)示例: make setup-token TOKEN=pypi-AgEIcHlwaS5vcmcC...$(NC)"; \
		exit 1; \
	fi
	@bash scripts/setup-pypi-token.sh "$(TOKEN)"

## setup-github: 配置 GitHub Secret（用于自动化发布）
setup-github:
	@echo "$(YELLOW)配置 GitHub Secret...$(NC)"
	@echo "$(BLUE)用法: make setup-github TOKEN=pypi-...$(NC)"
	@if [ -z "$(TOKEN)" ]; then \
		echo "$(RED)错误: 请提供 TOKEN 参数$(NC)"; \
		echo "$(YELLOW)示例: make setup-github TOKEN=pypi-AgEIcHlwaS5vcmcC...$(NC)"; \
		exit 1; \
	fi
	@bash scripts/setup-github-secret.sh "$(TOKEN)"

## setup-all: 一键配置所有发布环境
setup-all:
	@echo "$(YELLOW)一键配置发布环境...$(NC)"
	@if [ -z "$(TOKEN)" ]; then \
		echo "$(RED)错误: 请提供 TOKEN 参数$(NC)"; \
		echo "$(YELLOW)示例: make setup-all TOKEN=pypi-AgEIcHlwaS5vcmcC...$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)1. 配置全局 PyPI Token...$(NC)"
	@bash scripts/setup-pypi-token.sh "$(TOKEN)"
	@echo ""
	@echo "$(BLUE)2. 配置 GitHub Secret...$(NC)"
	@bash scripts/setup-github-secret.sh "$(TOKEN)"
	@echo ""
	@echo "$(GREEN)✓ 所有配置完成！$(NC)"
	@echo "$(BLUE)现在可以:$(NC)"
	@echo "  - 本地发布: make publish"
	@echo "  - 自动发布: git tag v0.2.4 && git push origin v0.2.4"
