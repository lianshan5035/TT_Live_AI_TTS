#!/usr/bin/env python3
"""
TT-Live-AI 完整队列处理器
生成每个xlsx文件的完整3200条语音，每个文件使用固定voice
"""
import os
import glob
import requests
import pandas as pd
import time
import logging
from datetime import datetime
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/full_queue_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
TTS_SERVICE_URL = "http://127.0.0.1:5001"
INPUTS_DIR = "inputs"
OUTPUTS_DIR = "outputs"
BATCH_SIZE = 50  # 每批处理的脚本数量
BATCH_DELAY = 3  # 批次间延迟（秒）
FILE_DELAY = 10  # 文件间延迟（秒）

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

class FullQueueProcessor:
    def __init__(self):
        self.processed_files = []
        self.failed_files = []
        self.total_audios_generated = 0
        self.total_audios_failed = 0
        self.start_time = None
        
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
        for file in xlsx_files:
            file_name = os.path.basename(file)
            voice = FILE_VOICE_MAPPING.get(file_name, "en-US-JennyNeural")
            logger.info(f"  - {file_name} -> {voice}")
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
    
    def generate_audio_batch(self, scripts, product_name, batch_size=BATCH_SIZE):
        """批量生成音频"""
        total_scripts = len(scripts)
        successful = 0
        failed = 0
        
        logger.info(f"🚀 开始生成 {total_scripts} 条音频，批量大小: {batch_size}")
        
        for i in range(0, total_scripts, batch_size):
            batch_scripts = scripts[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_scripts + batch_size - 1) // batch_size
            
            logger.info(f"📦 处理第 {batch_num}/{total_batches} 批，包含 {len(batch_scripts)} 条脚本")
            
            # 准备请求数据
            request_data = {
                "product_name": f"{product_name}_Batch{batch_num}",
                "scripts": batch_scripts,
                "emotion": "Friendly",
                "voice": batch_scripts[0]["voice"] if batch_scripts else "en-US-JennyNeural"
            }
            
            try:
                # 发送请求
                logger.info(f"📡 发送第 {batch_num} 批请求到TTS服务...")
                logger.info(f"🎤 使用语音: {request_data['voice']}")
                
                response = requests.post(f"{TTS_SERVICE_URL}/generate", json=request_data, timeout=300)
                
                if response.status_code == 200:
                    result = response.json()
                    batch_successful = result["summary"]["successful"]
                    batch_failed = result["summary"]["failed"]
                    
                    successful += batch_successful
                    failed += batch_failed
                    
                    logger.info(f"✅ 第 {batch_num} 批完成: 成功 {batch_successful}, 失败 {batch_failed}")
                    logger.info(f"📁 音频目录: {result['audio_directory']}")
                    
                    # 显示进度
                    progress = ((i + len(batch_scripts)) / total_scripts) * 100
                    logger.info(f"📊 总进度: {progress:.1f}% ({successful + failed}/{total_scripts})")
                    
                    # 显示预计剩余时间
                    if self.start_time:
                        elapsed_time = time.time() - self.start_time
                        if successful + failed > 0:
                            avg_time_per_audio = elapsed_time / (successful + failed)
                            remaining_audios = total_scripts - (successful + failed)
                            estimated_remaining = remaining_audios * avg_time_per_audio
                            logger.info(f"⏱️ 预计剩余时间: {estimated_remaining/60:.1f} 分钟")
                    
                else:
                    logger.error(f"❌ 第 {batch_num} 批请求失败: {response.status_code}")
                    logger.error(f"响应内容: {response.text}")
                    failed += len(batch_scripts)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ 第 {batch_num} 批请求异常: {e}")
                failed += len(batch_scripts)
            
            # 批次间暂停，避免过载
            if i + batch_size < total_scripts:
                logger.info(f"⏳ 批次间暂停 {BATCH_DELAY} 秒...")
                time.sleep(BATCH_DELAY)
        
        return successful, failed
    
    def process_single_file(self, file_path):
        """处理单个xlsx文件"""
        file_name = os.path.basename(file_path)
        logger.info(f"🔄 开始处理文件: {file_name}")
        
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
        
        # 开始生成音频
        file_start_time = time.time()
        successful, failed = self.generate_audio_batch(scripts, product_name)
        file_end_time = time.time()
        
        # 统计结果
        file_duration = file_end_time - file_start_time
        self.total_audios_generated += successful
        self.total_audios_failed += failed
        
        logger.info(f"✅ 文件处理完成: {file_name}")
        logger.info(f"  - 成功生成: {successful} 个音频文件")
        logger.info(f"  - 生成失败: {failed} 个")
        logger.info(f"  - 耗时: {file_duration/60:.1f} 分钟")
        
        self.processed_files.append({
            "file": file_name,
            "successful": successful,
            "failed": failed,
            "duration": file_duration,
            "voice": scripts[0]["voice"] if scripts else "unknown"
        })
        
        return True
    
    def process_all_files(self):
        """处理所有xlsx文件"""
        logger.info("🎵 开始完整处理inputs文件夹中的xlsx文件")
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
        
        # 处理每个文件
        success_count = 0
        for i, file_path in enumerate(xlsx_files):
            file_name = os.path.basename(file_path)
            logger.info(f"📁 处理文件 {i+1}/{len(xlsx_files)}: {file_name}")
            
            if self.process_single_file(file_path):
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
        logger.info("🎉 完整处理完成!")
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
            "voice_mapping": FILE_VOICE_MAPPING
        }
        
        report_file = f"logs/full_queue_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    processor = FullQueueProcessor()
    success = processor.process_all_files()
    
    if success:
        logger.info("✅ 所有文件处理成功！")
    else:
        logger.error("❌ 部分文件处理失败")

if __name__ == "__main__":
    main()
