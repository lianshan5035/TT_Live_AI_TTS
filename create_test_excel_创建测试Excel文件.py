import pandas as pd
import os

# 创建测试Excel文件
def create_test_excel():
    """创建一个测试用的Excel文件"""
    
    # 测试数据
    data = {
        'english_script': [
            'Welcome to our new product launch event.',
            'This innovative solution will revolutionize your workflow.',
            'Join us for an exclusive demonstration.',
            'Don\'t miss this amazing opportunity.'
        ],
        'chinese_translation': [
            '欢迎参加我们的新产品发布会。',
            '这个创新解决方案将彻底改变您的工作流程。',
            '加入我们参加独家演示。',
            '不要错过这个绝佳的机会。'
        ]
    }
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 保存为Excel文件
    filename = 'test_product_launch.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ 测试Excel文件已创建: {filename}")
    print(f"📊 包含 {len(df)} 条脚本")
    print(f"📁 文件大小: {os.path.getsize(filename)} bytes")
    
    return filename

if __name__ == "__main__":
    create_test_excel()
