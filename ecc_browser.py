#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║   ECC Skills Browser — Web UI (Python Edition)       ║
║   يقرأ ملفات SKILL.md مباشرة ويعرضها في المتصفح     ║
╚══════════════════════════════════════════════════════╝

Usage:
    python ecc_browser.py [path/to/skills] [--port 5500]

Opens a local web server with a full GUI in your browser.
Reads SKILL.md files directly — always shows the latest data.
Zero external dependencies (uses only Python standard library).
"""

import http.server
import json
import os
import re
import socket
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# ─────────────────────── Skill Category Mapping ───────────────────────

SKILL_CATEGORIES = {
    "android-clean-architecture": "android",
    "compose-multiplatform-patterns": "android",
    "kotlin-coroutines-flows": "android",
    "kotlin-exposed-patterns": "android",
    "kotlin-ktor-patterns": "android",
    "kotlin-patterns": "android",
    "kotlin-testing": "android",
    "foundation-models-on-device": "android",
    "api-design": "backend",
    "backend-patterns": "backend",
    "clickhouse-io": "backend",
    "coding-standards": "backend",
    "database-migrations": "backend",
    "deployment-patterns": "backend",
    "docker-patterns": "backend",
    "git-workflow": "backend",
    "postgres-patterns": "backend",
    "browser-qa": "frontend",
    "bun-runtime": "frontend",
    "design-system": "frontend",
    "e2e-testing": "frontend",
    "frontend-patterns": "frontend",
    "frontend-slides": "frontend",
    "nextjs-turbopack": "frontend",
    "nuxt4-patterns": "frontend",
    "agent-eval": "ai_agents",
    "agent-harness-construction": "ai_agents",
    "agent-payment-x402": "ai_agents",
    "agentic-engineering": "ai_agents",
    "ai-first-engineering": "ai_agents",
    "ai-regression-testing": "ai_agents",
    "autonomous-loops": "ai_agents",
    "claude-api": "ai_agents",
    "claude-devfleet": "ai_agents",
    "continuous-agent-loop": "ai_agents",
    "cost-aware-llm-pipeline": "ai_agents",
    "deep-research": "ai_agents",
    "dmux-workflows": "ai_agents",
    "enterprise-agent-ops": "ai_agents",
    "eval-harness": "ai_agents",
    "iterative-retrieval": "ai_agents",
    "benchmark": "testing",
    "canary-watch": "testing",
    "click-path-audit": "testing",
    "safety-guard": "testing",
    "security-review": "testing",
    "security-scan": "testing",
    "tdd-workflow": "testing",
    "verification-loop": "testing",
    "django-patterns": "python",
    "django-security": "python",
    "django-tdd": "python",
    "django-verification": "python",
    "python-patterns": "python",
    "python-testing": "python",
    "pytorch-patterns": "python",
    "golang-patterns": "go",
    "golang-testing": "go",
    "java-coding-standards": "java_spring",
    "jpa-patterns": "java_spring",
    "springboot-patterns": "java_spring",
    "springboot-security": "java_spring",
    "springboot-tdd": "java_spring",
    "springboot-verification": "java_spring",
    "liquid-glass-design": "swift_ios",
    "swift-actor-persistence": "swift_ios",
    "swift-concurrency-6-2": "swift_ios",
    "swift-protocol-di-testing": "swift_ios",
    "swiftui-patterns": "swift_ios",
    "rust-patterns": "rust",
    "rust-testing": "rust",
    "healthcare-cdss-patterns": "healthcare",
    "healthcare-emr-patterns": "healthcare",
    "healthcare-eval-harness": "healthcare",
    "healthcare-phi-compliance": "healthcare",
    "article-writing": "content",
    "content-engine": "content",
    "crosspost": "content",
    "exa-search": "content",
    "fal-ai-media": "content",
    "investor-materials": "content",
    "investor-outreach": "content",
    "market-research": "content",
    "video-editing": "content",
    "videodb": "content",
    "x-api": "content",
    "architecture-decision-records": "tools",
    "ck": "tools",
    "codebase-onboarding": "tools",
    "configure-ecc": "tools",
    "context-budget": "tools",
    "continuous-learning": "tools",
    "continuous-learning-v2": "tools",
    "documentation-lookup": "tools",
    "mcp-server-patterns": "tools",
    "prompt-optimizer": "tools",
    "repo-scan": "tools",
    "rules-distill": "tools",
    "search-first": "tools",
    "skill-stocktake": "tools",
    "strategic-compact": "tools",
    "token-budget-advisor": "tools",
}


# ─────────────────────── Skill Parser ───────────────────────

def scan_skills(skills_dir: Path) -> list:
    """Parse all SKILL.md files and return JSON-serializable list."""
    skills = []
    if not skills_dir.exists():
        return skills

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8", errors="replace")

        desc_match = re.search(r"^description:\s*(.+?)$", content, re.MULTILINE)
        desc = desc_match.group(1).strip().strip('"') if desc_match else ""
        if desc.startswith(">"):
            desc = ""

        title_match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else skill_dir.name.replace("-", " ").title()

        when_match = re.search(r"## When to.+?\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        when_text = when_match.group(1).strip()[:500] if when_match else ""

        sections = re.findall(r"^## (.+?)$", content, re.MULTILINE)

        skills.append({
            "id": skill_dir.name,
            "title": title,
            "desc": desc[:300],
            "when": when_text,
            "cat": SKILL_CATEGORIES.get(skill_dir.name, "other"),
            "lines": content.count("\n"),
            "sections": sections[:8],
            "content": content,
        })

    return skills


def find_skills_dir():
    """Auto-detect the skills/ directory."""
    cwd = Path.cwd()
    for candidate in [cwd / "skills", cwd / "everything-claude-code-main" / "skills", cwd]:
        if candidate.exists() and any(
            (candidate / d / "SKILL.md").exists()
            for d in os.listdir(candidate)
            if (candidate / d).is_dir()
        ):
            return candidate
    return None


# ─────────────────────── HTML Template ───────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ECC Skills Browser — Live</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Cairo:wght@400;600;700;900&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {
  --bg:#06080c;--surface:#0e1117;--surface2:#151921;--surface3:#1c212b;
  --border:#1e2530;--border-hover:#2a3140;
  --accent:#00d9ff;--accent-glow:rgba(0,217,255,.15);--accent2:#7c3aed;--accent3:#10b981;
  --text:#e2e8f0;--text2:#94a3b8;--muted:#64748b;--danger:#ef4444;
  --r:12px;--rs:8px;--rx:6px;
  --mono:'JetBrains Mono',monospace;--sans:'Cairo','Inter',sans-serif;--sans-en:'Inter','Cairo',sans-serif;
  --tr:.2s cubic-bezier(.4,0,.2,1);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh;overflow-x:hidden;-webkit-font-smoothing:antialiased}
body[dir="ltr"]{font-family:var(--sans-en)}
::selection{background:var(--accent);color:var(--bg)}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}

header{background:linear-gradient(180deg,rgba(14,17,23,.97),rgba(6,8,12,.97));border-bottom:1px solid var(--border);padding:0 28px;height:64px;display:flex;align-items:center;gap:16px;position:sticky;top:0;z-index:100;backdrop-filter:blur(24px)}
.logo{display:flex;align-items:center;gap:10px;flex-shrink:0}
.logo-icon{width:38px;height:38px;background:linear-gradient(135deg,var(--accent),var(--accent2));border-radius:10px;display:grid;place-items:center;font-size:14px;font-weight:800;color:#fff;font-family:var(--mono);box-shadow:0 0 24px rgba(0,217,255,.25)}
.logo-text h1{font-size:17px;font-weight:800;color:#fff;line-height:1.2}.logo-text span{font-size:11px;color:var(--muted);font-family:var(--mono)}
.live-badge{display:flex;align-items:center;gap:6px;background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.25);border-radius:var(--rx);padding:4px 10px;font-size:10px;font-family:var(--mono);color:var(--accent3)}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--accent3);box-shadow:0 0 6px var(--accent3);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.search-box{flex:1;max-width:380px;position:relative;margin:0 auto 0 16px}
[dir="ltr"] .search-box{margin:0 16px 0 auto}
.search-box input{width:100%;background:var(--surface2);border:1px solid var(--border);border-radius:var(--rs);padding:9px 14px 9px 38px;color:var(--text);font-family:inherit;font-size:13px;outline:none;transition:var(--tr)}
[dir="rtl"] .search-box input{padding:9px 38px 9px 14px}
.search-box input:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow)}
.search-box input::placeholder{color:var(--muted)}
.search-box svg{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--muted);pointer-events:none}
[dir="rtl"] .search-box svg{left:auto;right:12px}
.header-actions{display:flex;align-items:center;gap:8px;flex-shrink:0}
.stat-chip{background:var(--surface2);border:1px solid var(--border);border-radius:var(--rx);padding:5px 12px;font-size:11px;font-family:var(--mono);color:var(--muted);white-space:nowrap}
.stat-chip strong{color:var(--accent);font-weight:600}
.btn{background:var(--surface2);border:1px solid var(--border);border-radius:var(--rx);padding:5px 10px;font-size:12px;color:var(--text2);cursor:pointer;font-family:var(--mono);transition:var(--tr)}
.btn:hover{border-color:var(--accent);color:var(--accent)}

.app{display:flex;height:calc(100vh - 64px)}
.sidebar{width:260px;background:var(--surface);border-inline-end:1px solid var(--border);overflow-y:auto;padding:14px 0;flex-shrink:0}
.sidebar-label{font-size:10px;font-family:var(--mono);color:var(--muted);text-transform:uppercase;letter-spacing:1.5px;padding:4px 18px 10px}
.cat-btn{display:flex;align-items:center;gap:10px;padding:9px 18px;cursor:pointer;border:none;background:transparent;color:var(--text2);width:100%;text-align:inherit;font-family:inherit;font-size:13px;transition:var(--tr);border-inline-start:3px solid transparent}
.cat-btn:hover{background:var(--surface2);color:var(--text)}
.cat-btn.active{background:var(--surface2);color:var(--accent);border-inline-start-color:var(--accent)}
.cat-icon{font-size:15px;flex-shrink:0;line-height:1}
.cat-count{margin-inline-start:auto;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1px 7px;font-size:10px;font-family:var(--mono);color:var(--muted);min-width:24px;text-align:center}
.cat-btn.active .cat-count{border-color:rgba(0,217,255,.3);color:var(--accent);background:var(--accent-glow)}

.main{flex:1;overflow-y:auto;padding:20px 24px}
.results-bar{display:flex;align-items:center;gap:10px;margin-bottom:14px;font-size:12px;color:var(--muted);font-family:var(--mono)}
.results-bar strong{color:var(--accent)}
.filter-chip{background:var(--accent-glow);border:1px solid rgba(0,217,255,.25);border-radius:var(--rx);padding:2px 10px;font-size:11px;color:var(--accent);display:inline-flex;align-items:center;gap:4px}
.sort-btn{margin-inline-start:auto;background:var(--surface2);border:1px solid var(--border);border-radius:var(--rx);padding:4px 10px;font-size:11px;font-family:var(--mono);color:var(--muted);cursor:pointer;transition:var(--tr)}
.sort-btn:hover{border-color:var(--accent);color:var(--accent)}

.skills-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.skill-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:18px;cursor:pointer;transition:var(--tr);position:relative;overflow:hidden}
.skill-card::after{content:'';position:absolute;top:0;inset-inline-start:0;width:50px;height:2px;background:var(--card-accent,var(--accent));transition:width var(--tr)}
.skill-card:hover{border-color:var(--card-accent,var(--accent));transform:translateY(-1px);box-shadow:0 4px 16px rgba(0,0,0,.4);background:var(--surface2)}
.skill-card:hover::after{width:100%}
.card-head{display:flex;align-items:flex-start;gap:10px;margin-bottom:8px}
.card-icon{width:34px;height:34px;border-radius:var(--rs);background:var(--accent-glow);border:1px solid rgba(0,217,255,.15);display:grid;place-items:center;font-size:15px;flex-shrink:0}
.card-title{font-size:14px;font-weight:700;color:#fff;line-height:1.35}.card-id{font-size:10px;font-family:var(--mono);color:var(--muted);margin-top:1px}
.card-desc{font-size:12.5px;color:var(--text2);line-height:1.55;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card-foot{display:flex;align-items:center;gap:6px;margin-top:10px}
.tag{border:1px solid var(--border);border-radius:var(--rx);padding:2px 7px;font-size:10px;font-family:var(--mono);color:var(--muted);background:var(--surface2)}
.tag-cat{border-color:var(--card-accent,var(--border));color:var(--card-accent,var(--muted))}
.lines-label{margin-inline-start:auto;font-size:10px;font-family:var(--mono);color:var(--border-hover)}

.detail-panel{width:500px;background:var(--surface);border-inline-start:1px solid var(--border);display:none;flex-direction:column;flex-shrink:0}
.detail-panel.open{display:flex}
.detail-head{padding:18px 22px;border-bottom:1px solid var(--border);display:flex;align-items:flex-start;gap:12px}
.detail-icon{width:48px;height:48px;border-radius:var(--r);background:var(--accent-glow);border:1px solid rgba(0,217,255,.15);display:grid;place-items:center;font-size:22px;flex-shrink:0}
.detail-title h2{font-size:17px;font-weight:800;color:#fff;line-height:1.3}
.detail-title code{font-family:var(--mono);font-size:11px;color:var(--accent);background:var(--accent-glow);padding:2px 8px;border-radius:4px;display:inline-block;margin-top:4px}
.close-detail{margin-inline-start:auto;background:var(--surface2);border:1px solid var(--border);border-radius:var(--rs);color:var(--muted);padding:6px 10px;cursor:pointer;font-size:11px;font-family:inherit;transition:var(--tr)}
.close-detail:hover{border-color:var(--danger);color:var(--danger)}
.detail-body{flex:1;overflow-y:auto;padding:18px 22px}
.detail-section{margin-bottom:18px}
.section-label{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:var(--muted);font-family:var(--mono);margin-bottom:8px;display:flex;align-items:center;gap:8px}
.section-label::after{content:'';flex:1;height:1px;background:var(--border)}
.detail-desc{font-size:13.5px;color:var(--text);line-height:1.7}
.when-box{background:var(--surface2);border:1px solid var(--border);border-inline-start:3px solid var(--accent3);border-radius:var(--rs);padding:12px 14px;font-size:12.5px;color:var(--text);line-height:1.65;white-space:pre-wrap}
.chips-row{display:flex;flex-wrap:wrap;gap:5px}
.chip{background:var(--surface2);border:1px solid var(--border);border-radius:var(--rx);padding:4px 10px;font-size:11px;font-family:var(--mono);color:var(--text2)}
.install-box{background:var(--bg);border:1px solid var(--border);border-radius:var(--rs);padding:14px 16px;font-family:var(--mono);font-size:12px;color:var(--accent3);position:relative;direction:ltr;text-align:left;line-height:1.8;overflow-x:auto}
.copy-btn{position:absolute;top:8px;right:8px;background:var(--surface2);border:1px solid var(--border);border-radius:var(--rx);color:var(--muted);padding:3px 9px;font-size:10px;font-family:var(--mono);cursor:pointer;transition:var(--tr)}
.copy-btn:hover{border-color:var(--accent);color:var(--accent)}
.meta-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.meta-card{background:var(--surface2);border:1px solid var(--border);border-radius:var(--rs);padding:10px 12px}
.meta-label{font-size:10px;font-family:var(--mono);color:var(--muted);margin-bottom:3px}.meta-value{font-size:14px;font-weight:700;color:#fff}
.content-viewer{background:var(--bg);border:1px solid var(--border);border-radius:var(--rs);padding:16px;font-family:var(--mono);font-size:11.5px;color:var(--text2);line-height:1.7;white-space:pre-wrap;direction:ltr;text-align:left;max-height:500px;overflow-y:auto;margin-top:8px}
.view-btn{background:var(--surface2);border:1px solid var(--border);border-radius:var(--rx);padding:6px 14px;font-size:12px;font-family:var(--mono);color:var(--accent);cursor:pointer;transition:var(--tr);margin-top:8px;display:inline-block}
.view-btn:hover{border-color:var(--accent);background:var(--accent-glow)}
.empty-state{text-align:center;padding:80px 20px;color:var(--muted);grid-column:1/-1}
.empty-state .icon{font-size:40px;margin-bottom:12px;display:block;opacity:.5}
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.skill-card{animation:fadeUp .25s ease both}
@media(max-width:960px){.sidebar{display:none}.detail-panel{position:fixed;inset:64px 0 0;width:100%;z-index:90}}
@media(max-width:640px){header{padding:0 14px;gap:10px}.logo-text span,.live-badge span{display:none}.main{padding:14px}.skills-grid{grid-template-columns:1fr}.stat-chip{display:none}}
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-icon">ECC</div>
    <div class="logo-text"><h1>Skills Browser</h1><span>Everything Claude Code</span></div>
  </div>
  <div class="live-badge"><div class="live-dot"></div><span>LIVE</span></div>
  <div class="search-box">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input type="text" id="searchInput" placeholder="ابحث في المهارات..." oninput="filterSkills()">
  </div>
  <div class="header-actions">
    <div class="stat-chip"><strong id="totalCount">0</strong> <span data-i18n="skills">مهارة</span></div>
    <div class="stat-chip"><strong id="visibleCount">0</strong> <span data-i18n="visible">ظاهر</span></div>
    <button class="btn" onclick="reloadSkills()" title="Reload from disk">↻ Reload</button>
    <button class="btn" onclick="toggleLang()">EN / عر</button>
  </div>
</header>

<div class="app">
  <nav class="sidebar" id="sidebar"></nav>
  <main class="main">
    <div class="results-bar">
      <strong id="resultCount">0</strong> <span data-i18n="results">نتيجة</span>
      <span id="activeFilter"></span>
      <button class="sort-btn" id="sortBtn" onclick="toggleSort()">A→Z</button>
    </div>
    <div class="skills-grid" id="skillsGrid"></div>
  </main>
  <aside class="detail-panel" id="detailPanel">
    <div class="detail-head" id="detailHead"></div>
    <div class="detail-body" id="detailBody"></div>
  </aside>
</div>

<script>
const CATEGORIES={all:{icon:'🗂️',ar:'جميع المهارات',en:'All Skills',color:'#00d9ff'},ai_agents:{icon:'🧠',ar:'الذكاء والوكلاء',en:'AI & Agents',color:'#a78bfa'},backend:{icon:'⚙️',ar:'الخلفية والـ API',en:'Backend / API',color:'#6366f1'},frontend:{icon:'🎨',ar:'الواجهة الأمامية',en:'Frontend / UI',color:'#f472b6'},testing:{icon:'🛡️',ar:'الاختبار والأمان',en:'Testing / Security',color:'#f59e0b'},android:{icon:'🤖',ar:'أندرويد / كوتلن',en:'Android / Kotlin',color:'#3ddc84'},python:{icon:'🐍',ar:'بايثون / جانغو',en:'Python / Django',color:'#fbbf24'},java_spring:{icon:'☕',ar:'جافا / سبرنغ',en:'Java / Spring',color:'#f97316'},swift_ios:{icon:'🍎',ar:'سويفت / iOS',en:'Swift / iOS',color:'#ff6b6b'},rust:{icon:'⚙️',ar:'رست',en:'Rust',color:'#ce422b'},go:{icon:'🐹',ar:'Go',en:'Go',color:'#00add8'},healthcare:{icon:'🏥',ar:'الرعاية الصحية',en:'Healthcare',color:'#10b981'},content:{icon:'📝',ar:'المحتوى والميديا',en:'Content / Media',color:'#06b6d4'},tools:{icon:'🔧',ar:'أدوات / DevOps',en:'Tools / DevOps',color:'#8b5cf6'},other:{icon:'📦',ar:'أخرى',en:'Other',color:'#64748b'}};
const I18N={ar:{skills:'مهارة',visible:'ظاهر',results:'نتيجة',categories:'الفئات',search:'ابحث في المهارات...',noResults:'لا توجد نتائج',close:'✕ إغلاق',description:'الوصف',whenToUse:'متى تُستخدم',sections:'الأقسام',fileInfo:'معلومات الملف',lines:'عدد السطور',category:'الفئة',install:'كيفية الاستخدام',copy:'نسخ',copied:'✓ تم',noDesc:'لا يوجد وصف',line:'سطر',fullContent:'المحتوى الكامل',viewFull:'📄 عرض SKILL.md كاملاً',hideFull:'إخفاء'},en:{skills:'skills',visible:'visible',results:'results',categories:'Categories',search:'Search skills...',noResults:'No results found',close:'✕ Close',description:'Description',whenToUse:'When to Use',sections:'Sections',fileInfo:'File Info',lines:'Lines',category:'Category',install:'Installation',copy:'Copy',copied:'✓ Done',noDesc:'No description',line:'lines',fullContent:'Full Content',viewFull:'📄 View full SKILL.md',hideFull:'Hide'}};

let SKILLS=[], lang='ar', currentCat='all', searchTerm='', sortAZ=false;
const $=id=>document.getElementById(id), t=k=>I18N[lang][k]||k;
const catLabel=c=>CATEGORIES[c]?.[lang]||c, catColor=c=>CATEGORIES[c]?.color||'#64748b', catIcon=c=>CATEGORIES[c]?.icon||'📦';

function toggleLang(){lang=lang==='ar'?'en':'ar';const d=lang==='ar'?'rtl':'ltr';document.documentElement.lang=lang;document.documentElement.dir=d;document.body.dir=d;$('searchInput').placeholder=t('search');$('searchInput').dir=d;document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=t(el.dataset.i18n)});renderSidebar();renderSkills()}
async function reloadSkills(){try{const r=await fetch('/api/skills');SKILLS=await r.json();renderSidebar();renderSkills();console.log('Reloaded',SKILLS.length,'skills')}catch(e){console.error('Reload failed',e)}}
function renderSidebar(){const counts={};SKILLS.forEach(s=>{counts[s.cat]=(counts[s.cat]||0)+1});let h=`<div class="sidebar-label">${t('categories')}</div>`;for(const[k,c]of Object.entries(CATEGORIES)){const n=k==='all'?SKILLS.length:(counts[k]||0);if(k!=='all'&&n===0)continue;h+=`<button class="cat-btn ${currentCat===k?'active':''}" onclick="selectCat('${k}')"><span class="cat-icon">${c.icon}</span>${catLabel(k)}<span class="cat-count">${n}</span></button>`}$('sidebar').innerHTML=h}
function selectCat(c){currentCat=c;renderSidebar();renderSkills();closeDetail()}
function filterSkills(){searchTerm=$('searchInput').value.toLowerCase();renderSkills()}
function toggleSort(){sortAZ=!sortAZ;$('sortBtn').textContent=sortAZ?'Z→A':'A→Z';renderSkills()}
function getFiltered(){let l=SKILLS;if(currentCat!=='all')l=l.filter(s=>s.cat===currentCat);if(searchTerm)l=l.filter(s=>s.title.toLowerCase().includes(searchTerm)||s.id.toLowerCase().includes(searchTerm)||s.desc.toLowerCase().includes(searchTerm));if(sortAZ)l=[...l].sort((a,b)=>a.title.localeCompare(b.title));return l}
function renderSkills(){const f=getFiltered();$('totalCount').textContent=SKILLS.length;$('visibleCount').textContent=f.length;$('resultCount').textContent=f.length;$('activeFilter').innerHTML=currentCat!=='all'?`<span class="filter-chip">${catIcon(currentCat)} ${catLabel(currentCat)}</span>`:'';if(!f.length){$('skillsGrid').innerHTML=`<div class="empty-state"><span class="icon">🔍</span><p>${t('noResults')}</p></div>`;return}$('skillsGrid').innerHTML=f.map((s,i)=>{const c=catColor(s.cat);return`<div class="skill-card" style="--card-accent:${c};animation-delay:${i*.015}s" onclick="openDetail('${s.id}')"><div class="card-head"><div class="card-icon" style="color:${c};background:${c}12;border-color:${c}25">${catIcon(s.cat)}</div><div><div class="card-title">${s.title}</div><div class="card-id">${s.id}</div></div></div><div class="card-desc">${s.desc||`<em style="opacity:.4">${t('noDesc')}</em>`}</div><div class="card-foot"><span class="tag tag-cat" style="border-color:${c}30;color:${c}">${catLabel(s.cat)}</span><span class="lines-label">${s.lines} ${t('line')}</span></div></div>`}).join('')}

function openDetail(id){
  const s=SKILLS.find(sk=>sk.id===id);if(!s)return;const c=catColor(s.cat);
  $('detailHead').innerHTML=`<div class="detail-icon" style="color:${c};background:${c}12;border-color:${c}25">${catIcon(s.cat)}</div><div class="detail-title"><h2>${s.title}</h2><code>${s.id}</code></div><button class="close-detail" onclick="closeDetail()">${t('close')}</button>`;
  let h=`<div class="detail-section"><div class="section-label">${t('description')}</div><div class="detail-desc">${s.desc||`<em style="opacity:.5">${t('noDesc')}</em>`}</div></div>`;
  if(s.when)h+=`<div class="detail-section"><div class="section-label">${t('whenToUse')}</div><div class="when-box">${s.when}</div></div>`;
  if(s.sections?.length)h+=`<div class="detail-section"><div class="section-label">${t('sections')}</div><div class="chips-row">${s.sections.map(x=>`<span class="chip">${x}</span>`).join('')}</div></div>`;
  h+=`<div class="detail-section"><div class="section-label">${t('fileInfo')}</div><div class="meta-grid"><div class="meta-card"><div class="meta-label">${t('lines')}</div><div class="meta-value">${s.lines}</div></div><div class="meta-card"><div class="meta-label">${t('category')}</div><div class="meta-value" style="color:${c}">${catLabel(s.cat)}</div></div></div></div>`;
  h+=`<div class="detail-section"><div class="section-label">${t('install')}</div><div class="install-box"><button class="copy-btn" onclick="copyCmd('${s.id}')">${t('copy')}</button><span style="color:var(--muted)"># Project-level:</span>\ncp -r skills/${s.id} .agents/skills/\n\n<span style="color:var(--muted)"># User-level (global):</span>\ncp -r skills/${s.id} ~/.claude/skills/</div></div>`;
  if(s.content){h+=`<div class="detail-section"><div class="section-label">${t('fullContent')}</div><button class="view-btn" id="toggleFullBtn" onclick="toggleFull('${s.id}')">${t('viewFull')}</button><div id="fullBox" style="display:none"></div></div>`}
  $('detailBody').innerHTML=h;$('detailPanel').classList.add('open');
}

function toggleFull(id){const box=$('fullBox'),btn=$('toggleFullBtn');if(box.style.display==='none'){const s=SKILLS.find(sk=>sk.id===id);if(s?.content){box.innerHTML=`<div class="content-viewer">${s.content.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>`;box.style.display='block';btn.textContent=t('hideFull')}}else{box.style.display='none';btn.textContent=t('viewFull')}}
function copyCmd(id){navigator.clipboard.writeText(`cp -r skills/${id} .agents/skills/`).then(()=>{const b=document.querySelector('.copy-btn');if(b){b.textContent=t('copied');setTimeout(()=>b.textContent=t('copy'),1500)}})}
function closeDetail(){$('detailPanel').classList.remove('open')}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeDetail();if(e.key==='/'&&document.activeElement!==$('searchInput')){e.preventDefault();$('searchInput').focus()}});

// ──── INITIAL DATA (injected by Python server) ────
SKILLS = %%SKILLS_JSON%%;
renderSidebar(); renderSkills();
</script>
</body>
</html>"""


# ─────────────────────── HTTP Server ───────────────────────

class ECCHandler(http.server.BaseHTTPRequestHandler):
    skills_dir = Path(".")

    def log_message(self, fmt, *args):
        pass  # Suppress logs

    def do_GET(self):
        path = urlparse(self.path).path

        if path in ("/", "/index.html"):
            skills = scan_skills(self.skills_dir)
            skills_json = json.dumps(skills, ensure_ascii=False)
            # Escape sequences that would break <script> tags in HTML
            skills_json = skills_json.replace("</", "<\\/")
            html = HTML_TEMPLATE.replace("%%SKILLS_JSON%%", skills_json)
            self._respond(200, "text/html", html)

        elif path == "/api/skills":
            skills = scan_skills(self.skills_dir)
            self._respond(200, "application/json", json.dumps(skills, ensure_ascii=False))

        else:
            self.send_error(404)

    def _respond(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))


def find_free_port(preferred=5500):
    for port in [preferred] + list(range(5501, 5550)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return 0


# ─────────────────────── Main ───────────────────────

def main():
    port = 5500
    skills_path = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        elif not args[i].startswith("-"):
            skills_path = Path(args[i])
            i += 1
        else:
            i += 1

    if skills_path:
        skills_dir = skills_path
    else:
        skills_dir = find_skills_dir()
        if not skills_dir:
            print("❌ No skills/ directory found.")
            print("   Usage: python ecc_browser.py [path/to/skills] [--port 5500]")
            sys.exit(1)

    skills = scan_skills(skills_dir)
    if not skills:
        print(f"❌ No SKILL.md files found in: {skills_dir}")
        sys.exit(1)

    ECCHandler.skills_dir = skills_dir
    port = find_free_port(port)
    url = f"http://127.0.0.1:{port}"

    server = http.server.HTTPServer(("127.0.0.1", port), ECCHandler)

    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║     ECC Skills Browser — Web UI (Live)           ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"  📂  Skills: {skills_dir}")
    print(f"  📦  Found:  {len(skills)} skills")
    print(f"  🌐  URL:    {url}")
    print()
    print("  Opening browser... Press Ctrl+C to stop.")
    print()

    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  👋 Goodbye!")
        server.shutdown()


if __name__ == "__main__":
    main()