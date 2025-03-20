@echo off
echo 正在启动 EchoTik 数据分析工具...

:: 创建必要的目录
mkdir data 2>nul
mkdir analysis 2>nul
mkdir tasks 2>nul

:: 检查 Python 环境
echo 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

:: 检查并安装 Python 依赖
echo 检查 Python 依赖...
python -c "import fastapi, uvicorn, selenium, cv2, numpy, openpyxl, requests, aiohttp, pandas, PIL, dotenv" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装 Python 依赖...
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    if %errorlevel% neq 0 (
        echo [警告] 依赖安装可能不完整，程序可能无法正常运行
        echo 请尝试手动执行: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    ) else (
        echo Python 依赖安装完成
    )
) else (
    echo Python 依赖检查通过
)

:: 设置控制台编码为 UTF-8
chcp 65001 >nul

:: 检查 Node.js 环境
echo 检查 Node.js 环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js，请安装 Node.js 16 或更高版本
    pause
    exit /b 1
)

:: 检查前端依赖
echo 检查前端依赖...
cd frontend
if not exist "node_modules" (
    echo 正在安装前端依赖...
    call npm config set registry http://registry.npmmirror.com
    call npm install
    if %errorlevel% neq 0 (
        echo [警告] 前端依赖安装可能不完整，程序可能无法正常运行
    ) else (
        echo 前端依赖安装完成
    )
) else (
    echo 前端依赖检查通过
)
cd ..

:: 启动后端服务
echo.
echo 正在启动后端服务...
start cmd /k "chcp 65001 >nul && echo 正在启动后端服务... && python api_server.py"

:: 启动前端服务
echo 正在启动前端服务...
cd frontend
start cmd /k "chcp 65001 >nul && echo 正在启动前端服务... && npm run dev && timeout /t 3 >nul"

:: 等待几秒钟确保服务启动
timeout /t 5 >nul

:: 打开默认浏览器访问前端页面
echo 正在打开浏览器...
start http://localhost:5173

echo.
echo 服务启动中，请稍候...
echo 后端服务地址: http://localhost:8000
echo 前端服务地址: http://localhost:5173
echo.
echo 提示: 
echo - 如需停止服务，请关闭对应的命令行窗口
echo - 浏览器将自动打开，如果没有自动打开，请手动访问 http://localhost:5173 