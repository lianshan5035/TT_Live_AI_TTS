#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建GPTs Excel模板文件
支持多种字段名变体，方便GPTs生成
"""

import pandas as pd
import os

def create_gpts_excel_templates():
    """创建多种GPTs Excel模板"""
    
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(__file__), '08_数据文件_输入输出和日志', 'templates')
    os.makedirs(output_dir, exist_ok=True)
    
    # 模板1: 标准格式
    template1_data = {
        'english_script': [
            "Welcome to our revolutionary skincare line!",
            "Experience the power of natural ingredients.",
            "Transform your skin in just 7 days.",
            "Join thousands of satisfied customers worldwide.",
            "Discover the secret to radiant, youthful skin."
        ],
        'chinese_translation': [
            "欢迎来到我们革命性的护肤系列！",
            "体验天然成分的力量。",
            "仅需7天改变您的肌肤。",
            "加入全球数千名满意的客户。",
            "发现光彩年轻肌肤的秘密。"
        ]
    }
    
    # 模板2: GPTs常用格式
    template2_data = {
        'English Content': [
            "Introducing our breakthrough anti-aging formula!",
            "Clinical studies show 95% improvement in skin texture.",
            "Limited time offer - Save 50% today only!",
            "Free shipping on orders over $50.",
            "30-day money-back guarantee - risk-free trial."
        ],
        'Chinese Content': [
            "介绍我们突破性的抗衰老配方！",
            "临床研究显示肌肤纹理改善95%。",
            "限时优惠 - 今天仅限5折！",
            "订单满50美元免费配送。",
            "30天退款保证 - 无风险试用。"
        ]
    }
    
    # 模板3: 营销文案格式
    template3_data = {
        'English Marketing': [
            "Don't miss out on this exclusive deal!",
            "Transform your beauty routine today.",
            "Premium quality at an unbeatable price.",
            "Join the beauty revolution now.",
            "Your skin deserves the very best."
        ],
        'Chinese Marketing': [
            "不要错过这个独家优惠！",
            "今天就改变您的美容习惯。",
            "无与伦比价格的优质品质。",
            "立即加入美容革命。",
            "您的肌肤值得最好的。"
        ]
    }
    
    # 模板4: 产品描述格式
    template4_data = {
        'English Description': [
            "Advanced skincare technology meets natural ingredients.",
            "Dermatologist-tested and cruelty-free formula.",
            "Suitable for all skin types and ages.",
            "Easy to use - apply twice daily for best results.",
            "Packaged in eco-friendly, recyclable materials."
        ],
        'Chinese Description': [
            "先进护肤技术与天然成分的结合。",
            "皮肤科医生测试，无动物实验配方。",
            "适合所有肌肤类型和年龄。",
            "使用简单 - 每日两次获得最佳效果。",
            "环保包装，可回收材料。"
        ]
    }
    
    # 模板5: 社交媒体格式
    template5_data = {
        'English Posts': [
            "✨ New product alert! ✨",
            "💫 Glowing skin starts here 💫",
            "🌟 Limited edition - Get yours now! 🌟",
            "💎 Premium quality, affordable price 💎",
            "🎉 Special launch offer - Don't wait! 🎉"
        ],
        'Chinese Posts': [
            "✨ 新品提醒！✨",
            "💫 光彩肌肤从这里开始 💫",
            "🌟 限量版 - 立即获取！🌟",
            "💎 优质品质，实惠价格 💎",
            "🎉 特别发布优惠 - 不要等待！🎉"
        ]
    }
    
    templates = [
        (template1_data, "标准格式模板_Standard_Format_Template.xlsx"),
        (template2_data, "GPTs常用格式模板_GPTs_Common_Format_Template.xlsx"),
        (template3_data, "营销文案格式模板_Marketing_Copy_Template.xlsx"),
        (template4_data, "产品描述格式模板_Product_Description_Template.xlsx"),
        (template5_data, "社交媒体格式模板_Social_Media_Template.xlsx")
    ]
    
    created_files = []
    
    for template_data, filename in templates:
        try:
            df = pd.DataFrame(template_data)
            filepath = os.path.join(output_dir, filename)
            df.to_excel(filepath, index=False)
            created_files.append(filepath)
            print(f"✅ 创建模板: {filename}")
        except Exception as e:
            print(f"❌ 创建模板失败 {filename}: {str(e)}")
    
    # 创建说明文件
    readme_content = """# GPTs Excel模板文件说明

## 📁 模板文件列表

1. **标准格式模板_Standard_Format_Template.xlsx**
   - 字段: english_script, chinese_translation
   - 适用: 标准语音生成需求

2. **GPTs常用格式模板_GPTs_Common_Format_Template.xlsx**
   - 字段: English Content, Chinese Content
   - 适用: GPTs生成的内容

3. **营销文案格式模板_Marketing_Copy_Template.xlsx**
   - 字段: English Marketing, Chinese Marketing
   - 适用: 营销推广内容

4. **产品描述格式模板_Product_Description_Template.xlsx**
   - 字段: English Description, Chinese Description
   - 适用: 产品介绍描述

5. **社交媒体格式模板_Social_Media_Template.xlsx**
   - 字段: English Posts, Chinese Posts
   - 适用: 社交媒体内容

## 🎯 使用说明

1. **选择模板**: 根据您的需求选择合适的模板
2. **修改内容**: 替换示例内容为您的实际内容
3. **保存文件**: 使用描述性的文件名，包含产品名称
4. **上传生成**: 通过Web界面上传文件进行语音生成

## 📋 字段要求

- **必需字段**: 包含英文脚本内容的列（任意支持的字段名）
- **可选字段**: 中文翻译列（仅用于参考）
- **内容要求**: 每行一个完整的句子或短语
- **数量限制**: 建议单次处理不超过1000条

## 🎵 声音参数

系统会根据产品名称自动选择合适的声音参数：
- **情绪类型**: 12种预设情绪（Excited, Confident, Empathetic等）
- **语音选择**: 默认使用en-US-JennyNeural
- **动态调整**: 基于A3标准的动态参数生成

## 🔧 技术支持

如有问题，请参考：
- GPTS_EXCEL_FORMAT_GUIDE_GPTs_Excel格式规范指南.md
- 系统日志文件
- Web界面错误提示

---
*模板创建时间: 2025-10-27*
*版本: v1.0*
"""
    
    readme_path = os.path.join(output_dir, "README_模板使用说明.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n📋 创建说明文件: README_模板使用说明.md")
    print(f"\n🎯 模板文件位置: {output_dir}")
    print(f"📊 共创建 {len(created_files)} 个模板文件")
    
    return created_files

if __name__ == '__main__':
    print("🚀 创建GPTs Excel模板文件...")
    created_files = create_gpts_excel_templates()
    print(f"\n✅ 模板创建完成！")
    print(f"📁 文件位置: {os.path.dirname(created_files[0]) if created_files else 'N/A'}")
