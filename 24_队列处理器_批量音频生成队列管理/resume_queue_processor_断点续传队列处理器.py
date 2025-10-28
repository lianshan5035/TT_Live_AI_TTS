#!/usr/bin/env python3
"""
TT-Live-AI 断点续传队列处理器
支持断点续传，避免重复生成已有文件，从上次停止的地方继续
"""
import os
import glob
import requests
import pandas as pd
import time
import logging
from datetime import datetime
import json
import pickle

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('19_日志文件_系统运行日志和错误记录/resume_queue_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
TTS_SERVICE_URL = "http://127.0.0.1:5001"
INPUTS_DIR = "18_批量输入_批量文件输入目录"
OUTPUTS_DIR = "outputs"
BATCH_SIZE = 80  # 每批处理的脚本数量 (平衡性能和稳定性)
BATCH_DELAY = 2  # 批次间延迟（秒）(给API恢复时间)
FILE_DELAY = 5   # 文件间延迟（秒）(给系统缓冲时间)
PROGRESS_FILE = "19_日志文件_系统运行日志和错误记录/processing_progress.pkl"  # 进度保存文件

# 为每个文件定义固定的voice
FILE_VOICE_MAPPING = {
    "全产品_合并版_3200_v9.xlsx": "en-US-JennyNeural",
    "全产品_合并版_3200_v8.xlsx": "en-US-AriaNeural", 
    "全产品_合并版_3200_v7.xlsx": "en-US-MichelleNeural",
    "全产品_合并版_3200_v6.xlsx": "en-US-BrandonNeural",
    "全产品_合并版_3200_v5.xlsx": "en-US-AvaNeural",
    "全产品_合并版_3200_v4.xlsx": "en-US-NancyNeural",
    "全产品_合并版_3200_v3.xlsx": "en-US-KaiNeural",
    "全产品_合并版_3200_v2.xlsx": "en-US-SerenaNeural",
    "全产品_合并版_3200.xlsx": "en-US-EmmaNeural"
}

class ResumeQueueProcessor:
    def __init__(self):
        self.processed_files = []
        self.failed_files = []
        self.total_audios_generated = 0
        self.total_audios_failed = 0
        self.start_time = None
        self.progress = self.load_progress()
        
    def load_progress(self):
        """加载处理进度"""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'rb') as f:
                    progress = pickle.load(f)
                logger.info(f"📂 加载处理进度: {progress}")
                return progress
            except Exception as e:
                logger.warning(f"⚠️ 加载进度失败: {e}")
        
        return {
            "current_file_index": 0,
            "current_batch_index": 0,
            "completed_files": [],
            "completed_batches": {},
            "total_generated": 0,
            "total_failed": 0
        }
    
    def save_progress(self):
        """保存处理进度"""
        try:
            progress_data = {
                "current_file_index": self.progress["current_file_index"],
                "current_batch_index": self.progress["current_batch_index"],
                "completed_files": self.progress["completed_files"],
                "completed_batches": self.progress["completed_batches"],
                "total_generated": self.total_audios_generated,
                "total_failed": self.total_audios_failed,
                "last_update": datetime.now().isoformat()
            }
            
            with open(PROGRESS_FILE, 'wb') as f:
                pickle.dump(progress_data, f)
            
            logger.info(f"💾 进度已保存: 文件 {self.progress['current_file_index']+1}, 批次 {self.progress['current_batch_index']+1}")
        except Exception as e:
            logger.error(f"❌ 保存进度失败: {e}")
    
    def check_tts_service(self):
        """检查TTS服务状态"""
        try:
            response = requests.get(f"{TTS_SERVICE_URL}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ TTS服务状态正常")
                return True
            else:
                logger.error(f"❌ TTS服务状态异常: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ 无法连接到TTS服务: {e}")
            return False
    
    def scan_input_files(self):
        """扫描inputs文件夹中的xlsx文件"""
        xlsx_files = glob.glob(os.path.join(INPUTS_DIR, "*.xlsx"))
        logger.info(f"📁 发现 {len(xlsx_files)} 个xlsx文件:")
        for i, file in enumerate(xlsx_files):
            file_name = os.path.basename(file)
            voice = FILE_VOICE_MAPPING.get(file_name, "en-US-JennyNeural")
            status = "✅ 已完成" if file_name in self.progress["completed_files"] else "⏳ 待处理"
            logger.info(f"  {i+1}. {file_name} -> {voice} ({status})")
        return xlsx_files
    
    def read_excel_file(self, file_path):
        """读取Excel文件"""
        try:
            df = pd.read_excel(file_path)
            logger.info(f"✅ 成功读取: {os.path.basename(file_path)} - {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"❌ 读取失败: {os.path.basename(file_path)} - {e}")
            return None
    
    def prepare_scripts_data(self, df, file_name):
        """准备脚本数据"""
        scripts = []
        
        # 检查必要的列 - 支持多种字段名
        english_script_col = None
        for col in ['英文', 'english_script', 'English', 'english']:
            if col in df.columns:
                english_script_col = col
                break
        
        if not english_script_col:
            logger.error(f"❌ 未找到英文脚本列，可用列: {list(df.columns)}")
            return []
        
        logger.info(f"✅ 使用英文脚本列: {english_script_col}")
        
        # 获取文件固定的voice
        fixed_voice = FILE_VOICE_MAPPING.get(file_name, "en-US-JennyNeural")
        logger.info(f"🎤 文件 {file_name} 使用固定语音: {fixed_voice}")
        
        for index, row in df.iterrows():
            # 获取英文脚本内容
            english_script = str(row[english_script_col]).strip()
            if not english_script or english_script.lower() in ['nan', 'none', '']:
                continue  # 跳过空内容
            
            script = {
                "english_script": english_script,
                "emotion": "Friendly",  # 默认情绪
                "voice": fixed_voice  # 使用文件固定的voice
            }
            
            # 获取情绪参数
            if "情绪类型" in df.columns and pd.notna(row["情绪类型"]):
                emotion_map = {
                    "紧迫型": "Urgent",
                    "兴奋型": "Excited", 
                    "友好型": "Friendly",
                    "自信型": "Confident",
                    "平静型": "Calm"
                }
                emotion_type = str(row["情绪类型"]).strip()
                script["emotion"] = emotion_map.get(emotion_type, "Friendly")
            
            # 获取语音参数
            if "rate" in df.columns and pd.notna(row["rate"]):
                script["rate"] = float(row["rate"])
            if "pitch" in df.columns and pd.notna(row["pitch"]):
                script["pitch"] = float(row["pitch"])
            if "volume" in df.columns and pd.notna(row["volume"]):
                script["volume"] = float(row["volume"])
            
            # 获取产品信息
            if "产品" in df.columns and pd.notna(row["产品"]):
                script["product"] = str(row["产品"]).strip()
            if "类目" in df.columns and pd.notna(row["类目"]):
                script["category"] = str(row["类目"]).strip()
            
            # 获取中文翻译
            if "中文" in df.columns and pd.notna(row["中文"]):
                script["chinese_translation"] = str(row["中文"]).strip()
            
            # 获取CTA信息
            if "CTA" in df.columns and pd.notna(row["CTA"]):
                script["cta"] = str(row["CTA"]).strip()
            
            scripts.append(script)
        
        logger.info(f"✅ 准备了 {len(scripts)} 条脚本数据")
        return scripts
    
    def check_batch_completion(self, product_name, batch_num):
        """检查批次是否已完成"""
        # 使用统一的文件夹名称（不包含Batch信息）
        unified_dir = f"20_输出文件_处理完成的音频文件/{product_name}_{self.get_voice_name(product_name)}"
        
        if not os.path.exists(unified_dir):
            return False
        
        # 检查是否有足够的音频文件（基于批次号计算）
        mp3_files = glob.glob(os.path.join(unified_dir, "*.mp3"))
        expected_files = batch_num * BATCH_SIZE
        return len(mp3_files) >= expected_files
    
    def get_voice_name(self, product_name):
        """获取语音名称"""
        file_name = f"{product_name}.xlsx"
        voice = FILE_VOICE_MAPPING.get(file_name, "en-US-JennyNeural")
        return voice.replace("en-US-", "").replace("Neural", "")
    
    def generate_audio_batch(self, scripts, product_name, batch_num, batch_size=BATCH_SIZE):
        """批量生成音频"""
        total_scripts = len(scripts)
        successful = 0
        failed = 0
        
        # 检查批次是否已完成
        if self.check_batch_completion(product_name, batch_num):
            logger.info(f"⏭️ 批次 {batch_num} 已完成，跳过")
            return BATCH_SIZE, 0
        
        logger.info(f"🚀 开始生成批次 {batch_num}，包含 {batch_size} 条脚本")
        
        # 准备请求数据
        request_data = {
            "product_name": f"{product_name}_Batch{batch_num}",
            "scripts": scripts,
            "emotion": "Friendly",
            "voice": scripts[0]["voice"] if scripts else "en-US-JennyNeural"
        }
        
        try:
            # 发送请求
            logger.info(f"📡 发送批次 {batch_num} 请求到TTS服务...")
            logger.info(f"🎤 使用语音: {request_data['voice']}")
            
            response = requests.post(f"{TTS_SERVICE_URL}/generate", json=request_data, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                batch_successful = result["summary"]["successful"]
                batch_failed = result["summary"]["failed"]
                
                successful += batch_successful
                failed += batch_failed
                
                logger.info(f"✅ 批次 {batch_num} 完成: 成功 {batch_successful}, 失败 {batch_failed}")
                logger.info(f"📁 音频目录: {result['audio_directory']}")
                
                # 显示进度
                progress = ((batch_num - 1) * batch_size + batch_successful) / total_scripts * 100
                logger.info(f"📊 文件进度: {progress:.1f}% ({batch_successful}/{total_scripts})")
                
                # 显示预计剩余时间
                if self.start_time:
                    elapsed_time = time.time() - self.start_time
                    if self.total_audios_generated + batch_successful > 0:
                        avg_time_per_audio = elapsed_time / (self.total_audios_generated + batch_successful)
                        remaining_audios = total_scripts - (batch_num * batch_size)
                        estimated_remaining = remaining_audios * avg_time_per_audio
                        logger.info(f"⏱️ 预计剩余时间: {estimated_remaining/60:.1f} 分钟")
                
            else:
                logger.error(f"❌ 批次 {batch_num} 请求失败: {response.status_code}")
                logger.error(f"响应内容: {response.text}")
                failed += batch_size
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 批次 {batch_num} 请求异常: {e}")
            failed += batch_size
        
        return successful, failed
    
    def process_single_file(self, file_path, file_index):
        """处理单个xlsx文件"""
        file_name = os.path.basename(file_path)
        logger.info(f"🔄 开始处理文件 {file_index+1}/9: {file_name}")
        
        # 检查文件是否已完成
        if file_name in self.progress["completed_files"]:
            logger.info(f"⏭️ 文件 {file_name} 已完成，跳过")
            return True
        
        # 读取Excel文件
        df = self.read_excel_file(file_path)
        if df is None:
            self.failed_files.append(file_name)
            return False
        
        # 准备脚本数据
        scripts = self.prepare_scripts_data(df, file_name)
        if not scripts:
            logger.error(f"❌ 没有可用的脚本数据: {file_name}")
            self.failed_files.append(file_name)
            return False
        
        # 生成产品名称（去掉扩展名）
        product_name = os.path.splitext(file_name)[0]
        
        # 计算总批次数
        total_batches = (len(scripts) + BATCH_SIZE - 1) // BATCH_SIZE
        
        # 从上次停止的批次开始
        start_batch = self.progress["current_batch_index"] if file_index == self.progress["current_file_index"] else 0
        
        logger.info(f"📊 文件 {file_name}: {len(scripts)} 条脚本，{total_batches} 个批次")
        logger.info(f"🔄 从批次 {start_batch + 1} 开始处理")
        
        # 开始生成音频
        file_start_time = time.time()
        file_successful = 0
        file_failed = 0
        
        for batch_num in range(start_batch + 1, total_batches + 1):
            batch_start = (batch_num - 1) * BATCH_SIZE
            batch_end = min(batch_start + BATCH_SIZE, len(scripts))
            batch_scripts = scripts[batch_start:batch_end]
            
            logger.info(f"📦 处理批次 {batch_num}/{total_batches}，脚本 {batch_start+1}-{batch_end}")
            
            successful, failed = self.generate_audio_batch(batch_scripts, product_name, batch_num)
            
            file_successful += successful
            file_failed += failed
            self.total_audios_generated += successful
            self.total_audios_failed += failed
            
            # 更新进度
            self.progress["current_file_index"] = file_index
            self.progress["current_batch_index"] = batch_num - 1
            
            # 标记批次完成
            if successful > 0:
                batch_key = f"{file_name}_batch_{batch_num}"
                self.progress["completed_batches"][batch_key] = {
                    "successful": successful,
                    "failed": failed,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 保存进度
            self.save_progress()
            
            # 批次间暂停
            if batch_num < total_batches:
                logger.info(f"⏳ 批次间暂停 {BATCH_DELAY} 秒...")
                time.sleep(BATCH_DELAY)
        
        file_end_time = time.time()
        file_duration = file_end_time - file_start_time
        
        # 标记文件完成
        if file_successful > 0:
            self.progress["completed_files"].append(file_name)
            self.progress["current_file_index"] = file_index + 1
            self.progress["current_batch_index"] = 0
        
        logger.info(f"✅ 文件处理完成: {file_name}")
        logger.info(f"  - 成功生成: {file_successful} 个音频文件")
        logger.info(f"  - 生成失败: {file_failed} 个")
        logger.info(f"  - 耗时: {file_duration/60:.1f} 分钟")
        
        self.processed_files.append({
            "file": file_name,
            "successful": file_successful,
            "failed": file_failed,
            "duration": file_duration,
            "voice": scripts[0]["voice"] if scripts else "unknown"
        })
        
        return True
    
    def process_all_files(self):
        """处理所有xlsx文件"""
        logger.info("🎵 开始断点续传处理inputs文件夹中的xlsx文件")
        logger.info("=" * 80)
        
        # 检查TTS服务
        if not self.check_tts_service():
            logger.error("❌ TTS服务不可用，无法继续处理")
            return False
        
        # 扫描输入文件
        xlsx_files = self.scan_input_files()
        if not xlsx_files:
            logger.info("📁 inputs文件夹中没有xlsx文件")
            return False
        
        # 记录开始时间
        self.start_time = time.time()
        
        # 从上次停止的文件开始处理
        start_file_index = self.progress["current_file_index"]
        logger.info(f"🔄 从文件 {start_file_index + 1} 开始处理")
        
        # 处理每个文件
        success_count = 0
        for i, file_path in enumerate(xlsx_files):
            if i < start_file_index:
                logger.info(f"⏭️ 跳过已完成文件 {i+1}: {os.path.basename(file_path)}")
                continue
            
            file_name = os.path.basename(file_path)
            logger.info(f"📁 处理文件 {i+1}/{len(xlsx_files)}: {file_name}")
            
            if self.process_single_file(file_path, i):
                success_count += 1
            
            # 文件间暂停
            if i < len(xlsx_files) - 1:  # 不是最后一个文件
                logger.info(f"⏳ 文件间暂停 {FILE_DELAY} 秒...")
                time.sleep(FILE_DELAY)
        
        end_time = time.time()
        total_duration = end_time - self.start_time
        
        # 生成最终报告
        self.generate_final_report(total_duration, success_count, len(xlsx_files))
        
        return success_count == len(xlsx_files)
    
    def generate_final_report(self, total_duration, success_count, total_files):
        """生成最终处理报告"""
        logger.info("=" * 80)
        logger.info("🎉 断点续传处理完成!")
        logger.info(f"📊 处理统计:")
        logger.info(f"  - 处理文件数: {total_files}")
        logger.info(f"  - 成功文件数: {success_count}")
        logger.info(f"  - 失败文件数: {total_files - success_count}")
        logger.info(f"  - 总音频生成: {self.total_audios_generated}")
        logger.info(f"  - 总音频失败: {self.total_audios_failed}")
        logger.info(f"  - 总耗时: {total_duration/3600:.1f} 小时")
        
        if self.processed_files:
            logger.info(f"📁 处理结果:")
            for file_info in self.processed_files:
                logger.info(f"  - {file_info['file']}: {file_info['successful']} 成功, {file_info['failed']} 失败, 语音: {file_info['voice']}, 耗时: {file_info['duration']/60:.1f}分钟")
        
        if self.failed_files:
            logger.info(f"❌ 失败的文件:")
            for file_name in self.failed_files:
                logger.info(f"  - {file_name}")
        
        # 保存报告到文件
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "success_count": success_count,
            "total_files": total_files,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "total_audios_generated": self.total_audios_generated,
            "total_audios_failed": self.total_audios_failed,
            "voice_mapping": FILE_VOICE_MAPPING,
            "progress": self.progress
        }
        
        report_file = f"19_日志文件_系统运行日志和错误记录/resume_queue_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 详细报告已保存: {report_file}")
        
        # 判断处理是否成功
        if success_count == total_files and self.total_audios_failed == 0:
            logger.info("🎉 所有文件处理成功！")
            return True
        else:
            logger.warning("⚠️ 部分文件处理失败，请检查日志。")
            return False

def main():
    """主函数"""
    processor = ResumeQueueProcessor()
    success = processor.process_all_files()
    
    if success:
        logger.info("✅ 所有文件处理成功！")
    else:
        logger.error("❌ 部分文件处理失败")

if __name__ == "__main__":
    main()
