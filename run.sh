#!/bin/bash

# 一键启动脚本
# 用于快速启动网格交易策略配置和运行

echo "=========================================="
echo "Lighter 交易所网格交易策略"
echo "=========================================="
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python"
    exit 1
fi

# 检查是否已安装依赖
if [ ! -f "requirements.txt" ]; then
    echo "⚠️  未找到 requirements.txt，正在创建..."
    cat > requirements.txt << EOF
requests>=2.31.0
EOF
fi

# 安装依赖
echo "正在检查依赖..."
pip3 install -q -r requirements.txt

# 显示菜单
echo ""
echo "请选择操作:"
echo "1. 启动图形界面（推荐）"
echo "2. 配置策略参数（命令行）"
echo "3. 启动网格交易策略（命令行）"
echo "4. 退出"
echo ""

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "启动图形界面..."
        python3 gui.py
        ;;
    2)
        echo ""
        echo "启动配置向导..."
        python3 interactive_setup.py
        ;;
    3)
        echo ""
        echo "启动网格交易策略..."
        python3 main.py
        ;;
    4)
        echo "退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

