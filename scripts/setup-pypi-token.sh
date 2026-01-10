#!/bin/bash
# PyPI Token 全局配置脚本
# 配置后所有项目都可以使用同一个 Token

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查参数
if [ -z "$1" ]; then
    echo -e "${YELLOW}用法: $0 <PYPI_API_TOKEN>${NC}"
    echo -e "${YELLOW}示例: $0 pypi-AgEIcHlwaS5vcmcC...${NC}"
    exit 1
fi

TOKEN="$1"

# 检测 Shell 类型
SHELL_NAME=$(basename "$SHELL")
echo -e "${BLUE}检测到 Shell: ${SHELL_NAME}${NC}"

# 确定配置文件
case "$SHELL_NAME" in
    zsh)
        CONFIG_FILE="$HOME/.zshrc"
        ;;
    bash)
        CONFIG_FILE="$HOME/.bashrc"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            CONFIG_FILE="$HOME/.bash_profile"
        fi
        ;;
    *)
        echo -e "${RED}不支持的 Shell: ${SHELL_NAME}${NC}"
        echo -e "${YELLOW}请手动配置环境变量${NC}"
        exit 1
        ;;
esac

echo -e "${BLUE}配置文件: ${CONFIG_FILE}${NC}"

# 检查是否已配置
if grep -q "PYPI_API_TOKEN" "$CONFIG_FILE" 2>/dev/null; then
    echo -e "${YELLOW}PYPI_API_TOKEN 已存在，是否覆盖？${NC}"
    read -p "(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}已取消${NC}"
        exit 0
    fi
    # 删除旧配置
    sed -i.bak '/PYPI_API_TOKEN/d' "$CONFIG_FILE"
fi

# 添加新配置
cat >> "$CONFIG_FILE" << 'EOF'

# PyPI API Token (用于发布 Python 包到 PyPI)
export PYPI_API_TOKEN="YOUR_TOKEN_HERE"
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="${PYPI_API_TOKEN}"
EOF

# 替换 Token
sed -i.bak "s|YOUR_TOKEN_HERE|${TOKEN}|g" "$CONFIG_FILE"

echo -e "${GREEN}✓ 配置已添加到 ${CONFIG_FILE}${NC}"
echo ""
echo -e "${YELLOW}请执行以下命令使配置生效:${NC}"
echo -e "${BLUE}source ${CONFIG_FILE}${NC}"
echo ""
echo -e "${GREEN}或者重启终端${NC}"

# 创建 ~/.pypirc
echo -e "${BLUE}同时创建 ~/.pypirc 配置文件...${NC}"
cat > "$HOME/.pypirc" << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = ${TOKEN}

[testpypi]
username = __token__
password = ${TOKEN}
repository = https://test.pypi.org/legacy/
EOF

echo -e "${GREEN}✓ ~/.pypirc 已创建${NC}"
echo ""
echo -e "${GREEN}配置完成！现在可以使用以下命令发布:${NC}"
echo -e "${BLUE}  make publish${NC}"
echo -e "${BLUE}  twine upload dist/*${NC}"
echo -e "${BLUE}  (无需再输入用户名和密码)${NC}"
