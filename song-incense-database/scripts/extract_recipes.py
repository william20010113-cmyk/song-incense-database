#!/usr/bin/env python3
"""
宋代香谱数据库 - 香方提取脚本
用 DeepSeek V4 Flash API 从古籍知识中提取结构化香方数据
"""
import json, os, sys, time
import requests

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "__DEEPSEEK_API_KEY__")
API_URL = "https://api.deepseek.com/chat/completions"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def call_deepseek(system_prompt, user_prompt, model="deepseek-v4-flash", temp=0.1):
    """Call DeepSeek API"""
    resp = requests.post(API_URL, json={
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temp,
        "max_tokens": 16384,
        "stream": False
    }, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }, timeout=120)
    
    data = resp.json()
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API Error: {data.get('error', data)}")

# ===== 古籍列表 =====
BOOKS = [
    {
        "id": "chenshi_xiangpu_v1",
        "name": "陈氏香谱 卷第一",
        "author": "陈敬 (南宋)",
        "desc": "含香品、修制、合香等总论及约100条香方"
    },
    {
        "id": "chenshi_xiangpu_v2",
        "name": "陈氏香谱 卷第二",
        "author": "陈敬 (南宋)",
        "desc": "约100条香方，含熏香、佩香等"
    },
    {
        "id": "chenshi_xiangpu_v3",
        "name": "陈氏香谱 卷第三",
        "author": "陈敬 (南宋)",
        "desc": "约100条香方，含印香、涂香等"
    },
    {
        "id": "chenshi_xiangpu_v4",
        "name": "陈氏香谱 卷第四",
        "author": "陈敬 (南宋)",
        "desc": "约100条香方，含香丸、香饼等"
    },
    {
        "id": "hongchu_xiangpu",
        "name": "香谱 (洪刍)",
        "author": "洪刍 (北宋)",
        "desc": "洪刍《香谱》约100条香方，最早香谱专书"
    },
    {
        "id": "ye_xianglu",
        "name": "香录 (叶廷珪)",
        "author": "叶廷珪 (南宋)",
        "desc": "《名香谱》即叶廷珪《香录》，约80条香方"
    },
]

def extract_book(book):
    """从 DeepSeek 知识中提取一个古籍的全部香方"""
    print(f"\n{'='*60}")
    print(f"📖 正在提取: {book['name']}")
    print(f"   作者: {book['author']}")
    print(f"{'='*60}")
    
    system_prompt = """你是一位精通宋代香谱古籍的学者。你的任务是从你训练数据中的知识，提取完整的宋代香方数据。

请严格按照以下 JSON 格式输出每一条香方：

```json
[
  {
    "fang_name": "香方名称",
    "book": "所属古籍",
    "author": "作者",
    "volume": "卷次",
    "source_text": "香方原文（包括药材、用量、制法等完整原文）",
    "ingredients": [
      {"name": "药材名", "amount": "用量", "original": "原文中的名称"}
    ],
    "method": "制作方法描述",
    "category": "分类（合香/熏衣/佩香/焚香/涂香/印香/香丸/香饼/其它）",
    "usage": "用途（如：熏衣、佩带、焚烧、供佛、入药等）",
    "notes": "备注/特色说明"
  }
]
```

注意事项：
1. 只输出格式化的 JSON，不要额外文字
2. 如果原文中有"右为细末""炼蜜和丸"等制法术语，保留原貌
3. 药材用量保留原文中的"两""钱""分""字"等单位
4. 每个香方尽量包含完整的配方+制法
5. 如果同一个香方有不同的出处版本（如《陈氏香谱》引《洪谱》），在 notes 中注明
6. 严格只输出 JSON 数组，不要 Markdown 包裹"""

    prompt = f"""请从你的知识库中提取《{book['name']}》（{book['author']}）的全部香方数据。

{book['desc']}

请输出完整的结构化 JSON，包含所有香方。每条香方需包含：
- fang_name: 香方名称
- book: 书名
- author: 作者
- volume: 卷次
- source_text: 完整原文
- ingredients: 成分列表（name/amount/original）
- method: 制法
- category: 分类
- usage: 用途
- notes: 备注

能回忆起多少条就输出多少条，请尽量完整。"""

    try:
        result = call_deepseek(system_prompt, prompt)
        
        # 提取 JSON
        result_clean = result.strip()
        if result_clean.startswith("```json"):
            result_clean = result_clean[7:]
        if result_clean.startswith("```"):
            result_clean = result_clean[3:]
        if result_clean.endswith("```"):
            result_clean = result_clean[:-3]
        result_clean = result_clean.strip()
        
        recipes = json.loads(result_clean)
        if not isinstance(recipes, list):
            recipes = [recipes]
        
        print(f"   ✅ 提取到 {len(recipes)} 条香方")
        
        # 保存
        outpath = os.path.join(OUTPUT_DIR, f"{book['id']}.json")
        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        print(f"   💾 已保存: {outpath}")
        
        return recipes
        
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON解析错误: {e}")
        print(f"   📝 原始返回(前500字): {result[:500]}")
        # 保存原始返回以供分析
        with open(os.path.join(OUTPUT_DIR, f"{book['id']}_raw.txt"), "w", encoding="utf-8") as f:
            f.write(result)
        return []
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return []

def merge_all(output_dir, books_meta):
    """合并所有提取结果"""
    all_recipes = []
    
    for book in books_meta:
        path = os.path.join(output_dir, f"{book['id']}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                recipes = json.load(f)
            for r in recipes:
                r["_source_book"] = book["name"]
            all_recipes.extend(recipes)
            print(f"  ✅ {book['name']}: {len(recipes)} 条")
    
    # 去重（同名的只保留一份）
    seen = set()
    unique = []
    for r in all_recipes:
        key = r.get("fang_name", "") + "|" + r.get("source_text", "")[:50]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    
    print(f"\n📊 总计: {len(all_recipes)} 条, 去重后: {len(unique)} 条")
    
    outpath = os.path.join(output_dir, "all_recipes.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"💾 合并保存: {outpath}")
    
    return unique

def build_index(all_recipes):
    """构建按香材索引"""
    ingredient_index = {}
    
    for recipe in all_recipes:
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
                "ingredient_detail": ing,
                "method": recipe.get("method", "")[:100]
            })
    
    outpath = os.path.join(OUTPUT_DIR, "ingredient_index.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(ingredient_index, f, ensure_ascii=False, indent=2, sort_keys=True)
    
    print(f"\n📊 索引统计:")
    print(f"   香材种类: {len(ingredient_index)} 种")
    
    # 列出最常用的香材
    sorted_ings = sorted(ingredient_index.items(), key=lambda x: len(x[1]), reverse=True)
    print(f"   最常用香材 TOP 20:")
    for name, recipes in sorted_ings[:20]:
        print(f"     {name}: {len(recipes)} 个香方使用")
    
    return ingredient_index

if __name__ == "__main__":
    print("🏛️  宋代香谱数据库 - 提取工具")
    print("=" * 40)
    print(f"模型: DeepSeek V4 Flash")
    print(f"古籍数: {len(BOOKS)} 部")
    print(f"输出目录: {OUTPUT_DIR}")
    
    all_ok = []
    
    for book in BOOKS:
        recipes = extract_book(book)
        all_ok.append(len(recipes) > 0)
        time.sleep(2)  # 避免频率限制
    
    print(f"\n{'='*60}")
    print(f"📊 提取完成")
    print(f"{'='*60}")
    
    # 合并
    print(f"\n🔄 合并中...")
    all_recipes = merge_all(OUTPUT_DIR, BOOKS)
    
    # 建索引
    print(f"\n🔍 构建香材索引...")
    ingredient_index = build_index(all_recipes)
    
    print(f"\n🎉 阶段1完成!")
    print(f"   数据库: {OUTPUT_DIR}/all_recipes.json")
    print(f"   索引: {OUTPUT_DIR}/ingredient_index.json")
    print(f"   香方总数: {len(all_recipes)}")
    print(f"   香材种类: {len(ingredient_index)}")
    
    # 输出示例
    print(f"\n📝 使用示例:")
    print(f"   搜索'檀香':")
    if "檀香" in ingredient_index:
        for r in ingredient_index["檀香"][:5]:
            print(f"     → {r['fang_name']} ({r['book']})")
