import os
import subprocess
import sys
import time
from pathlib import Path

def check_python_packages():
    """检查并安装后端所需的 Python 包"""
    print("\n=== 检查后端依赖 ===")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "requests",
        "python-multipart",
        "pydantic",
        "beautifulsoup4",
        "selenium",
        "pillow",
        "opencv-python",
        "numpy",
        "openpyxl",
        "pandas"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"安装 {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

def check_node_packages():
    """检查并安装前端所需的 npm 包"""
    print("\n=== 检查前端依赖 ===")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("错误: 找不到 frontend 目录")
        return False
        
    # 检查 node_modules 是否存在
    if not (frontend_dir / "node_modules").exists():
        print("安装前端依赖...")
        subprocess.run("npm install", shell=True, cwd=frontend_dir, check=True)
    else:
        print("✓ 前端依赖已安装")
    
    return True

def start_backend():
    """启动后端服务"""
    print("\n=== 启动后端服务 ===")
    return subprocess.Popen([sys.executable, "api_server.py"])

def start_frontend():
    """启动前端服务"""
    print("\n=== 启动前端服务 ===")
    return subprocess.Popen("npm run dev", shell=True, cwd="frontend")

def main():
    """主函数"""
    try:
        # 检查 Node.js 是否安装
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            print("✓ Node.js 已安装")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("错误: 请先安装 Node.js")
            return
        
        # 检查并安装依赖
        check_python_packages()
        if not check_node_packages():
            return
            
        # 启动后端
        backend_process = start_backend()
        time.sleep(2)  # 等待后端启动
        
        # 启动前端
        frontend_process = start_frontend()
        
        print("\n=== 服务已启动 ===")
        print("前端地址: http://localhost:5173")
        print("后端地址: http://localhost:9527")
        print("\n按 Ctrl+C 停止服务...")
        
        # 等待用户中断
        backend_process.wait()
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n=== 正在停止服务 ===")
        if 'backend_process' in locals():
            backend_process.terminate()
        if 'frontend_process' in locals():
            frontend_process.terminate()
        print("服务已停止")
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 