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

# 存储任务状态的字典
task_status = {}
# 存储任务结果的字典
task_results = {}

# 添加任务存储相关的常量
TASKS_FILE = "tasks.json"
TASKS_DIR = Path("tasks")
TASKS_DIR.mkdir(exist_ok=True)

def load_tasks():
    """从文件加载任务数据"""
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                task_status.update(data.get('status', {}))
                task_results.update(data.get('results', {}))
    except Exception as e:
        print(f"加载任务数据失败: {e}")

def save_tasks():
    """保存任务数据到文件"""
    try:
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'status': task_status,
                'results': task_results
            }, f, ensure_ascii=False, indent=2)
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
        task_status[task_id] = {"status": "running", "message": "正在爬取数据..."}
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
                
                task_results[task_id] = {
                    "status": "completed",
                    "message": "数据爬取完成",
                    "file_path": file_path,
                    "file_name": latest_file
                }
                save_tasks()  # 保存任务结果
            except Exception as e:
                task_results[task_id] = {
                    "status": "failed",
                    "message": f"爬取失败: {str(e)}",
                    "error": str(e)
                }
        
        # 启动爬虫线程
        thread = threading.Thread(target=run_crawler)
        thread.start()
        
    except Exception as e:
        task_status[task_id] = {
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
    if task_id not in task_status and task_id not in task_results:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 如果任务已完成，返回结果
    if task_id in task_results:
        result = task_results[task_id]
        return TaskStatus(
            task_id=task_id,
            status=result["status"],
            message=result["message"],
            result=result
        )
    
    # 否则返回当前状态
    status = task_status[task_id]
    return TaskStatus(
        task_id=task_id,
        status=status["status"],
        message=status["message"]
    )

@app.get("/api/download/{task_id}")
async def download_file(task_id: str, type: str = 'raw'):
    """下载文件
    type: 'raw' 原始数据文件, 'analysis' 分析结果文件
    """
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = task_results[task_id]
    
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
    if task_id not in task_status and task_id not in task_results:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 如果任务有关联文件，删除文件
    if task_id in task_results:
        result = task_results[task_id]
        # 删除原始数据文件
        if result.get("file_path") and os.path.exists(result["file_path"]):
            try:
                os.remove(result["file_path"])
            except Exception as e:
                print(f"删除原始文件失败: {e}")
        
        # 删除分析结果文件
        if result.get("analysis_file") and os.path.exists(result["analysis_file"]):
            try:
                os.remove(result["analysis_file"])
            except Exception as e:
                print(f"删除分析文件失败: {e}")
    
    # 从状态字典中删除任务
    if task_id in task_status:
        del task_status[task_id]
    if task_id in task_results:
        del task_results[task_id]
    
    # 保存更新后的任务数据
    save_tasks()
    
    return {"message": "任务已删除"}

@app.post("/api/analyze")
async def start_analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """启动数据分析任务"""
    if request.task_id not in task_results:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = task_results[request.task_id]
    if result["status"] != "completed":
        raise HTTPException(status_code=400, detail="只能分析已完成的任务")
    
    if not result.get("file_path") or not os.path.exists(result["file_path"]):
        raise HTTPException(status_code=404, detail="数据文件不存在")
    
    # 更新任务状态为分析中
    result["status"] = "analyzing"
    result["message"] = "正在进行数据分析..."
    save_tasks()
    
    # 启动分析任务
    async def run_analyze():
        try:
            # 执行数据分析
            output_file = analyze_data(result["file_path"], strategy=request.strategy)
            
            # 执行1688识图
            analyze_1688(output_file)
            
            # 更新任务状态
            result["status"] = "completed"
            result["message"] = "分析完成"
            result["analysis_file"] = output_file
            save_tasks()
            
        except Exception as e:
            result["status"] = "failed"
            result["message"] = f"分析失败: {str(e)}"
            save_tasks()
    
    background_tasks.add_task(run_analyze)
    
    return {"message": "分析任务已启动"}

def start_server():
    """启动服务器"""
    load_tasks()  # 加载已有任务数据
    uvicorn.run(
        app, 
        host="0.0.0.0",  # 修改为监听所有地址
        port=8000,
        reload=True  # 开发模式下启用热重载
    )

if __name__ == "__main__":
    start_server() 