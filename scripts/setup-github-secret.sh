#!/bin/bash
# GitHub Secret 自动配置脚本
# 使用方法: ./scripts/setup-github-secret.sh <PYPI_TOKEN>

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# 检查参数
if [ -z "$1" ]; then
    echo -e "${YELLOW}用法: $0 <PYPI_API_TOKEN>${NC}"
    echo -e "${YELLOW}示例: $0 pypi-AgEIcHlwaS5vcmcC...${NC}"
    exit 1
fi

TOKEN="$1"

# 检查 gh 是否安装
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}错误: gh CLI 未安装${NC}"
    echo -e "${YELLOW}请访问: https://cli.github.com/${NC}"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}请先登录 GitHub:${NC}"
    echo -e "${BLUE}gh auth login${NC}"
    exit 1
fi

# 获取仓库信息
REPO=$(git remote get-url origin | sed -E 's|git@github.com:([^/]+)/([^/]+).git|\1/\2|' | sed -E 's|https://github.com/([^/]+)/([^/]+).git|\1/\2|')

if [ -z "$REPO" ]; then
    echo -e "${YELLOW}错误: 无法获取仓库信息${NC}"
    echo -e "${YELLOW}请确保在 Git 仓库中运行此脚本${NC}"
    exit 1
fi

echo -e "${BLUE}仓库: ${REPO}${NC}"
echo -e "${BLUE}Token: ${TOKEN:0:20}...${NC}"
echo ""

# 确认
read -p "确认配置？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}已取消${NC}"
    exit 0
fi

# 设置 Secret
echo -e "${BLUE}正在配置 GitHub Secret...${NC}"

gh secret set PYPI_API_TOKEN --body "$TOKEN" --repo "$REPO"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ GitHub Secret 配置成功！${NC}"
    echo -e "${GREEN}  仓库: ${REPO}${NC}"
    echo -e "${GREEN}  Secret: PYPI_API_TOKEN${NC}"
else
    echo -e "${YELLOW}配置失败，请检查权限${NC}"
    exit 1
fi
