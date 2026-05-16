# Chinese Incense Compendium · 香谱数据库

> **A curated digital archive of 378 classical Chinese incense formulas from 8 texts spanning the Song through Qing dynasties — fully bilingual, searchable, and open.**

[🌐 Browse Online](https://changhaoli.com/digital-analogue/incense-db/) · [📖 About the Project](https://changhaoli.com/digital-analogue/incense-db/about) · [🀄 中文版](https://changhaoli.com/digital-analogue/incense-db/about_zh)

---

## Overview

The Song dynasty (960–1279) was a golden age of Chinese incense culture. Scholars, monks, and perfumers developed a sophisticated body of knowledge around blending, compounding, and appreciating aromatic materials — recorded across dozens of manuscripts, manuals, and literary miscellanies. Much of this knowledge remained inaccessible outside specialist circles.

This project brings together **378 formulas** from eight major classical sources into a unified, searchable database. Every recipe has been structurally parsed and translated into English alongside its original Chinese text.

### Data at a Glance

| Metric | Count |
|--------|-------|
| Total formulas | **378** |
| Classical sources | **8** |
| Ingredient entries | **2,938** |
| Unique materials | **217** |
| Categories (preparation/application) | **55** |
| Use cases (intended application) | **180** |
| Bilingual glossary entries | **831** |

### Source Texts

| Work | Author | Dynasty |
|------|--------|---------|
| Chen's Incense Manual (陈氏香谱, 4 vols.) | Chen Jing (陈敬) | Song |
| Hong Chu's Incense Manual (洪刍香谱) | Hong Chu (洪刍) | Song |
| Compendium of Incense (香乘, 18 vols.) | Zhou Jiashe (周嘉胄) | Ming (preserving Song sources) |
| Eight Discourses on Nurturing Life (遵生八笺) | Gao Lian (高濂) | Ming |
| Essential Arts for Household Use (居家必用事类全集) | Anonymous | Ming/Yuan |
| Extensive Records from Forest of Affairs (事林广记) | Chen Yuanjing (陈元靓) | Song |
| Notes on the Ancestor of Incense (香祖笔记) | Wang Shizhen (王士禛) | Qing |
| Selected Sources on Chinese Incense Literature (中国香文献辑要) | Modern compilation | Modern |

---

## Features

- **Bilingual interface** — Toggle between Chinese and English at any time. Labels, filters, and recipe data switch in-place.
- **Multi-dimensional filtering** — Filter by classical text, category, or usage. Full-text search across names and ingredients.
- **Structured recipe data** — Each formula includes ingredients (with traditional Chinese medicine properties: nature, flavor, effect, toxicity), compounding method, and source citation.
- **Traditional units preserved** — Quantities are kept in original units (liang 两, qian 钱, fen 分, equal parts, etc.) rather than converted to metric.
- **Incense poetry** — Random Song-dynasty incense poem displayed on each page load.
- **Zero-dependency frontend** — Single HTML file, no build tools, no server, no database. Just open and use.

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/william20010113-cmyk/changhaoli.com.git
cd changhaoli.com/digital-analogue/incense-db/

# Open in browser (no server required)
open index.html
# or: xdg-open index.html
# or just double-click the file
```

The complete dataset (`all_recipes.json` for Chinese, `all_recipes_en.json` for English) is loaded from the local filesystem — no network requests needed once the page is open.

---

## Recipe Structure

Each of the 378 formulas is recorded with the following fields:

```json
{
  "fang_name": "Han Palace Incense",
  "fang_name_zh": "汉宫香",
  "book": "Compendium of Incense (香乘)",
  "author": "Zhou Jiashe",
  "volume": "Volume 12",
  "category": "Compound Blending (合香)",
  "usage": "Clothes Scenting (熏衣)",
  "method": "Grind into fine powder, mix with honey...",
  "ingredients": [
    {
      "name": "Agarwood / Aloeswood / Chenxiang",
      "original_name": "沉香",
      "amount": "8 liang",
      "nature": "Warm",
      "flavor": "Acrid, Bitter",
      "effect": "Promotes qi, relieves pain",
      "toxicity": "Non-toxic"
    }
  ],
  "source_text": "真腊沉香八两...",
  "source_citation": "香乘·卷十二·汉宫香"
}
```

---

## Translation Pipeline

Translation was not a single pass but a structured pipeline:

1. **Glossary construction** — 831 entries extracted: 8 book titles + 55 categories + 217 ingredients + 175 usages + 377 formula names
2. **Pattern-based formula name translation** — Rule matching (`X香` → `X Incense`, `X法` → `X Method`, etc.) with manual edge-case review
3. **English dataset generation** — All fields mapped through the glossary, producing `all_recipes_en.json` (1.3 MB)
4. **Zero Chinese characters** in translated fields verified programmatically

Formula names preserve the Chinese original in brackets during English display:
> *Han Palace Incense [汉宫香]*

---

## Design

- **No build tools** — Everything in a single `index.html` (36 KB), inline CSS and JavaScript
- **Color palette**: Warm paper (`#f5f0e6`), ink (`#1a1612`), soft gold (`#b8923c`)
- **Typography**: Playfair Display + Noto Serif SC (headings), Inter (body), JetBrains Mono (data)
- **Responsive**: Mobile-first, with 48px minimum touch targets
- **Safe**: All JS wrapped in try-catch to survive edge-case failures (canvas-unfriendly webviews, CDN outages, etc.)

---

## Project Structure

```
song-incense-database/
├── data/
│   ├── all_recipes.json          # Chinese data (378 formulas)
│   ├── all_recipes_en.json       # English data (378 formulas)
│   ├── ingredient_index.json     # Ingredient index
│   ├── chenshi_v1-4.json        # Individual source extracts
│   ├── xiangcheng_raw.json       # Compendium of Incense extract
│   ├── hongchu_xiangpu.json      # Hong Chu's manual
│   ├── zunsheng_raw.json         # Eight Discourses extract
│   ├── jujia_raw.json            # Household arts extract
│   ├── shilin_raw.json           # Forest of Affairs extract
│   ├── zhongguo_raw.json         # Modern compilation extract
│   └── xiangzubiji_raw.json      # Ancestor of Incense extract
├── scripts/
│   ├── extract_recipes.py        # Recipe extractor (per source)
│   ├── batch_extract.py          # Batch extraction + merge
│   ├── normalize_validate.py     # Normalization + validation
│   ├── build_translations.py     # Translation glossary builder
│   ├── translate_fangs.py        # Formula name translator
│   ├── build_en_data.py          # English dataset pipeline
│   └── fix_missing_ingredients.py # Repair empty ingredient lists
├── README.md
└── index.html                    # Web application (single file)
```

---

## Contributing

Contributions are welcome! Areas where help is most needed:

- **Ingredient identification** — Some rare materials may have variant or uncertain English identifications. If you spot one, please open an issue.
- **Additional texts** — If you know of a classical incense text not included here, I'd love to add it.
- **Translation corrections** — Formula names, ingredient properties, and usage descriptions are always open to refinement.
- **Data quality** — Flag any parsing errors or inconsistencies you find.

Please [open an issue](https://github.com/william20010113-cmyk/changhaoli.com/issues) or submit a pull request.

---

## Limitations

- **One empty entry**: "Incense-Burning Method" (烧香法) is a general guide, not a recipe — no ingredient list.
- **Variable source quality**: Some editions contain copyist errors or ambiguous dosage descriptions. Notes flag these where possible.
- **Not a medical reference**: Ingredient properties are recorded per the source texts and TCM. This is a scholarly resource, not a safety guide. Some ingredients may be toxic — always consult a professional.
- **Translation is interpretive**: Ingredient names for rare materials represent the best available judgment. Alternate identifications are noted where relevant.

---

## Built With

- [anime.js](https://animejs.com/) — Page load animations (loaded via CDN)
- [Cloudflare Pages](https://pages.cloudflare.com/) — Hosting
- [Ghostscript](https://www.ghostscript.com/) — PDF compression for large reference documents
- Google Fonts — Playfair Display, Noto Serif SC, Inter, JetBrains Mono

---

## License

The classical source texts are in the public domain. The curated data and English translations are made available for scholarly and educational use.

---

## Author

**Changhao Li** — [changhaoli.com](https://changhaoli.com)

*Questions, corrections, and contributions are welcome.*
