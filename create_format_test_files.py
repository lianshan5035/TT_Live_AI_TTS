import pandas as pd
import os

# 创建测试目录
test_dir = '/Volumes/M2/TT_Live_AI_TTS/input'
os.makedirs(test_dir, exist_ok=True)

# 测试数据
test_data = {
    'English Script': [
        'Quick chat while I\'m getting ready during my morning routine — underarm and inner thigh shadows can mess with your vibe.',
        'Real talk from my during my post-shower moment — you shouldn\'t have to hide in oversized tees.',
        'Let\'s be honest during my pre-gym freshen-up — it\'s awkward when you love the dress but not the underarm shade.'
    ],
    'Chinese Translation': [
        '早上准备时的快速聊天——腋下和大腿内侧的阴影会影响你的心情。',
        '我在淋浴后的真实感受——你不应该躲在超大T恤里。',
        '我在健身前整理时的诚实感受——当你喜欢这件裙子但不喜欢腋下阴影时很尴尬。'
    ]
}

# 1. 创建不同字段名的Excel文件
df1 = pd.DataFrame(test_data)
df1.to_excel(f'{test_dir}/Test_Product_2025-10-27_800.xlsx', index=False)

# 2. 创建CSV文件
df2 = pd.DataFrame({
    'script': test_data['English Script'],
    'translation': test_data['Chinese Translation']
})
df2.to_csv(f'{test_dir}/Test_Product_2025-10-27_800.csv', index=False, encoding='utf-8')

# 3. 创建TSV文件
df3 = pd.DataFrame({
    'english': test_data['English Script'],
    'chinese': test_data['Chinese Translation']
})
df3.to_csv(f'{test_dir}/Test_Product_2025-10-27_800.tsv', index=False, sep='\t', encoding='utf-8')

# 4. 创建不同命名格式的文件
df4 = pd.DataFrame({
    '文案': test_data['English Script'],
    '翻译': test_data['Chinese Translation']
})
df4.to_excel(f'{test_dir}/2025-10-27美白产品_合并模板.xlsx', index=False)

print("测试文件已创建:")
print("1. Test_Product_2025-10-27_800.xlsx (English Script, Chinese Translation)")
print("2. Test_Product_2025-10-27_800.csv (script, translation)")
print("3. Test_Product_2025-10-27_800.tsv (english, chinese)")
print("4. 2025-10-27美白产品_合并模板.xlsx (文案, 翻译)")
