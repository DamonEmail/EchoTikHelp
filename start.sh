#!/bin/bash
echo "正在启动 EchoTik 数据分析工具..."

# 创建必要的目录
mkdir -p data
mkdir -p analysis
mkdir -p tasks

# 启动后端服务
gnome-terminal -- bash -c "echo '正在启动后端服务...' && python api_server.py; exec bash" || \
xterm -e "echo '正在启动后端服务...' && python api_server.py; exec bash" || \
konsole -e "echo '正在启动后端服务...' && python api_server.py; exec bash" || \
echo "无法打开新终端窗口，请手动启动后端服务"

# 启动前端服务
cd frontend
gnome-terminal -- bash -c "echo '正在启动前端服务...' && npm run dev; exec bash" || \
xterm -e "echo '正在启动前端服务...' && npm run dev; exec bash" || \
konsole -e "echo '正在启动前端服务...' && npm run dev; exec bash" || \
echo "无法打开新终端窗口，请手动启动前端服务"

echo ""
echo "服务启动中，请稍候..."
echo "后端服务地址: http://localhost:9527"
echo "前端服务地址: http://localhost:5173"
echo ""
echo "提示: 如需停止服务，请关闭对应的终端窗口" 