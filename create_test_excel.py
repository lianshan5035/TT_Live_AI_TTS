import pandas as pd

# 创建测试Excel文件
data = {
    'english_script': [
        'Quick chat while I\'m getting ready during my morning routine — underarm and inner thigh shadows can mess with your vibe. I don\'t chase magic, I just want skin that looks calm and even. So, so I started using this brightening spot cream in my morning routine: non-sticky, light scent, and it helps skin look smoother and more even. I use a tiny amount, gentle circles, and let clothes glide without friction. Week by week, the look feels more confident — sleeves off, shorts on. Two pieces save thirty percent, four pieces save fifty percent. If it fits your vibe, grab the bundle. Results may vary.',
        'Real talk from my during my post-shower moment — you shouldn\'t have to hide in oversized tees. I don\'t chase magic, I just want skin that looks calm and even. So, I added this lightweight cream to my post-shower moment: it\'s simple care that makes outfits feel easier. I use a tiny amount, gentle circles, and let clothes glide without friction. Week by week, the look feels more confident — sleeves off, shorts on. Two pieces save thirty percent, four pieces save fifty percent. If you want simple care, this is it — Results may vary.',
        'Let\'s be honest during my pre-gym freshen-up — it\'s awkward when you love the dress but not the underarm shade. I don\'t chase magic, I just want skin that looks calm and even. So, I tried this soft, fast-absorbing cream in my pre-gym freshen-up: non-sticky, light scent, and it helps skin look smoother and more even. I use a tiny amount, gentle circles, and let clothes glide without friction. Week by week, the look feels more confident — sleeves off, shorts on. Two pieces save thirty percent, four pieces save fifty percent. If you love a clean finish, snag it. Results may vary.'
    ],
    'chinese_translation': [
        '早上准备时的快速聊天——腋下和大腿内侧的阴影会影响你的心情。我不追求魔法，我只想要看起来平静均匀的肌肤。所以，我在晨间护肤中开始使用这款亮白淡斑霜：不粘腻，淡香，让肌肤看起来更光滑均匀。我用少量，轻柔打圈，让衣服无摩擦滑动。一周又一周，看起来更自信——袖子卷起，短裤穿上。两件省30%，四件省50%。如果符合你的风格，就买套装。效果因人而异。',
        '我在淋浴后的真实感受——你不应该躲在超大T恤里。我不追求魔法，我只想要看起来平静均匀的肌肤。所以，我在淋浴后添加了这款轻质霜：简单的护理让穿搭更容易。我用少量，轻柔打圈，让衣服无摩擦滑动。一周又一周，看起来更自信——袖子卷起，短裤穿上。两件省30%，四件省50%。如果你想要简单护理，这就是——效果因人而异。',
        '我在健身前整理时的诚实感受——当你喜欢这件裙子但不喜欢腋下阴影时很尴尬。我不追求魔法，我只想要看起来平静均匀的肌肤。所以，我在健身前整理时尝试了这款柔软、快速吸收的霜：不粘腻，淡香，让肌肤看起来更光滑均匀。我用少量，轻柔打圈，让衣服无摩擦滑动。一周又一周，看起来更自信——袖子卷起，短裤穿上。两件省30%，四件省50%。如果你喜欢干净的效果，就买它。效果因人而异。'
    ]
}

df = pd.DataFrame(data)
df.to_excel('/Volumes/M2/TT_Live_AI_TTS/input/Lior2025-10-23淡化美白美容霜腋下和大腿黑斑霜_800合并模板.xlsx', index=False)
print("测试Excel文件已创建")
