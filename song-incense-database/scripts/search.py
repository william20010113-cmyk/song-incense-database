#!/usr/bin/env python3
"""
宋代香谱数据库 v4.0
用法: python3 search.py [香材名]
"""
import json, sys, os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "all_recipes.json")

with open(DB_PATH) as f:
    ALL_RECIPES = json.load(f)

def search(ingredient):
    results = []
    for r in ALL_RECIPES:
        for ing in r.get("ingredients", []):
            if ingredient in ing.get("name", ""):
                results.append(r)
                break
    return results

def main():
    if len(sys.argv) < 2:
        books = set(r.get("book", "") for r in ALL_RECIPES)
        print(f"🏛️  香谱数据库 v4.0 — 326 条 — {len(ALL_RECIPES)} 条香方, {', '.join(sorted(books))}")
        print(f"用法: python3 search.py <香材名>")
        return
    
    query = sys.argv[1]
    results = search(query)
    
    if not results:
        print(f"未找到含「{query}」的香方")
        return
    
    print(f"\n🔍 「{query}」→ {len(results)} 条香方:")
    for i, r in enumerate(results[:30], 1):
        cite = r.get("source_citation", {}).get("full_reference", "")
        ings = "、".join([f"{ig['name']}{ig.get('amount','')}" for ig in r.get("ingredients", [])[:4]])
        flag = " ⚠️" if r.get("validation") else ""
        print(f"  {i:2d}. {r['fang_name']}{flag}")
        print(f"     出处: {cite}")
        print(f"     配方: {ings}...")
    
    if len(results) > 30:
        print(f"\n  ... 还有 {len(results)-30} 条未显示")

if __name__ == "__main__":
    main()
