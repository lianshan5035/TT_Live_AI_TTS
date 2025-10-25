import os
import sys
import time
import asyncio
import pandas as pd
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from batch_tts import process_excel  # 确保 batch_tts.py 内暴露该函数
from tqdm import tqdm

# -----------------------------
# 全局配置
# -----------------------------
INPUT_DIR = "input"
OUTPUT_DIR = "outputs"
LOG_DIR = "logs"
REPORT_FILE = os.path.join(OUTPUT_DIR, "task_report.csv")
MAX_CONCURRENT_TASKS = 10  # 支持 5-10 个并行任务
RETRY_LIMIT = 3

# -----------------------------
# 工具函数
# -----------------------------
def log_message(product, message):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, f"{product}.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def get_product_name_from_filename(filename):
    # 文件格式示例：2025-10-25_Dark_Spot_Patch.xlsx
    base = os.path.basename(filename)
    name = os.path.splitext(base)[0]
    parts = name.split("_", 3)
    return parts[-1] if len(parts) > 1 else name

def discover_tasks():
    os.makedirs(INPUT_DIR, exist_ok=True)
    excel_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".xlsx")]
    return [os.path.join(INPUT_DIR, f) for f in excel_files]

# -----------------------------
# 单任务执行逻辑
# -----------------------------
def run_single_task(file_path):
    product_name = get_product_name_from_filename(file_path)
    start_time = time.time()
    result = {"product_name": product_name, "status": "pending"}

    try:
        log_message(product_name, f"开始处理任务：{file_path}")
        process_excel(file_path)  # 调用批量语音生成函数
        duration = time.time() - start_time
        result.update({
            "status": "success",
            "duration_sec": round(duration, 2)
        })
        log_message(product_name, f"✅ 任务完成，耗时 {duration:.2f}s")
    except Exception as e:
        log_message(product_name, f"❌ 任务失败：{e}")
        result.update({"status": "failed", "error": str(e)})
    return result

# -----------------------------
# 异步任务调度器
# -----------------------------
async def run_tasks_concurrently(task_files):
    loop = asyncio.get_event_loop()
    results = []
    sem = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    async def sem_task(file):
        async with sem:
            for attempt in range(RETRY_LIMIT):
                result = await loop.run_in_executor(None, run_single_task, file)
                if result["status"] == "success":
                    return result
                log_message(result["product_name"], f"重试第 {attempt+1}/{RETRY_LIMIT} 次...")
                time.sleep(3)
            return result

    with tqdm(total=len(task_files), desc="🎧 任务进度", ncols=100) as pbar:
        tasks = [asyncio.create_task(sem_task(f)) for f in task_files]
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            pbar.update(1)
    return results

# -----------------------------
# 报告生成
# -----------------------------
def generate_report(results):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(REPORT_FILE, index=False, encoding="utf-8-sig")

    success = len(df[df["status"] == "success"])
    failed = len(df[df["status"] == "failed"])
    avg_time = round(df["duration_sec"].mean(), 2) if success else 0

    print("\n📊 任务报告汇总")
    print("=" * 40)
    print(f"总任务数：{len(df)}")
    print(f"成功：{success}")
    print(f"失败：{failed}")
    print(f"平均耗时：{avg_time}s")
    print(f"报告文件：{REPORT_FILE}")
    print("=" * 40)

# -----------------------------
# 命令行控制逻辑
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="TT-Live-AI 多产品任务控制器")
    parser.add_argument("command", choices=["run", "status", "retry", "report"], help="操作命令")
    parser.add_argument("arg", nargs="?", default="all", help="参数（如产品名）")
    args = parser.parse_args()

    if args.command == "run":
        print(f"\n🚀 启动任务：{args.arg}\n")
        all_tasks = discover_tasks()
        if not all_tasks:
            print("⚠️ 未在 input/ 目录中发现 Excel 文件")
            return

        if args.arg != "all":
            all_tasks = [t for t in all_tasks if args.arg in t]
            if not all_tasks:
                print(f"❌ 未找到匹配产品 {args.arg}")
                return

        asyncio.run(async_run(all_tasks))

    elif args.command == "status":
        if os.path.exists(REPORT_FILE):
            df = pd.read_csv(REPORT_FILE)
            print("\n📊 当前任务状态：")
            print(df[["product_name", "status", "duration_sec"]])
        else:
            print("📂 暂无报告文件，请先运行任务。")

    elif args.command == "retry":
        if not os.path.exists(REPORT_FILE):
            print("⚠️ 无报告文件，无法重试。")
            return
        df = pd.read_csv(REPORT_FILE)
        failed_files = [os.path.join(INPUT_DIR, f"{p}.xlsx")
                        for p in df[df["status"] == "failed"]["product_name"]]
        if not failed_files:
            print("🎉 没有失败任务！")
            return
        asyncio.run(async_run(failed_files))

    elif args.command == "report":
        if os.path.exists(REPORT_FILE):
            df = pd.read_csv(REPORT_FILE)
            print("\n📈 全部任务报告：")
            print(df)
        else:
            print("📁 尚未生成报告。")

async def async_run(task_files):
    results = await run_tasks_concurrently(task_files)
    generate_report(results)

if __name__ == "__main__":
    main()