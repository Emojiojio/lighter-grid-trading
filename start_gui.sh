#!/bin/bash

# 快速启动图形界面脚本

cd "$(dirname "$0")"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python"
    exit 1
fi

# 安装依赖
pip3 install -q -r requirements.txt

# 启动图形界面
python3 gui.py


