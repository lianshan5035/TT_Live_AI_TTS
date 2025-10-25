#!/usr/bin/env python3
"""
TT-Live-AI A3-TK 口播生成系统 - 多产品任务管理器
支持多产品并行处理、任务队列管理、进度监控、CLI 控制界面
"""
import os
import json
import asyncio
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import logging
import argparse
import sys
from pathlib import Path

# 导入本地模块
from run_tts import process_scripts_batch, generate_excel_output, EMOTION_PARAMS, DEFAULT_VOICE, MAX_CONCURRENT
from batch_tts import process_excel_file

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/task_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Task:
    """任务数据结构"""
    task_id: str
    product_name: str
    discount: str
    scripts: List[Dict[str, Any]]
    status: str = "pending"  # pending, running, completed, failed, paused
    progress: int = 0
    total_scripts: int = 0
    successful: int = 0
    failed: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    output_excel: str = ""
    audio_directory: str = ""
    error_message: str = ""
    
    def to_dict(self):
        return asdict(self)

class TaskQueue:
    """任务队列管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_file = "logs/task_queue.json"
        self.load_tasks()
    
    def add_task(self, task: Task):
        """添加任务到队列"""
        self.tasks[task.task_id] = task
        self.save_tasks()
        logger.info(f"✅ 任务已添加到队列: {task.task_id} - {task.product_name}")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def update_task(self, task: Task):
        """更新任务状态"""
        self.tasks[task.task_id] = task
        self.save_tasks()
    
    def get_pending_tasks(self) -> List[Task]:
        """获取待处理任务"""
        return [task for task in self.tasks.values() if task.status == "pending"]
    
    def get_running_tasks(self) -> List[Task]:
        """获取运行中任务"""
        return [task for task in self.tasks.values() if task.status == "running"]
    
    def get_failed_tasks(self) -> List[Task]:
        """获取失败任务"""
        return [task for task in self.tasks.values() if task.status == "failed"]
    
    def get_completed_tasks(self) -> List[Task]:
        """获取已完成任务"""
        return [task for task in self.tasks.values() if task.status == "completed"]
    
    def save_tasks(self):
        """保存任务到文件"""
        try:
            os.makedirs(os.path.dirname(self.task_file), exist_ok=True)
            with open(self.task_file, 'w', encoding='utf-8') as f:
                json.dump({tid: task.to_dict() for tid, task in self.tasks.items()}, 
                         f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"保存任务失败: {str(e)}")
    
    def load_tasks(self):
        """从文件加载任务"""
        try:
            if os.path.exists(self.task_file):
                with open(self.task_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for tid, task_data in data.items():
                        # 转换 datetime 字符串
                        if task_data.get('start_time'):
                            task_data['start_time'] = datetime.fromisoformat(task_data['start_time'])
                        if task_data.get('end_time'):
                            task_data['end_time'] = datetime.fromisoformat(task_data['end_time'])
                        self.tasks[tid] = Task(**task_data)
        except Exception as e:
            logger.error(f"加载任务失败: {str(e)}")

class WorkerPool:
    """工作池管理器"""
    
    def __init__(self, max_workers: int = MAX_CONCURRENT):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_workers = {}
        self.is_paused = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # 初始状态为运行
    
    async def process_task(self, task: Task) -> Task:
        """处理单个任务"""
        try:
            task.status = "running"
            task.start_time = datetime.now()
            task.total_scripts = len(task.scripts)
            
            logger.info(f"🚀 开始处理任务: {task.task_id} - {task.product_name}")
            
            # 异步处理脚本
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    process_scripts_batch(task.scripts, task.product_name, task.discount)
                )
            finally:
                loop.close()
            
            # 生成 Excel 输出
            excel_path = generate_excel_output(
                task.scripts, task.product_name, task.discount, result["results"]
            )
            
            # 更新任务状态
            task.status = "completed"
            task.end_time = datetime.now()
            task.duration_seconds = (task.end_time - task.start_time).total_seconds()
            task.successful = result["successful"]
            task.failed = result["failed"]
            task.output_excel = excel_path
            task.audio_directory = f"outputs/{task.product_name}/"
            task.progress = 100
            
            logger.info(f"✅ 任务完成: {task.task_id} - 成功: {task.successful}, 失败: {task.failed}")
            
        except Exception as e:
            task.status = "failed"
            task.end_time = datetime.now()
            task.error_message = str(e)
            logger.error(f"❌ 任务失败: {task.task_id} - {str(e)}")
        
        return task
    
    def pause(self):
        """暂停工作池"""
        self.is_paused = True
        self.pause_event.clear()
        logger.info("⏸️ 工作池已暂停")
    
    def resume(self):
        """恢复工作池"""
        self.is_paused = False
        self.pause_event.set()
        logger.info("▶️ 工作池已恢复")
    
    def shutdown(self):
        """关闭工作池"""
        self.executor.shutdown(wait=True)
        logger.info("🛑 工作池已关闭")

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """生成汇总报告"""
        all_tasks = list(self.task_queue.tasks.values())
        
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.status == "completed"])
        failed_tasks = len([t for t in all_tasks if t.status == "failed"])
        running_tasks = len([t for t in all_tasks if t.status == "running"])
        pending_tasks = len([t for t in all_tasks if t.status == "pending"])
        
        total_scripts = sum(t.total_scripts for t in all_tasks)
        total_successful = sum(t.successful for t in all_tasks)
        total_failed = sum(t.failed for t in all_tasks)
        
        avg_duration = sum(t.duration_seconds for t in all_tasks if t.duration_seconds > 0)
        if completed_tasks > 0:
            avg_duration /= completed_tasks
        
        return {
            "report_time": datetime.now().isoformat(),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "pending_tasks": pending_tasks,
            "total_scripts": total_scripts,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "success_rate": (total_successful / total_scripts * 100) if total_scripts > 0 else 0,
            "avg_duration_seconds": avg_duration
        }
    
    def generate_detailed_report(self) -> List[Dict[str, Any]]:
        """生成详细报告"""
        report_data = []
        for task in self.task_queue.tasks.values():
            report_data.append({
                "task_id": task.task_id,
                "product_name": task.product_name,
                "status": task.status,
                "total_scripts": task.total_scripts,
                "successful": task.successful,
                "failed": task.failed,
                "duration_seconds": task.duration_seconds,
                "output_excel": task.output_excel,
                "start_time": task.start_time.isoformat() if task.start_time else "",
                "end_time": task.end_time.isoformat() if task.end_time else "",
                "error_message": task.error_message
            })
        return report_data
    
    def save_reports(self):
        """保存报告到文件"""
        try:
            # 生成汇总报告
            summary = self.generate_summary_report()
            summary_file = "logs/summary_report.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            # 生成详细报告
            detailed = self.generate_detailed_report()
            detailed_file = "logs/detailed_report.json"
            with open(detailed_file, 'w', encoding='utf-8') as f:
                json.dump(detailed, f, indent=2, ensure_ascii=False)
            
            # 生成 CSV 报告
            if detailed:
                df = pd.DataFrame(detailed)
                csv_file = "logs/task_report.csv"
                df.to_csv(csv_file, index=False, encoding='utf-8')
            
            logger.info("📊 报告已保存到 logs/ 目录")
            
        except Exception as e:
            logger.error(f"保存报告失败: {str(e)}")

class MultiProductManager:
    """多产品任务管理器"""
    
    def __init__(self):
        self.task_queue = TaskQueue()
        self.worker_pool = WorkerPool()
        self.report_generator = ReportGenerator(self.task_queue)
        self.is_running = False
        self.worker_thread = None
    
    def add_product_task(self, product_name: str, discount: str, scripts: List[Dict[str, Any]]):
        """添加产品任务"""
        task_id = f"{product_name}_{int(time.time())}"
        task = Task(
            task_id=task_id,
            product_name=product_name,
            discount=discount,
            scripts=scripts,
            total_scripts=len(scripts)
        )
        self.task_queue.add_task(task)
        return task_id
    
    def add_excel_task(self, excel_file: str, product_name: str = None):
        """从 Excel 文件添加任务"""
        try:
            df = pd.read_excel(excel_file)
            scripts = []
            for _, row in df.iterrows():
                scripts.append({
                    "english_script": row.get('english_script', ''),
                    "chinese_translation": row.get('chinese_translation', ''),
                    "emotion": row.get('emotion', 'Friendly'),
                    "voice": row.get('voice', DEFAULT_VOICE)
                })
            
            if not product_name:
                product_name = os.path.splitext(os.path.basename(excel_file))[0]
            
            return self.add_product_task(product_name, "Excel Import", scripts)
            
        except Exception as e:
            logger.error(f"添加 Excel 任务失败: {str(e)}")
            return None
    
    def start_processing(self):
        """开始处理任务"""
        if self.is_running:
            logger.warning("⚠️ 任务处理器已在运行")
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        logger.info("🚀 任务处理器已启动")
    
    def stop_processing(self):
        """停止处理任务"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join()
        logger.info("🛑 任务处理器已停止")
    
    def _process_worker(self):
        """工作线程"""
        while self.is_running:
            try:
                # 等待暂停状态
                self.worker_pool.pause_event.wait()
                
                # 获取待处理任务
                pending_tasks = self.task_queue.get_pending_tasks()
                if not pending_tasks:
                    time.sleep(1)
                    continue
                
                # 处理任务
                for task in pending_tasks[:self.worker_pool.max_workers]:
                    if not self.is_running:
                        break
                    
                    # 提交任务到工作池
                    future = self.worker_pool.executor.submit(
                        self._run_task, task
                    )
                    self.worker_pool.running_workers[task.task_id] = future
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"工作线程错误: {str(e)}")
                time.sleep(5)
    
    def _run_task(self, task: Task):
        """运行单个任务"""
        try:
            # 异步处理任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.worker_pool.process_task(task)
                )
                self.task_queue.update_task(result)
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"运行任务失败: {task.task_id} - {str(e)}")
            task.status = "failed"
            task.error_message = str(e)
            self.task_queue.update_task(task)
        finally:
            # 从运行中移除
            if task.task_id in self.worker_pool.running_workers:
                del self.worker_pool.running_workers[task.task_id]
    
    def pause_processing(self):
        """暂停处理"""
        self.worker_pool.pause()
    
    def resume_processing(self):
        """恢复处理"""
        self.worker_pool.resume()
    
    def retry_failed_tasks(self):
        """重试失败任务"""
        failed_tasks = self.task_queue.get_failed_tasks()
        for task in failed_tasks:
            task.status = "pending"
            task.error_message = ""
            self.task_queue.update_task(task)
        logger.info(f"🔄 已重置 {len(failed_tasks)} 个失败任务")
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "is_running": self.is_running,
            "is_paused": self.worker_pool.is_paused,
            "max_workers": self.worker_pool.max_workers,
            "running_workers": len(self.worker_pool.running_workers),
            "total_tasks": len(self.task_queue.tasks),
            "pending_tasks": len(self.task_queue.get_pending_tasks()),
            "running_tasks": len(self.task_queue.get_running_tasks()),
            "completed_tasks": len(self.task_queue.get_completed_tasks()),
            "failed_tasks": len(self.task_queue.get_failed_tasks())
        }

class ControllerCLI:
    """命令行控制界面"""
    
    def __init__(self):
        self.manager = MultiProductManager()
        self.setup_parser()
    
    def setup_parser(self):
        """设置命令行参数解析器"""
        self.parser = argparse.ArgumentParser(
            description="TT-Live-AI 多产品任务管理器",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例用法:
  python task_manager.py status                    # 查看状态
  python task_manager.py start                     # 启动处理器
  python task_manager.py stop                      # 停止处理器
  python task_manager.py pause                     # 暂停处理
  python task_manager.py resume                    # 恢复处理
  python task_manager.py add-product "Acne Patch" "20% OFF" --scripts-file scripts.json
  python task_manager.py add-excel input/products.xlsx
  python task_manager.py retry-failed              # 重试失败任务
  python task_manager.py report                    # 生成报告
  python task_manager.py list                      # 列出所有任务
            """
        )
        
        subparsers = self.parser.add_subparsers(dest='command', help='可用命令')
        
        # status 命令
        subparsers.add_parser('status', help='查看系统状态')
        
        # start 命令
        subparsers.add_parser('start', help='启动任务处理器')
        
        # stop 命令
        subparsers.add_parser('stop', help='停止任务处理器')
        
        # pause 命令
        subparsers.add_parser('pause', help='暂停处理')
        
        # resume 命令
        subparsers.add_parser('resume', help='恢复处理')
        
        # add-product 命令
        add_product_parser = subparsers.add_parser('add-product', help='添加产品任务')
        add_product_parser.add_argument('product_name', help='产品名称')
        add_product_parser.add_argument('discount', help='优惠信息')
        add_product_parser.add_argument('--scripts-file', help='脚本文件路径')
        add_product_parser.add_argument('--scripts', help='脚本数量（自动生成）', type=int)
        
        # add-excel 命令
        add_excel_parser = subparsers.add_parser('add-excel', help='从 Excel 文件添加任务')
        add_excel_parser.add_argument('excel_file', help='Excel 文件路径')
        add_excel_parser.add_argument('--product-name', help='产品名称（可选）')
        
        # retry-failed 命令
        subparsers.add_parser('retry-failed', help='重试失败任务')
        
        # report 命令
        subparsers.add_parser('report', help='生成报告')
        
        # list 命令
        list_parser = subparsers.add_parser('list', help='列出任务')
        list_parser.add_argument('--status', choices=['all', 'pending', 'running', 'completed', 'failed'], 
                               default='all', help='任务状态过滤')
    
    def run(self, args=None):
        """运行 CLI"""
        args = self.parser.parse_args(args)
        
        if not args.command:
            self.parser.print_help()
            return
        
        try:
            if args.command == 'status':
                self._show_status()
            elif args.command == 'start':
                self._start_processing()
            elif args.command == 'stop':
                self._stop_processing()
            elif args.command == 'pause':
                self._pause_processing()
            elif args.command == 'resume':
                self._resume_processing()
            elif args.command == 'add-product':
                self._add_product_task(args)
            elif args.command == 'add-excel':
                self._add_excel_task(args)
            elif args.command == 'retry-failed':
                self._retry_failed_tasks()
            elif args.command == 'report':
                self._generate_report()
            elif args.command == 'list':
                self._list_tasks(args)
        except Exception as e:
            logger.error(f"执行命令失败: {str(e)}")
            print(f"❌ 错误: {str(e)}")
    
    def _show_status(self):
        """显示系统状态"""
        status = self.manager.get_status()
        print("\n" + "="*60)
        print("📊 TT-Live-AI 多产品任务管理器状态")
        print("="*60)
        print(f"🔄 处理器状态: {'运行中' if status['is_running'] else '已停止'}")
        print(f"⏸️ 暂停状态: {'已暂停' if status['is_paused'] else '正常运行'}")
        print(f"👥 最大工作线程: {status['max_workers']}")
        print(f"🏃 当前运行线程: {status['running_workers']}")
        print(f"📋 总任务数: {status['total_tasks']}")
        print(f"⏳ 待处理: {status['pending_tasks']}")
        print(f"🏃 运行中: {status['running_tasks']}")
        print(f"✅ 已完成: {status['completed_tasks']}")
        print(f"❌ 失败: {status['failed_tasks']}")
        print("="*60)
    
    def _start_processing(self):
        """启动处理"""
        self.manager.start_processing()
        print("✅ 任务处理器已启动")
    
    def _stop_processing(self):
        """停止处理"""
        self.manager.stop_processing()
        print("🛑 任务处理器已停止")
    
    def _pause_processing(self):
        """暂停处理"""
        self.manager.pause_processing()
        print("⏸️ 处理已暂停")
    
    def _resume_processing(self):
        """恢复处理"""
        self.manager.resume_processing()
        print("▶️ 处理已恢复")
    
    def _add_product_task(self, args):
        """添加产品任务"""
        if args.scripts_file:
            # 从文件读取脚本
            try:
                with open(args.scripts_file, 'r', encoding='utf-8') as f:
                    scripts_data = json.load(f)
                scripts = scripts_data.get('scripts', [])
            except Exception as e:
                print(f"❌ 读取脚本文件失败: {str(e)}")
                return
        elif args.scripts:
            # 自动生成脚本
            scripts = []
            for i in range(args.scripts):
                scripts.append({
                    "english_script": f"Discover the amazing {args.product_name}! {args.discount} Don't miss out!",
                    "chinese_translation": f"发现令人惊叹的{args.product_name}！{args.discount} 不要错过！",
                    "emotion": ["Excited", "Confident", "Friendly", "Playful", "Calm", "Urgent"][i % 6],
                    "voice": DEFAULT_VOICE
                })
        else:
            print("❌ 请指定 --scripts-file 或 --scripts 参数")
            return
        
        task_id = self.manager.add_product_task(args.product_name, args.discount, scripts)
        print(f"✅ 产品任务已添加: {task_id}")
    
    def _add_excel_task(self, args):
        """添加 Excel 任务"""
        if not os.path.exists(args.excel_file):
            print(f"❌ Excel 文件不存在: {args.excel_file}")
            return
        
        task_id = self.manager.add_excel_task(args.excel_file, args.product_name)
        if task_id:
            print(f"✅ Excel 任务已添加: {task_id}")
        else:
            print("❌ 添加 Excel 任务失败")
    
    def _retry_failed_tasks(self):
        """重试失败任务"""
        self.manager.retry_failed_tasks()
        print("🔄 失败任务已重置为待处理状态")
    
    def _generate_report(self):
        """生成报告"""
        self.manager.report_generator.save_reports()
        print("📊 报告已生成并保存到 logs/ 目录")
    
    def _list_tasks(self, args):
        """列出任务"""
        tasks = list(self.manager.task_queue.tasks.values())
        
        if args.status != 'all':
            tasks = [t for t in tasks if t.status == args.status]
        
        if not tasks:
            print("📋 没有找到任务")
            return
        
        print(f"\n📋 任务列表 (状态: {args.status})")
        print("-" * 80)
        print(f"{'任务ID':<20} {'产品名称':<15} {'状态':<10} {'进度':<8} {'成功':<6} {'失败':<6}")
        print("-" * 80)
        
        for task in tasks:
            print(f"{task.task_id:<20} {task.product_name:<15} {task.status:<10} "
                  f"{task.progress}%{'':<4} {task.successful:<6} {task.failed:<6}")

def main():
    """主函数"""
    # 创建必要目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('input', exist_ok=True)
    
    # 启动 CLI
    cli = ControllerCLI()
    cli.run()

if __name__ == '__main__':
    main()
