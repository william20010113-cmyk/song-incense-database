#!/usr/bin/env python3
"""
宋代香谱数据库 - 三步合一：本草药性 + 香材归一化 + 配方校验
"""
import json

with open("data/all_recipes.json") as f:
    recipes = json.load(f)
with open("data/materia_medica.json") as f:
    mm = json.load(f)
with open("data/ingredient_index.json") as f:
    idx = json.load(f)

# ===== 1. 归一化映射 =====
NORMALIZATION_MAP = {
    "檀香": {"standard": "檀香", "aliases": ["白檀香", "旃檀"]},
    "白檀香": {"standard": "檀香", "aliases": ["檀香", "旃檀"]},
    "龙脑": {"standard": "龙脑", "aliases": ["片脑", "龙脑香", "梅花冰片", "冰片"]},
    "片脑": {"standard": "龙脑", "aliases": ["龙脑", "龙脑香", "梅花冰片", "冰片"]},
    "梅花冰片": {"standard": "龙脑", "aliases": ["龙脑", "片脑", "龙脑香", "冰片"]},
    "苏合油": {"standard": "苏合香", "aliases": ["苏合香油", "苏合香"]},
    "苏合香油": {"standard": "苏合香", "aliases": ["苏合油", "苏合香"]},
    "苏合香": {"standard": "苏合香", "aliases": ["苏合油", "苏合香油"]},
    "蜜": {"standard": "蜜", "aliases": ["炼蜜", "白蜜"]},
    "藿香叶": {"standard": "藿香", "aliases": ["藿香"]},
    "白芨末": {"standard": "白芨", "aliases": ["白芨"]},
    "芸香草": {"standard": "芸香", "aliases": ["芸香"]},
    "龙涎香末": {"standard": "龙涎香", "aliases": ["龙涎香"]},
    "桂花末": {"standard": "桂花", "aliases": ["桂花"]},
    "柏子实": {"standard": "柏子仁", "aliases": ["柏子仁"]},
}

def get_standard_name(name):
    if name in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[name]["standard"]
    return name

# ===== 2. 更新每条香方 =====
for r in recipes:
    normalized_ingredients = []
    for ing in r.get("ingredients", []):
        raw_name = ing.get("name", "")
        std_name = get_standard_name(raw_name)
        
        new_ing = {
            "name": std_name,
            "original_name": raw_name,
            "original_text": ing.get("original_text", raw_name),
            "amount": ing.get("amount", ""),
        }
        
        if std_name in mm:
            new_ing["nature"] = mm[std_name].get("nature", "")
            new_ing["flavor"] = mm[std_name].get("flavor", "")
            new_ing["effect"] = mm[std_name].get("effect", "")
            new_ing["toxicity"] = mm[std_name].get("toxicity", "无毒")
        
        normalized_ingredients.append(new_ing)
    
    r["ingredients"] = normalized_ingredients
    
    # ===== 3. 校验 =====
    flags = []
    ings = r.get("ingredients", [])
    amounts = [i.get("amount", "") for i in ings]
    
    if amounts and all(a in ["等分", "equal parts", "各等分", "适量"] for a in amounts):
        flags.append("配方用量为等分，需考证原书")
    
    if len(ings) < 3:
        flags.append("配方仅" + str(len(ings)) + "味香材，可能不完整")
    
    common = {"沉香", "檀香", "龙脑", "麝香"}
    ing_names = set(i.get("name", "") for i in ings)
    if ing_names.issubset(common) and len(ings) <= 4:
        flags.append("仅含基础四味（沉香/檀香/龙脑/麝香），可能为模型推拟")
    
    method = r.get("method", "")
    if "等分" in method or len(method) < 10:
        flags.append("制法简略，需考证")
    
    if "推拟" in r.get("notes", "") or "常规" in r.get("notes", ""):
        flags.append("模型标注为推拟")
    
    if flags:
        r["validation"] = flags

# ===== 4. 保存 =====
with open("data/all_recipes.json", "w", encoding="utf-8") as f:
    json.dump(recipes, f, ensure_ascii=False, indent=2)
print("All recipes saved.")

# ===== 5. 重建索引 =====
new_idx = {}
for r in recipes:
    for ing in r.get("ingredients", []):
        name = ing.get("name", "").strip()
        if not name:
            continue
        if name not in new_idx:
            new_idx[name] = []
        new_idx[name].append({
            "fang_name": r.get("fang_name", ""),
            "book": r.get("book", ""),
            "volume": r.get("volume", ""),
            "original_name": ing.get("original_name", name),
        })

with open("data/ingredient_index.json", "w", encoding="utf-8") as f:
    json.dump(new_idx, f, ensure_ascii=False, indent=2, sort_keys=True)

print("Ingredient index rebuilt.")
print(f"Materials: {len(idx)} -> {len(new_idx)} (merged {len(idx)-len(new_idx)} aliases)")

# ===== 6. 校验报告 =====
flagged = [r for r in recipes if r.get("validation")]
print(f"\nNeeds validation: {len(flagged)}/{len(recipes)} recipes")

with open("data/validation_report.txt", "w", encoding="utf-8") as f:
    f.write(f"Song Incense DB Validation Report\n")
    f.write(f"Total: {len(recipes)}, Flagged: {len(flagged)}\n\n")
    for r in flagged:
        f.write(f"[FLAG] {r['fang_name']} ({r.get('book','')} {r.get('volume','')})\n")
        for v in r.get("validation", []):
            f.write(f"  -> {v}\n")
        parts = [i.get("original_name","")+i.get("amount","") for i in r.get("ingredients",[])]
        f.write(f"  Recipe: {', '.join(parts)}\n\n")

print(f"Report: data/validation_report.txt")
print(f"Recipes: {len(recipes)}, Flagged: {len(flagged)}")
