# EchoTik 数据分析工具

## 项目简介

EchoTik 数据分析工具是一个用于抓取、分析和匹配电商产品数据的应用程序。它可以帮助用户快速找到相似商品，分析价格和销量数据，提供商品匹配建议。

## 环境要求

以下软件需要用户手动安装：

- **Python 3.8+** - [下载地址](https://www.python.org/downloads/)
- **Node.js 16+** - [下载地址](https://nodejs.org/en/download/)
- **Chrome 浏览器** - [下载地址](https://www.google.com/chrome/)

其他依赖项（如 Python 包和 Node.js 模块）将由启动脚本自动检查并安装。

## 快速开始

### Windows 用户

1. 克隆或下载本项目到本地
2. 双击运行 `start.bat` 文件
3. 启动脚本会自动：
   - 检查并创建必要的目录
   - 检查 Python 和 Node.js 环境
   - 安装所需的依赖项（如果缺少）
   - 启动后端和前端服务

## 访问应用

启动成功后，可以通过浏览器访问：

- 前端界面：http://localhost:5173

## 使用说明

1. 在首页可以创建新任务或查看已有任务
2. 创建任务时需要提供 Cookie 和 Authorization 信息
3. 选择商品类别或输入关键词进行数据抓取
4. 抓取完成后，可以对数据进行分析
5. 分析结果会显示匹配的商品信息

## 目录结构

## 常见问题

1. **启动失败**

   - 确保已安装 Python 3.8+ 和 Node.js 16+
   - 确保 Chrome 浏览器已安装
   - 如果提示端口被占用：

     1. 使用管理员权限运行 start.bat
     2. 或手动关闭占用端口的程序：

     ```
     # 查看占用端口的程序
     netstat -ano | find ":9527"    # 查看后端端口
     netstat -ano | find ":5173"    # 查看前端端口

     # 使用任务管理器结束对应的进程
     taskkill /F /PID <进程ID>
     ```

   - 如果提示访问权限不允许：
     - 右键 start.bat 选择"以管理员身份运行"
     - 或检查防火墙设置是否阻止了程序访问网络

2. **中文乱码**

   - 如果看到乱码，请尝试在命令行中执行：`chcp 65001`
   - 或者重新打开命令行窗口

3. **依赖安装失败**

   - 如果自动安装失败，可以手动执行以下命令：
     ```
     pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
     cd frontend && npm install
     ```

4. **运行时缺少依赖**
   - 如果运行时提示缺少某个模块，请检查 requirements.txt 文件
   - 可以手动安装缺失的依赖：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple 模块名`
   - 或者重新安装所有依赖：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`
