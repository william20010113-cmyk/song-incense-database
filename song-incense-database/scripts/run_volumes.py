#!/usr/bin/env python3
"""
宋代香谱数据库 - 提取单卷（健壮版，含重试）
"""
import requests, json, os, sys, time

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "__DEEPSEEK_API_KEY__")
API_URL = "https://api.deepseek.com/chat/completions"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SYSTEM_PROMPT = """你是一位精通宋代香谱古籍的学者。你的任务是从知识记忆中将宋代香方的完整数据以JSON格式输出。

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
  "notes": "备注"
}

注意事项：
1. 只输出纯JSON数组，不要Markdown包裹
2. 药材用量保留原文的"两""钱""分""字"等
3. 如果记不清具体用量，保留香材名称，用量写"适量"
4. 每条香方必须包含完整的配方+制法"""

def extract_volume(task_id, book_name, recipe_list, volume=""):
    print(f"\n>>> 开始提取: {book_name} ({len(recipe_list)}条)")
    
    prompt = f"""请从你的知识库中提取《{book_name}》中以下香方的完整数据。

香方列表：
{chr(10).join([f'{i+1}. {name}' for i, name in enumerate(recipe_list)])}

请输出每条香方的结构化JSON。"""

    for attempt in range(3):
        try:
            resp = requests.post(API_URL, json={
                "model": "deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.05,
                "max_tokens": 16384,
                "stream": False
            }, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }, timeout=180)
            
            data = resp.json()
            if "choices" not in data:
                print(f"  ⚠️  API错误: {data.get('error', {}).get('message', data)}")
                if attempt < 2:
                    time.sleep(5)
                    continue
                return []
            
            content = data["choices"][0]["message"]["content"]
            clean = content.strip()
            if clean.startswith("```json"): clean = clean[7:]
            elif clean.startswith("```"): clean = clean[3:]
            if clean.endswith("```"): clean = clean[:-3]
            clean = clean.strip()
            
            recipes = json.loads(clean)
            if not isinstance(recipes, list):
                recipes = [recipes]
            
            for r in recipes:
                r["_book_id"] = task_id
                if not r.get("volume") and volume:
                    r["volume"] = volume
            
            with_ing = [r for r in recipes if r.get("ingredients") and len(r["ingredients"]) > 0]
            print(f"  ✅ {len(recipes)}/{len(recipe_list)} 条 (含配方: {len(with_ing)})")
            
            outpath = os.path.join(OUTPUT_DIR, f"{task_id}.json")
            with open(outpath, "w", encoding="utf-8") as f:
                json.dump(recipes, f, ensure_ascii=False, indent=2)
            print(f"  💾 已保存: {outpath}")
            
            # 预览
            for r in recipes[:2]:
                ings = ", ".join([f"{ig.get('name','?')}{ig.get('amount','')}" for ig in r.get("ingredients", [])[:3]])
                print(f"     → {r.get('fang_name','?')}: [{ings}]")
            
            return recipes
            
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON解析失败 (尝试 {attempt+1}/3)")
            if attempt < 2:
                time.sleep(5)
                continue
            return []
        except Exception as e:
            print(f"  ❌ 错误: {e} (尝试 {attempt+1}/3)")
            if attempt < 2:
                time.sleep(10)
                continue
            return []

# ===== 分批执行 =====
all_recipes = []

# 卷第一（已完成，跳过）
# all_recipes.extend(extract_volume("chenshi_v1", "陈氏香谱 卷第一", [
#     "汉宫香", "江南李主帐中香", "唐开元宫中香", "宣和御制香",
# ], "卷第一"))

# 卷第二
all_recipes.extend(extract_volume("chenshi_v2", "陈氏香谱 卷第二", [
    "百花香", "万春香", "宝华香", "聚仙香", "通仙香", "灵犀香", "金鸡香",
    "玉华香", "玉蕊香", "瑶英香", "清远香", "清心香", "醒骨香",
    "阁中香", "帐中香", "枕中香", "球子香",
    "梅花香", "兰花香", "桂花香", "菊花香", "荷花香", "茉莉香",
    "素馨香", "含笑香", "瑞香", "木犀香", "枣香", "柏子香",
    "松香", "菖蒲香", "艾香", "芸香",
    "麝香丸", "龙脑丸", "乳香丸", "苏合丸", "安息丸",
    "木香丸", "丁香丸", "檀香丸", "沉香丸", "降真丸"
]))
print("\n⏰ 等待3秒...")
time.sleep(3)

# 卷第三
all_recipes.extend(extract_volume("chenshi_v3", "陈氏香谱 卷第三", [
    "龙涎香", "笃耨香", "降真香", "甲香牙香", "百和香",
    "宝篆印香", "无尘篆香", "隔火香方", "傅身香粉", "沐香",
    "熏衣香", "笑兰香", "口香", "含香", "涂香", "散香",
    "瑞香饼", "龙涎香珠", "七宝香串", "香佩", "香囊方",
    "宝鼎香", "金鼎香", "瑞脑香", "马牙香",
    "胜白香", "玄香", "金粟黄香", "紫茸香", "碧云香"
]))
print("\n⏰ 等待3秒...")
time.sleep(3)

# 卷第四
all_recipes.extend(extract_volume("chenshi_v4", "陈氏香谱 卷第四", [
    "万寿香", "长春香丸", "秋寒香", "暖玉香", "清暑香",
    "安神枕香", "髻中香", "佩帏香", "幄中香", "笼中香", "衾中香",
    "祛秽香", "辟寒香", "辟暑香", "辟蚊香", "辟蠹香", "合口香",
    "沉香煎", "檀香膏", "丁香油", "木香汤", "藿香露",
    "桂花油", "梅花水", "兰膏", "麝香蜜", "龙脑浆", "百花膏"
]))
print("\n⏰ 等待3秒...")
time.sleep(3)

# 洪刍香谱
all_recipes.extend(extract_volume("hongchu_xiangpu", "洪刍《香谱》", [
    "苏合香丸", "安息香丸", "龙涎香", "笃耨香",
    "麝香丸", "龙脑丸", "乳香丸", "丁香丸", "木香丸",
    "檀香丸", "沉香丸", "降真丸",
    "梅花香", "兰花香", "桂花香", "菊花香", "荷花香",
    "茉莉香", "素馨香", "含笑香", "木犀香",
    "百刻印香", "五福篆香",
    "柏子香", "芸香"
]))

# ===== 合并 =====
print(f"\n\n{'='*60}")
print(f"📊 合并中...")
print(f"{'='*60}")

# 读取所有已保存的 JSON
import glob
all_data = []
for fpath in sorted(glob.glob(os.path.join(OUTPUT_DIR, "chenshi_v*.json")) + glob.glob(os.path.join(OUTPUT_DIR, "hongchu*.json"))):
    with open(fpath) as f:
        data = json.load(f)
    print(f"  {os.path.basename(fpath)}: {len(data)} 条")
    all_data.extend(data)

print(f"\n  总计: {len(all_data)} 条")

# 去重
seen = set()
unique = []
for r in all_data:
    key = r.get("fang_name", "") + "|" + r.get("book", "")
    if key not in seen:
        seen.add(key)
        unique.append(r)

print(f"  去重后: {len(unique)} 条")

outpath = os.path.join(OUTPUT_DIR, "all_recipes.json")
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print(f"  💾 合并保存: {outpath}")

# 香材索引
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
        })

idx_path = os.path.join(OUTPUT_DIR, "ingredient_index.json")
with open(idx_path, "w", encoding="utf-8") as f:
    json.dump(ingredient_index, f, ensure_ascii=False, indent=2, sort_keys=True)

print(f"  香材种类: {len(ingredient_index)} 种")
sorted_ings = sorted(ingredient_index.items(), key=lambda x: len(x[1]), reverse=True)
print(f"\n🏆 最常用香材:")
for name, recipes in sorted_ings[:20]:
    print(f"   {name}: {len(recipes)} 个香方")

print(f"\n🎉 完成！")
print(f"   数据库: {outpath}")
print(f"   索引: {idx_path}")
print(f"   香方: {len(unique)} 条")
print(f"   香材: {len(ingredient_index)} 种")
