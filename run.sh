#!/bin/bash

# HIQ UPR Process Tree Builder - 启动脚本

echo "========================================"
echo "HIQ UPR Process Tree Builder"
echo "========================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python3"
    exit 1
fi

echo "✓ Python3 已安装: $(python3 --version)"

# 检查依赖是否安装
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo ""
    echo "⚠ 依赖未安装，正在安装..."
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✓ 依赖安装成功"
fi

echo ""
echo "========================================"
echo "步骤 1: 测试数据库连接"
echo "========================================"
python3 src/test_connection.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 数据库连接测试失败，请检查配置"
    exit 1
fi

echo ""
read -p "是否继续构建过程树？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "========================================"
echo "步骤 2: 构建过程树"
echo "========================================"
python3 src/build_process_tree.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 完成！"
    echo ""
    echo "生成的文件:"
    ls -lh output/process_tree.md 2>/dev/null
    echo ""
    echo "你也可以运行以下命令生成 JSON 格式:"
    echo "  python3 src/export_json.py"
else
    echo ""
    echo "❌ 构建失败"
    exit 1
fi

