import os
import time
import subprocess

print("🚀 启动 TT-Live-AI 自动控制系统...")
os.chdir("/Volumes/M2/TT_Live_AI_TTS")

# 自动安装依赖（如无 requirements.txt 可注释掉）
subprocess.run("pip install -r requirements.txt", shell=True)

# 启动主程序
print("▶️ 正在运行 web_dashboard.py 控制中心...")
subprocess.run("python web_dashboard.py", shell=True)

# 持续监听运行状态
while True:
    print("💡 控制中心持续运行中...按 Ctrl+C 退出")
    time.sleep(600)
