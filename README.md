<div align="center">

# 🔍 ECC Skills Explorer

### Browse **136+ Everything Claude Code** skills with a modern bilingual UI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![HTML5](https://img.shields.io/badge/HTML5-Single_File-E34F26?logo=html5&logoColor=white)](#)
[![Bilingual](https://img.shields.io/badge/Language-AR_|_EN-00d9ff)](#)

**English** | [العربية](#-متصفح-مهارات-ecc)

<img src="https://img.shields.io/badge/Skills-136+-00d9ff?style=for-the-badge" /> <img src="https://img.shields.io/badge/Categories-15-7c3aed?style=for-the-badge" /> <img src="https://img.shields.io/badge/Dependencies-Zero-10b981?style=for-the-badge" />

</div>

---

## ✨ Features
![Untitled](https://github.com/user-attachments/assets/140567a4-8e07-4870-ad9f-077ab1e4dd53)


![2](https://github.com/user-attachments/assets/8b0be87f-2832-4a5c-8d4a-e2a3bf783b79)


- 🌙 **Dark theme** with category-colored accents
- 🌐 **Bilingual UI** — switch between Arabic and English with one click
- 🔎 **Full-text search** across skill names, IDs, and descriptions
- 📂 **15 categories** — AI & Agents, Backend, Frontend, Testing, Python, Go, Rust, and more
- 📋 **Detail panel** — description, usage triggers, sections, and install command
- ⌨️ **Keyboard shortcuts** — `/` to search, `Esc` to close
- 📱 **Fully responsive** — works on mobile, tablet, and desktop

---

## 🚀 Two Ways to Explore

| Mode | File | How to Run |
|------|------|------------|
| **Static** (offline) | `ecc_skills_browser.html` | Double-click to open in any browser |
| **Live** (reads from disk) | `ecc_browser.py` | `python ecc_browser.py skills` |

### 📄 HTML — Static Browser

Just open the file in your browser. No server, no install, no dependencies. Skill data is embedded inside.

```bash
# macOS
open ecc_skills_browser.html

# Linux
xdg-open ecc_skills_browser.html

# Windows — just double-click the file
```

### 🐍 Python — Live Browser

Reads `SKILL.md` files directly from disk. Add or edit a skill, press **↻ Reload**, and it appears instantly.

```bash
# Auto-detect skills/ in current directory
python ecc_browser.py

# Specify path
python ecc_browser.py path/to/skills

# Custom port
python ecc_browser.py skills --port 8080
```

Opens `http://127.0.0.1:5500` automatically. Press `Ctrl+C` to stop.

**Extra features in Python edition:**
- 🟢 **LIVE** indicator — always reading from disk
- 📄 **View full SKILL.md** content inside the detail panel
- ↻ **Reload** without restarting the server

---

## 📊 Skill Categories

| Icon | Category | Count |
|------|----------|-------|
| 🧠 | AI & Agents | 16 |
| ⚙️ | Backend / API | 9 |
| 🎨 | Frontend / UI | 8 |
| 🛡️ | Testing / Security | 8 |
| 🤖 | Android / Kotlin | 8 |
| 🐍 | Python / Django | 7 |
| ☕ | Java / Spring | 6 |
| 🍎 | Swift / iOS | 5 |
| 🐹 | Go | 2 |
| ⚙️ | Rust | 2 |
| 🏥 | Healthcare | 4 |
| 📝 | Content / Media | 11 |
| 🔧 | Tools / DevOps | 15 |
| 📦 | Other | 35 |

---

## 📁 Project Structure

```
claude-code-skills-explorer/
├── ecc_skills_browser.html   # Static web UI (single file, zero deps)
├── ecc_browser.py            # Live web UI (Python 3.10+, zero deps)
└── README.md
```

---

## 📜 License

MIT — Built on top of [Everything Claude Code](https://github.com/affaan-m/everything-claude-code) by [@affaan-m](https://github.com/affaan-m).

---

<div align="center" dir="rtl">

## 🔍 متصفح مهارات ECC

### تصفح **+136 مهارة** لـ Everything Claude Code بواجهة حديثة ثنائية اللغة

[English](#-ecc-skills-explorer) | **العربية**

</div>

<div dir="rtl">

## ✨ المميزات

- 🌙 **ثيم داكن** مع ألوان مميزة لكل فئة
- 🌐 **واجهة ثنائية اللغة** — تبديل بين العربية والإنجليزية بنقرة واحدة
- 🔎 **بحث شامل** في أسماء المهارات والأوصاف والمعرّفات
- 📂 **15 فئة** — ذكاء اصطناعي، خلفية، واجهة أمامية، اختبار، بايثون، والمزيد
- 📋 **لوحة تفاصيل** — الوصف، حالات الاستخدام، الأقسام، وأمر التثبيت
- ⌨️ **اختصارات لوحة المفاتيح** — `/` للبحث، `Esc` للإغلاق
- 📱 **متجاوب بالكامل** — يعمل على الهاتف والتابلت والكمبيوتر

---

## 🚀 طريقتان للتصفح

| الوضع | الملف | طريقة التشغيل |
|-------|-------|---------------|
| **ثابت** (بدون إنترنت) | `ecc_skills_browser.html` | افتحه بنقرة مزدوجة في المتصفح |
| **حي** (يقرأ من القرص) | `ecc_browser.py` | `python ecc_browser.py skills` |

### 📄 HTML — المتصفح الثابت

افتح الملف مباشرة في المتصفح. بدون سيرفر، بدون تثبيت، بدون أي متطلبات. البيانات مدمجة داخل الملف.

### 🐍 بايثون — المتصفح الحي

يقرأ ملفات `SKILL.md` مباشرة من القرص. أضف أو عدّل مهارة، اضغط **↻ إعادة تحميل**، وتظهر فوراً.

```bash
# اكتشاف تلقائي لمجلد skills/
python ecc_browser.py

# تحديد المسار
python ecc_browser.py path/to/skills

# تغيير المنفذ
python ecc_browser.py skills --port 8080
```

يفتح `http://127.0.0.1:5500` تلقائياً. اضغط `Ctrl+C` للإيقاف.

**ميزات إضافية في نسخة بايثون:**
- 🟢 **مؤشر LIVE** — يقرأ من القرص دائماً
- 📄 **عرض محتوى SKILL.md الكامل** داخل لوحة التفاصيل
- ↻ **إعادة تحميل** بدون إعادة تشغيل السيرفر

---

## 📊 فئات المهارات

| الرمز | الفئة | العدد |
|-------|-------|-------|
| 🧠 | الذكاء والوكلاء | 16 |
| ⚙️ | الخلفية والـ API | 9 |
| 🎨 | الواجهة الأمامية | 8 |
| 🛡️ | الاختبار والأمان | 8 |
| 🤖 | أندرويد / كوتلن | 8 |
| 🐍 | بايثون / جانغو | 7 |
| ☕ | جافا / سبرنغ | 6 |
| 🍎 | سويفت / iOS | 5 |
| 🐹 | Go | 2 |
| ⚙️ | رست | 2 |
| 🏥 | الرعاية الصحية | 4 |
| 📝 | المحتوى والميديا | 11 |
| 🔧 | أدوات / DevOps | 15 |
| 📦 | أخرى | 35 |

---

## 📜 الرخصة

MIT — مبني على [Everything Claude Code](https://github.com/affaan-m/everything-claude-code) بواسطة [@affaan-m](https://github.com/affaan-m).

</div>
