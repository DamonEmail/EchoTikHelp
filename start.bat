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
python -c "import fastapi, uvicorn, selenium, cv2, numpy, openpyxl, requests, aiohttp, pandas, PIL, dotenv, bs4, lxml" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装 Python 依赖...
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    if %errorlevel% neq 0 (
        echo [警告] 依赖安装可能不完整，程序可能无法正常运行
        echo 请尝试手动执行: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
        echo 或者单独安装缺失的包: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple 包名
        pause
    ) else (
        echo Python 依赖安装完成
    )
) else (
    echo Python 依赖检查通过
)

:: 检查并下载 ChromeDriver
echo 检查 ChromeDriver...
python -c "from selenium import webdriver; from selenium.webdriver.chrome.service import Service as ChromeService; from webdriver_manager.chrome import ChromeDriverManager; from selenium.webdriver.chrome.options import Options; options = Options(); options.add_argument('--headless'); webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装 ChromeDriver...
    python -c "from webdriver_manager.chrome import ChromeDriverManager; print('ChromeDriver 路径:', ChromeDriverManager().install())"
    if %errorlevel% neq 0 (
        echo [警告] ChromeDriver 安装失败，分析功能可能无法正常工作
        echo 请确保已安装 Chrome 浏览器，并且网络连接正常
        echo 尝试设置 PYTHONPATH 环境变量...
        set PYTHONPATH=%PYTHONPATH%;%USERPROFILE%\.wdm\drivers\chromedriver
        pause
    ) else (
        echo ChromeDriver 安装完成
        echo 设置 PATH 环境变量...
        set PATH=%PATH%;%USERPROFILE%\.wdm\drivers\chromedriver
    )
) else (
    echo ChromeDriver 检查通过
    echo 设置 PATH 环境变量...
    set PATH=%PATH%;%USERPROFILE%\.wdm\drivers\chromedriver
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
:: 保存当前目录路径
set CURRENT_DIR=%CD%

:: 检查端口 9527 是否被占用
netstat -ano | find ":9527" >nul
if not errorlevel 1 (
    echo [警告] 端口 9527 已被占用，请关闭占用该端口的程序后重试
    echo 您可以使用以下命令查看占用端口的程序：
    echo netstat -ano ^| find ":9527"
    pause
    exit /b 1
)

:: 以管理员权限启动后端服务，同时保持在当前目录
powershell -Command "Start-Process cmd -ArgumentList '/k cd /d %CURRENT_DIR% && chcp 65001 >nul && echo 正在启动后端服务... && python api_server.py' -Verb RunAs"
if %errorlevel% neq 0 (
    echo [警告] 管理员权限启动失败，尝试普通方式启动...
    start cmd /k "cd /d %CURRENT_DIR% && chcp 65001 >nul && echo 正在启动后端服务... && python api_server.py"
)

:: 启动前端服务
echo 正在启动前端服务...
:: 检查端口 5173 是否被占用
netstat -ano | find ":5173" >nul
if not errorlevel 1 (
    echo [警告] 端口 5173 已被占用，请关闭占用该端口的程序后重试
    echo 您可以使用以下命令查看占用端口的程序：
    echo netstat -ano ^| find ":5173"
    pause
    exit /b 1
)

cd frontend
start cmd /k "chcp 65001 >nul && echo 正在启动前端服务... && npm run dev && timeout /t 3 >nul"

:: 等待几秒钟确保服务启动
timeout /t 5 >nul

:: 打开默认浏览器访问前端页面
echo 正在打开浏览器...
start http://localhost:5173

echo.
echo 服务启动中，请稍候...
echo 后端服务地址: http://localhost:9527
echo 前端服务地址: http://localhost:5173
echo.
echo 提示: 
echo - 如需停止服务，请关闭对应的命令行窗口
echo - 浏览器将自动打开，如果没有自动打开，请手动访问 http://localhost:5173 