from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Union
import uvicorn
import os
import json
from datetime import datetime
from crawler import EchoTikCrawler
import asyncio
import threading
from queue import Queue
from fastapi.responses import FileResponse
import shutil
from pathlib import Path
from analyse import analyze_product_data as analyze_data, analyze_1688

app = FastAPI(title="EchoTik Data API")

# 修改 CORS 配置，确保前端可以正常访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储所有任务数据的字典
tasks = {"tasks": {}}

# 添加任务存储相关的常量
TASKS_FILE = "tasks.json"
TASKS_DIR = Path("tasks")
ANALYSIS_DIR = Path("analysis")
DATA_DIR = Path("data")

# 创建必要的目录
TASKS_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

def load_tasks():
    """从文件加载任务数据"""
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict) or "tasks" not in data:
                    return {"tasks": {}}
                return data
    except Exception as e:
        print(f"加载任务数据失败: {e}")
    return {"tasks": {}}

def save_tasks():
    """保存任务数据到文件"""
    try:
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"保存任务数据失败: {e}")

class CrawlRequest(BaseModel):
    category_id: Optional[str] = None
    keyword: Optional[str] = None
    cookie: str
    authorization: str

class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending", "running", "completed", "failed"
    message: str
    result: Optional[Dict] = None

class AnalyzeRequest(BaseModel):
    task_id: str
    strategy: str = 'top50'  # 默认使用 top50 策略

def generate_task_id(category_id: Optional[str], keyword: Optional[str]) -> str:
    """生成任务ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if category_id:
        return f"cat_{category_id}_{timestamp}"
    elif keyword:
        return f"kw_{keyword}_{timestamp}"
    return f"task_{timestamp}"

async def crawl_data(task_id: str, category_id: Optional[str], 
                    keyword: Optional[str], cookie: str, authorization: str):
    """执行爬虫任务"""
    try:
        # 确保 tasks 字典结构正确
        if "tasks" not in tasks:
            tasks["tasks"] = {}
        
        tasks["tasks"][task_id] = {"status": "running", "message": "正在爬取数据..."}
        save_tasks()  # 保存任务状态
        
        crawler = EchoTikCrawler()
        # 更新认证信息
        crawler.update_cookie(cookie)
        crawler.headers['authorization'] = authorization
        
        if category_id:
            crawler.default_params['product_categories'] = category_id
        if keyword:
            crawler.default_params['keyword'] = keyword
            
        # 在新线程中运行爬虫
        def run_crawler():
            try:
                crawler.crawl(start_page=1)
                # 获取生成的文件路径
                data_dir = crawler.data_dir
                latest_file = max([f for f in os.listdir(data_dir) 
                                 if f.startswith(f'products_cat{category_id}_' if category_id 
                                               else 'products_kw_')],
                                key=lambda x: os.path.getctime(os.path.join(data_dir, x)))
                file_path = os.path.join(data_dir, latest_file)
                
                tasks["tasks"][task_id] = {
                    "status": "completed",
                    "message": "数据爬取完成",
                    "file_path": file_path,
                    "file_name": latest_file
                }
                save_tasks()  # 保存任务结果
            except Exception as e:
                tasks["tasks"][task_id] = {
                    "status": "failed",
                    "message": f"爬取失败: {str(e)}",
                    "error": str(e)
                }
        
        # 启动爬虫线程
        thread = threading.Thread(target=run_crawler)
        thread.start()
        
    except Exception as e:
        tasks["tasks"][task_id] = {
            "status": "failed",
            "message": f"任务启动失败: {str(e)}"
        }
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crawl", response_model=TaskStatus)
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """启动数据爬取任务"""
    if not request.category_id and not request.keyword:
        raise HTTPException(status_code=400, 
                          detail="必须提供category_id或keyword其中之一")
        
    task_id = generate_task_id(request.category_id, request.keyword)
    
    # 确保 tasks 字典结构正确
    if "tasks" not in tasks:
        tasks["tasks"] = {}
    
    # 启动异步任务
    background_tasks.add_task(crawl_data, task_id, 
                            request.category_id, request.keyword, request.cookie, request.authorization)
    
    return TaskStatus(
        task_id=task_id,
        status="pending",
        message="任务已创建，正在启动..."
    )

@app.get("/api/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """获取任务状态"""
    global tasks
    tasks = load_tasks()
    
    if task_id not in tasks["tasks"]:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks["tasks"][task_id]
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        message=task["message"],
        result=task
    )

@app.get("/api/download/{task_id}")
async def download_file(task_id: str, type: str = 'raw'):
    """下载文件
    type: 'raw' 原始数据文件, 'analysis' 分析结果文件
    """
    if task_id not in tasks["tasks"]:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = tasks["tasks"][task_id]
    
    if type == 'analysis':
        if not result.get("analysis_file") or not os.path.exists(result["analysis_file"]):
            raise HTTPException(status_code=404, detail="分析文件不存在")
        file_path = result["analysis_file"]
        file_name = os.path.basename(file_path)
    else:
        if not result.get("file_path") or not os.path.exists(result["file_path"]):
            raise HTTPException(status_code=404, detail="文件不存在")
        file_path = result["file_path"]
        file_name = result["file_name"]
    
    return FileResponse(
        file_path,
        filename=file_name,
        media_type="application/octet-stream"
    )

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务及其相关数据"""
    global tasks
    tasks = load_tasks()
    
    if task_id not in tasks["tasks"]:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks["tasks"][task_id]
    try:
        # 删除原始数据文件
        file_path = task.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"已删除原始数据文件: {file_path}")
            except Exception as e:
                print(f"删除原始文件失败: {e}")
        
        # 删除分析结果文件
        analysis_file = task.get("analysis_file")
        if analysis_file and os.path.exists(analysis_file):
            try:
                os.remove(analysis_file)
                print(f"已删除分析Excel文件: {analysis_file}")
            except Exception as e:
                print(f"删除分析Excel文件失败: {e}")
        
        # 删除分析结果JSON文件
        analysis_json = task.get("analysis_json")
        if analysis_json and os.path.exists(analysis_json):
            try:
                os.remove(analysis_json)
                print(f"已删除分析JSON文件: {analysis_json}")
            except Exception as e:
                print(f"删除分析JSON文件失败: {e}")
        
    except Exception as e:
        print(f"删除文件时出错: {e}")
    
    # 从任务字典中删除任务
    del tasks["tasks"][task_id]
    
    # 保存更新后的任务数据
    save_tasks()
    
    return {"message": "任务及相关数据已删除"}

@app.post("/api/analyze")
async def start_analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """启动数据分析任务"""
    print(f"\n=== 收到分析请求 ===")
    print(f"请求参数: {request}")
    
    # 重新加载最新的任务数据
    global tasks
    tasks = load_tasks()
    
    if request.task_id not in tasks["tasks"]:
        print(f"任务不存在: {request.task_id}")
        print(f"当前任务列表: {tasks}")
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks["tasks"][request.task_id]
    print(f"当前任务状态: {task}")
    
    # 只要有原始数据文件就可以进行分析
    if not task.get("file_path") or not os.path.exists(task["file_path"]):
        raise HTTPException(status_code=404, detail="数据文件不存在，无法进行分析")
    
    if task["status"] == "analyzing":
        raise HTTPException(
            status_code=400, 
            detail="任务正在分析中，请等待当前分析完成"
        )
    
    # 更新任务状态为分析中
    task["status"] = "analyzing"
    task["message"] = "正在进行数据分析..."
    # 清除之前的分析结果（如果有）
    if "analysis_file" in task:
        del task["analysis_file"]
    if "analysis_json" in task:
        del task["analysis_json"]
    save_tasks()
    
    # 启动分析任务
    async def run_analyze():
        try:
            # 执行数据分析
            output_files = analyze_data(task["file_path"], strategy=request.strategy)
            
            if isinstance(output_files, tuple) and len(output_files) == 2:
                excel_file, json_file = output_files
            else:
                excel_file = output_files
                json_file = None
            
            # 更新任务状态
            task["status"] = "completed"
            task["message"] = "分析完成"
            task["analysis_file"] = excel_file
            if json_file:
                task["analysis_json"] = json_file
            save_tasks()
            
        except Exception as e:
            task["status"] = "failed"
            task["message"] = f"分析失败: {str(e)}"
            # 清除可能的部分分析结果
            if "analysis_file" in task:
                del task["analysis_file"]
            if "analysis_json" in task:
                del task["analysis_json"]
            save_tasks()
            print(f"分析过程出错: {str(e)}")
    
    background_tasks.add_task(run_analyze)
    return {"message": "分析任务已启动"}

@app.get("/api/analysis/{task_id}")
async def get_analysis_results(task_id: str):
    """获取分析结果数据"""
    global tasks
    tasks = load_tasks()
    
    if task_id not in tasks["tasks"]:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = tasks["tasks"][task_id]
    
    if result.get("status") != "completed":
        raise HTTPException(status_code=400, detail="分析尚未完成")
    
    analysis_json = result.get("analysis_json")
    if not analysis_json or not os.path.exists(analysis_json):
        raise HTTPException(status_code=404, detail="分析结果数据不存在")
    
    try:
        with open(analysis_json, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        return analysis_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取分析结果失败: {str(e)}")

@app.get("/api/tasks")
async def get_tasks():
    """获取所有任务状态"""
    try:
        # 先加载最新的任务数据
        tasks_data = load_tasks()
        
        # 确保 tasks_data 和 tasks_data["tasks"] 存在
        if not tasks_data or not isinstance(tasks_data, dict):
            tasks_data = {"tasks": {}}
        if "tasks" not in tasks_data:
            tasks_data["tasks"] = {}
        
        tasks_list = []
        for task_id, task in tasks_data["tasks"].items():
            task_info = {
                "task_id": task_id,
                "status": task.get("status", "unknown"),
                "message": task.get("message", ""),
                "result": {
                    "file_path": task.get("file_path"),
                    "file_name": task.get("file_name"),
                    "analysis_file": task.get("analysis_file"),
                    "analysis_json": task.get("analysis_json")
                } if task.get("file_path") else None
            }
            tasks_list.append(task_info)
            
        print(f"返回任务列表: {tasks_list}")  # 添加调试日志
        return tasks_list
        
    except Exception as e:
        print(f"获取任务列表失败: {e}")
        # 出错时也返回空列表，而不是抛出错误
        return []

def start_server():
    """启动服务器"""
    # 加载已有任务数据到全局变量
    global tasks
    tasks = load_tasks()
    print(f"加载已有任务数据: {tasks}")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--reload":
        # 使用reload模式启动（用于开发）
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    else:
        # 普通模式启动
        start_server() 