import pandas as pd
import os

# 创建测试目录
test_dir = '/Volumes/M2/TT_Live_AI_TTS/input'
os.makedirs(test_dir, exist_ok=True)

# 1. GPTs生成的Markdown表格文件
markdown_content = """| English Content | Chinese Translation |
|----------------|---------------------|
| Transform your skin with our revolutionary dark spot patch! | 用我们的革命性黑斑贴片改变您的肌肤！ |
| Say goodbye to dark spots forever with our advanced formula. | 用我们先进的配方永远告别黑斑。 |
| Get ready for flawless, even-toned skin in just 7 days! | 准备在短短7天内获得完美、均匀的肌肤！ |
| Experience visible results from the very first application. | 从第一次使用就能看到明显效果。 |
| Join thousands of satisfied customers who trust our solution. | 加入数千名信任我们解决方案的满意客户。 |
"""

with open(f'{test_dir}/GPTs_Generated_2025-10-27_美白产品.txt', 'w', encoding='utf-8') as f:
    f.write(markdown_content)

# 2. GPTs生成的CSV文件（不同字段名）
gpts_csv_data = {
    'Content': [
        'Transform your skin with our revolutionary dark spot patch!',
        'Say goodbye to dark spots forever with our advanced formula.',
        'Get ready for flawless, even-toned skin in just 7 days!',
        'Experience visible results from the very first application.',
        'Join thousands of satisfied customers who trust our solution.'
    ],
    'Chinese': [
        '用我们的革命性黑斑贴片改变您的肌肤！',
        '用我们先进的配方永远告别黑斑。',
        '准备在短短7天内获得完美、均匀的肌肤！',
        '从第一次使用就能看到明显效果。',
        '加入数千名信任我们解决方案的满意客户。'
    ]
}

df1 = pd.DataFrame(gpts_csv_data)
df1.to_csv(f'{test_dir}/GPTs_Generated_2025-10-27_美白产品.csv', index=False, encoding='utf-8')

# 3. GPTs生成的Excel文件（营销内容字段名）
gpts_excel_data = {
    'English Marketing': [
        'Transform your skin with our revolutionary dark spot patch!',
        'Say goodbye to dark spots forever with our advanced formula.',
        'Get ready for flawless, even-toned skin in just 7 days!',
        'Experience visible results from the very first application.',
        'Join thousands of satisfied customers who trust our solution.'
    ],
    'Chinese Marketing': [
        '用我们的革命性黑斑贴片改变您的肌肤！',
        '用我们先进的配方永远告别黑斑。',
        '准备在短短7天内获得完美、均匀的肌肤！',
        '从第一次使用就能看到明显效果。',
        '加入数千名信任我们解决方案的满意客户。'
    ]
}

df2 = pd.DataFrame(gpts_excel_data)
df2.to_excel(f'{test_dir}/GPTs_Generated_2025-10-27_美白产品_营销.xlsx', index=False)

# 4. GPTs生成的TSV文件（文案字段名）
gpts_tsv_data = {
    'English Copywriting': [
        'Transform your skin with our revolutionary dark spot patch!',
        'Say goodbye to dark spots forever with our advanced formula.',
        'Get ready for flawless, even-toned skin in just 7 days!',
        'Experience visible results from the very first application.',
        'Join thousands of satisfied customers who trust our solution.'
    ],
    'Chinese Copywriting': [
        '用我们的革命性黑斑贴片改变您的肌肤！',
        '用我们先进的配方永远告别黑斑。',
        '准备在短短7天内获得完美、均匀的肌肤！',
        '从第一次使用就能看到明显效果。',
        '加入数千名信任我们解决方案的满意客户。'
    ]
}

df3 = pd.DataFrame(gpts_tsv_data)
df3.to_csv(f'{test_dir}/GPTs_Generated_2025-10-27_美白产品_文案.tsv', index=False, sep='\t', encoding='utf-8')

# 5. GPTs生成的纯文本表格
text_table_content = """English Headlines	Chinese Headlines
Transform your skin with our revolutionary dark spot patch!	用我们的革命性黑斑贴片改变您的肌肤！
Say goodbye to dark spots forever with our advanced formula.	用我们先进的配方永远告别黑斑。
Get ready for flawless, even-toned skin in just 7 days!	准备在短短7天内获得完美、均匀的肌肤！
Experience visible results from the very first application.	从第一次使用就能看到明显效果。
Join thousands of satisfied customers who trust our solution.	加入数千名信任我们解决方案的满意客户。
"""

with open(f'{test_dir}/GPTs_Generated_2025-10-27_美白产品_标题.txt', 'w', encoding='utf-8') as f:
    f.write(text_table_content)

print("GPTs生成的测试文件已创建:")
print("1. GPTs_Generated_2025-10-27_美白产品.txt (Markdown表格)")
print("2. GPTs_Generated_2025-10-27_美白产品.csv (Content, Chinese)")
print("3. GPTs_Generated_2025-10-27_美白产品_营销.xlsx (English Marketing, Chinese Marketing)")
print("4. GPTs_Generated_2025-10-27_美白产品_文案.tsv (English Copywriting, Chinese Copywriting)")
print("5. GPTs_Generated_2025-10-27_美白产品_标题.txt (English Headlines, Chinese Headlines)")
