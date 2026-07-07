# MLBBVision

> AI-Powered Mobile Legends: Bang Bang Post-Game Data Extraction

MLBBVision adalah sistem Computer Vision berbasis Artificial Intelligence yang digunakan untuk mengekstrak data hasil pertandingan Mobile Legends: Bang Bang (MLBB) dari screenshot post-game secara otomatis.

Project ini menggabungkan beberapa metode AI:

- Hero Classification
- Item Classification
- OCR (Optical Character Recognition)
- Image Preprocessing
- JSON Builder

Hasil akhirnya berupa file JSON yang dapat langsung digunakan oleh Overlay Tournament, Website, Dashboard, ataupun aplikasi statistik pertandingan.

---

# Features

## Hero Detection

Menggunakan CNN untuk mengenali hero setiap player.

Output:

```json
{
    "hero": "Hayabusa"
}
```

---

## Item Detection

Menggunakan CNN untuk mengenali seluruh item player.

Output:

```json
"itemlist": [
    "War Axe",
    "Hunter Strike",
    "Blade of Despair",
    "Immortality",
    "Malefic Roar",
    "Rose Gold Meteor"
]
```

---

## OCR Detection

Mengekstrak:

- Player Name
- Gold
- Level
- KDA
- Match Duration
- Team Score

---

## Automatic JSON Builder

Semua hasil AI akan digabung menjadi satu file JSON.

Contoh:

```json
{
    "game_duration": "20:12",
    "game_number": "2",
    "winmatches": "blue",
    "teamdata": {

    }
}
```

---

# Project Structure

```
MLBBVision
│
├── crop_engine/
│   └── crop_engine.py
│
├── hero_classifier/
│   ├── dataset.py
│   ├── model.py
│   ├── train.py
│   ├── predict.py
│   └── config.py
│
├── item_classifier/
│   ├── dataset.py
│   ├── model.py
│   ├── train.py
│   ├── predict.py
│   └── config.py
│
├── ocr_engine/
│   ├── engine.py
│   ├── preprocess.py
│   ├── parser.py
│   ├── predict.py
│   └── config.py
│
├── pipeline/
│   ├── parser.py
│   ├── builder.py
│   └── postgame.py
│
├── layout_editor/
│   └── coordinates.json
│
├── output/
│
├── test/
│
├── main.py
│
└── README.md
```

---

# Pipeline

```
Screenshot
        │
        ▼
Crop Engine
        │
        ├──────────────┐
        │              │
        ▼              ▼
 Hero AI         Item AI
        │              │
        └──────┬───────┘
               │
               ▼
           OCR Engine
               │
               ▼
        PostGame Builder
               │
               ▼
         postgame.json
```

---

# Output JSON

```json
{
    "game_duration": "20:12",
    "game_number": "2",
    "winmatches": "blue",
    "teamdata": {
        "blueteam": {
            "teamname": "BLUE TEAM",
            "score": "1",
            "logo": "",
            "totalgold": 73500,
            "turret": 0,
            "lord": 0,
            "turtle": 0,
            "playerlist": [
                {
                    "name": "Player",
                    "hero": "Hayabusa",
                    "level": "15",
                    "KDA": "7/2/11",
                    "gold": 15420,
                    "spell": "",
                    "banhero": "",
                    "itemlist": [
                        "...",
                        "...",
                        "...",
                        "...",
                        "...",
                        "..."
                    ],
                    "lane": ""
                }
            ]
        }
    }
}
```

---

# AI Modules

| Module | Status |
|---------|--------|
| Crop Engine | ✅ |
| Hero Classifier | ✅ |
| Item Classifier | ✅ |
| OCR Engine | ✅ |
| Hero OCR | ✅ |
| Gold OCR | ✅ |
| Level OCR | ✅ |
| KDA OCR | ✅ |
| Name OCR | ✅ |
| Team Score OCR | ✅ |
| Match Duration OCR | ✅ |
| JSON Builder | ✅ |

---

# OCR Modules

Current OCR supports:

- Gold
- Level
- KDA
- Player Name
- Match Duration
- Team Score

---

# Hero Classifier

Input

```
Hero Icon
```

↓

Output

```
Hayabusa
```

---

# Item Classifier

Input

```
Item Icon
```

↓

Output

```
Blade of Despair
```

---

# Crop Engine

Crop Engine membaca seluruh ROI berdasarkan file:

```
layout_editor/coordinates.json
```

Kemudian menghasilkan seluruh crop secara otomatis.

Contoh:

```
hero_blue_1
hero_blue_2

item1_blue_1
item2_blue_1

gold_blue_1

kda_blue_1

name_blue_1

...
```

---

# Run

```bash
python main.py
```

---

# Output

```
output/
└── json/
    └── postgame.json
```

---

# Dependencies

- Python 3.10+
- PyTorch
- OpenCV
- Albumentations
- NumPy
- EasyOCR

Install:

```bash
pip install -r requirements.txt
```

---

# Roadmap

## Current

- [x] Crop Engine
- [x] Hero Classification
- [x] Item Classification
- [x] OCR Engine
- [x] JSON Builder

## Next

- [ ] Spell Classification
- [ ] Lane Classification
- [ ] Ban Hero Detection
- [ ] Team Logo Detection
- [ ] Auto MVP Detection
- [ ] Auto Win Detection
- [ ] Draft Pick Detection

---

# Author

**Dikri Fauzan Amrulloh**

GitHub:
https://github.com/dikrifzn

---

# License

This project is licensed under the MIT License.