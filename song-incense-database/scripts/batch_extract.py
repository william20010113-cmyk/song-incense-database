#!/usr/bin/env python3
"""
宋代香谱数据库 - 批量提取配方详情
策略：按卷分批，每批让模型输出完整结构化JSON
"""
import requests, json, os, time, sys

API_KEY = "__DEEPSEEK_API_KEY__"
API_URL = "https://api.deepseek.com/chat/completions"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def call_api(messages, max_tokens=16384):
    """Call DeepSeek API"""
    resp = requests.post(API_URL, json={
        "model": "deepseek-v4-flash",
        "messages": messages,
        "temperature": 0.05,
        "max_tokens": max_tokens,
        "stream": False
    }, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }, timeout=180)
    
    data = resp.json()
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API Error: {data.get('error', data)}")

def parse_json(text):
    """Extract JSON from model response"""
    clean = text.strip()
    if clean.startswith("```json"): clean = clean[7:]
    elif clean.startswith("```"): clean = clean[3:]
    if clean.endswith("```"): clean = clean[:-3]
    clean = clean.strip()
    return json.loads(clean)

# 每批提取的任务
TASKS = [
    {
        "id": "chenshi_v1",
        "name": "陈氏香谱 卷第一",
        "recipe_list": [
            "汉宫香", "江南李主帐中香", "唐开元宫中香", "宣和御制香",
            "真宗御制香", "仁宗御制香", "英宗御制香", "神宗御制香",
            "徽宗御制香", "高庙御制香", "宪圣皇后御制香",
            "寿光香", "长春香", "醒心香", "清神香",
            "黄太史香", "山谷香", "欧公香", "苏公香",
            "韩魏公香", "丁公香", "蔡太师香", "王荆公香", "温公香", "赵清献公香"
        ]
    },
    {
        "id": "chenshi_v2",
        "name": "陈氏香谱 卷第二",
        "recipe_list": [
            "百花香", "万春香", "宝华香", "聚仙香", "通仙香", "灵犀香", "金鸡香",
            "玉华香", "玉蕊香", "瑶英香", "清远香", "清心香", "醒骨香",
            "阁中香", "帐中香", "枕中香", "球子香",
            "梅花香", "兰花香", "桂花香", "菊花香", "荷花香", "茉莉香",
            "素馨香", "含笑香", "瑞香", "木犀香", "枣香", "柏子香",
            "松香", "菖蒲香", "艾香", "芸香",
            "麝香丸", "龙脑丸", "乳香丸", "苏合丸", "安息丸",
            "木香丸", "丁香丸", "檀香丸", "沉香丸", "降真丸",
            "清神丸", "醒心丸", "通神丸"
        ]
    },
    {
        "id": "chenshi_v3",
        "name": "陈氏香谱 卷第三",
        "recipe_list": [
            "龙涎香(甲式)", "笃耨香(复合方)", "降真香(复合方)", "牙香(甲香牙香)", "百和香",
            "宝篆印香", "无尘篆香", "隔火香方", "傅身香粉", "沐香",
            "洗香", "熏衣香(笑兰香)", "口香", "含香", "涂香", "散香",
            "瑞香饼", "龙涎香珠", "七宝香串", "香佩", "香囊方",
            "宝鼎香", "金鼎香", "瑞脑香", "马牙香",
            "胜白香", "玄香", "金粟黄香", "紫茸香", "碧云香",
            "妙香", "灵奇香", "天异香", "道德香", "道香", "佛智香",
            "天香第一", "地藏香"
        ]
    },
    {
        "id": "chenshi_v4",
        "name": "陈氏香谱 卷第四",
        "recipe_list": [
            "百花香(乙式)", "万寿香", "长春香丸", "秋寒香", "暖玉香", "清暑香",
            "安神枕香", "髻中香", "佩帏香", "幄中香", "笼中香", "衾中香",
            "祛秽香", "辟寒香", "辟暑香", "辟蚊香", "辟蠹香", "合口香",
            "乳香丸(别方)", "沉香煎", "檀香膏", "丁香油", "木香汤", "藿香露",
            "桂花油", "梅花水", "兰膏", "麝香蜜", "龙脑浆", "百花膏"
        ]
    },
    {
        "id": "hongchu_xiangpu",
        "name": "洪刍《香谱》",
        "recipe_list": [
            "汉宫香", "江南李主帐中香", "唐开元宫中香", "宣和御制香",
            "苏合香丸", "安息香丸", "龙涎香(洪氏方)", "笃耨香(洪氏方)",
            "麝香丸", "龙脑丸", "乳香丸", "丁香丸", "木香丸",
            "檀香丸", "沉香丸", "降真丸", "清神丸", "醒心丸", "通神丸",
            "百花香", "万春香", "宝华香", "聚仙香", "通仙香",
            "灵犀香", "金鸡香", "玉华香", "玉蕊香", "瑶英香",
            "清远香", "清心香", "醒骨香",
            "梅花香(洪氏方)", "兰花香", "桂花香", "菊花香", "荷花香",
            "茉莉香", "素馨香", "含笑香", "瑞香", "木犀香",
            "枣香", "柏子香", "松香", "菖蒲香", "艾香", "芸香",
            "百刻印香", "五福篆香"
        ]
    },
]

def extract_volume(task):
    """Extract all recipes for one volume"""
    print(f"\n{'='*60}")
    print(f"📖 提取: {task['name']}")
    print(f"   香方数: {len(task['recipe_list'])}")
    print(f"{'='*60}")
    
    system_prompt = """你是一位精通宋代香谱古籍的学者。你的任务是从知识记忆中将宋代香方的完整数据以JSON格式输出。

每个香方包含以下字段：
{
  "fang_name": "香方名称",
  "book": "所属古籍",
  "author": "作者",
  "volume": "卷次",
  "source_text": "香方原文（药材、用量、制法等完整原文，尽量还原古籍原文表述）",
  "ingredients": [{"name": "药材名", "amount": "用量，如一两、半两、五钱等", "original_text": "原文表述"}],
  "method": "制作方法描述",
  "category": "合香/熏衣/佩香/焚香/涂香/印香/香丸/香饼/其他",
  "usage": "用途说明",
  "notes": "备注，如不同版本的差异或特色说明"
}

注意事项：
1. 只输出纯JSON数组，不要Markdown包裹
2. 药材用量保留原文的"两""钱""分""字"等
3. 如果没有原文记忆，可以用合理的宋代合香常规做法推断，但在notes中注明"据常规推拟"
4. 不能回忆的香方请在ingredients中留空，在notes中注明"佚"
5. 尽量还原每条香方的完整配方"""

    prompt = f"""请从你的知识库中提取《{task['name']}》中以下香方的完整数据。

香方列表（共{len(task['recipe_list'])}条）：
{chr(10).join([f'  {i+1}. {name}' for i, name in enumerate(task['recipe_list'])])}

请输出每条香方的结构化JSON。尽可能完整还原配方和制法。"""

    try:
        result = call_api([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ])
        
        recipes = parse_json(result)
        if not isinstance(recipes, list):
            recipes = [recipes]
        
        # 添加来源标记
        for r in recipes:
            r["_book_id"] = task["id"]
        
        print(f"   ✅ 提取到 {len(recipes)}/{len(task['recipe_list'])} 条")
        
        # 统计有完整配方的
        with_ingredients = [r for r in recipes if r.get("ingredients") and len(r["ingredients"]) > 0]
        print(f"   📊 含完整配方: {len(with_ingredients)} 条")
        
        outpath = os.path.join(OUTPUT_DIR, f"{task['id']}.json")
        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        print(f"   💾 已保存: {outpath}")
        
        return recipes
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        # 保存原始返回供调试
        try:
            with open(os.path.join(OUTPUT_DIR, f"{task['id']}_error.txt"), "w") as f:
                f.write(str(e))
        except:
            pass
        return []

if __name__ == "__main__":
    print("🏛️  宋代香谱数据库 - 批量提取工具")
    print(f"   模型: DeepSeek V4 Flash")
    print(f"   任务数: {len(TASKS)}")
    print(f"   预计总香方: {sum(len(t['recipe_list']) for t in TASKS)}")
    print()
    
    all_recipes = []
    
    for i, task in enumerate(TASKS, 1):
        print(f"\n[{i}/{len(TASKS)}] ", end="")
        recipes = extract_volume(task)
        all_recipes.extend(recipes)
        
        # 打印预览
        for r in recipes[:3]:
            ings = ", ".join([f"{ig.get('name','?')}{ig.get('amount','')}" for ig in r.get("ingredients", [])[:3]])
            print(f"     {r.get('fang_name','?')}: [{ings}]")
        
        if i < len(TASKS):
            print("   ⏰ 等待2秒...")
            time.sleep(2)
    
    # 合并全部
    print(f"\n\n{'='*60}")
    print(f"📊 提取完成！总计 {len(all_recipes)} 条")
    print(f"{'='*60}")
    
    # 去重
    seen = set()
    unique = []
    for r in all_recipes:
        key = r.get("fang_name", "") + "|" + r.get("volume", "")
        if key not in seen:
            seen.add(key)
            unique.append(r)
    
    print(f"   去重后: {len(unique)} 条")
    
    outpath = os.path.join(OUTPUT_DIR, "all_recipes.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"   💾 合并保存: {outpath}")
    
    # 构建香材索引
    print(f"\n🔍 构建香材索引...")
    ingredient_index = {}
    for recipe in unique:
        for ing in recipe.get("ingredients", []):
            name = ing.get("name", "").strip()
            if not name:
                continue
            if name not in ingredient_index:
                ingredient_index[name] = []
            ingredient_index[name].append({
                "fang_name": recipe.get("fang_name", ""),
                "book": recipe.get("book", ""),
                "volume": recipe.get("volume", ""),
                "amount": ing.get("amount", ""),
                "method": recipe.get("method", "")[:80]
            })
    
    idx_path = os.path.join(OUTPUT_DIR, "ingredient_index.json")
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(ingredient_index, f, ensure_ascii=False, indent=2, sort_keys=True)
    
    print(f"   香材种类: {len(ingredient_index)} 种")
    sorted_ings = sorted(ingredient_index.items(), key=lambda x: len(x[1]), reverse=True)
    print(f"\n🏆 最常用香材 TOP 20:")
    for name, recipes in sorted_ings[:20]:
        print(f"   {name}: {len(recipes)} 个香方使用")
    
    # 输出示例查询
    print(f"\n📝 使用示例: 搜索'檀香'")
    if "檀香" in ingredient_index:
        for r in ingredient_index["檀香"][:5]:
            print(f"   → {r['fang_name']} ({r['book']}{'·'+r['volume'] if r.get('volume') else ''})")
    
    print(f"\n🎉 阶段1完成！")
