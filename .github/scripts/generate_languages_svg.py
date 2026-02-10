#!/usr/bin/env python3
"""
生成 GitHub 语言统计 SVG（条形图样式）
"""
import os
import sys
import requests
from datetime import datetime

# 配置
USERNAME = "KeLuoJun"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_FILE = "stats/languages.svg"
IGNORED_LANGS = {"HTML", "CSS", "TeX", "Dockerfile", "Makefile", "YAML", "JSON", "Shell", "PowerShell"}

def get_repos():
    """获取用户所有仓库"""
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
    repos = []
    page = 1
    
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}", file=sys.stderr)
            sys.exit(1)
        
        page_repos = response.json()
        if not page_repos:
            break
        
        repos.extend([r for r in page_repos if not r.get("fork")])
        page += 1
    
    return repos

def get_languages(repos):
    """统计所有仓库的语言使用量"""
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
    languages = {}
    
    for repo in repos:
        lang_url = repo["languages_url"]
        response = requests.get(lang_url, headers=headers)
        
        if response.status_code == 200:
            lang_data = response.json()
            for lang, bytes_count in lang_data.items():
                if lang not in IGNORED_LANGS:
                    languages[lang] = languages.get(lang, 0) + bytes_count
    
    # 按字节数排序
    return sorted(languages.items(), key=lambda x: x[1], reverse=True)

def generate_svg(languages, top_n=8):
    """生成 SVG 条形图"""
    if not languages:
        return f'''<svg width="400" height="100" viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title {{ font: 600 18px sans-serif; fill: #0366d6; }}
    .error {{ font: 400 14px sans-serif; fill: #cf222e; }}
  </style>
  <text x="20" y="30" class="title">Most Used Languages</text>
  <text x="20" y="60" class="error">No languages found</text>
  <text x="20" y="80" class="error">Check repository visibility</text>
</svg>'''
    
    total = sum(bytes_count for _, bytes_count in languages)
    items = []
    y_offset = 50
    bar_height = 16
    bar_width = 320
    item_height = 28
    
    # GitHub 官方语言颜色
    lang_colors = {
        "Python": "#3572A5",
        "JavaScript": "#f1e05a",
        "TypeScript": "#007acc",
        "Java": "#b07219",
        "C++": "#f34b7d",
        "C": "#555555",
        "C#": "#178600",
        "Go": "#00ADD8",
        "Rust": "#dea584",
        "Ruby": "#701516",
        "PHP": "#4F5D95",
        "Swift": "#ffac45",
        "Kotlin": "#0095D5",
        "Scala": "#c22d40",
        "R": "#198ce7",
        "Julia": "#9558b2",
        "Dart": "#00b4ab",
        "Lua": "#000080",
        "Haskell": "#5e5086",
        "Elixir": "#6e4a7e",
        "Clojure": "#db5855",
        "Objective-C": "#438eff",
        "Perl": "#0298c3",
        "VimL": "#199f4b",
        "Jupyter Notebook": "#da5b0b",
    }
    
    # 生成条目
    for i, (lang, bytes_count) in enumerate(languages[:top_n]):
        percent = (bytes_count / total) * 100
        color = lang_colors.get(lang, "#cccccc")
        bar_len = (percent / 100) * bar_width
        
        items.append(f'''
  <g transform="translate(0,{y_offset + i * item_height})">
    <text x="0" y="14" class="lang-name">{lang}</text>
    <rect x="0" y="18" width="{bar_len}" height="{bar_height}" rx="3" fill="{color}"/>
    <text x="{bar_width + 10}" y="30" class="percent">{percent:.1f}%</text>
  </g>''')
    
    svg = f'''<svg width="400" height="{80 + len(languages[:top_n]) * item_height}" viewBox="0 0 400 {80 + len(languages[:top_n]) * item_height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 18px sans-serif; fill: #0366d6; }}
    .lang-name {{ font: 400 14px sans-serif; fill: #24292e; }}
    .percent {{ font: 400 14px sans-serif; fill: #57606a; text-anchor: end; }}
  </style>
  <text x="0" y="28" class="header">Most Used Languages</text>
  <g transform="translate(0,40)">
    {''.join(items)}
  </g>
  <text x="0" y="{80 + len(languages[:top_n]) * item_height - 5}" class="update-time" font-size="12" fill="#6a737d">Updated: {datetime.now().strftime('%Y-%m-%d')}</text>
</svg>'''
    
    return svg

def save_svg(svg_content):
    """保存 SVG 文件"""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg_content.strip())
    print(f"✅ 语言统计已保存到: {OUTPUT_FILE}")

def main():
    print("🔍 正在获取仓库列表...")
    repos = get_repos()
    print(f"✅ 找到 {len(repos)} 个非 Fork 仓库")
    
    print("📊 正在统计语言使用量...")
    languages = get_languages(repos)
    
    if not languages:
        print("⚠️  警告: 未检测到任何编程语言", file=sys.stderr)
        print("   可能原因:")
        print("   1. 仓库都是私有的（需要正确配置 TOKEN）")
        print("   2. 仓库只有被忽略的语言（HTML/CSS 等）")
        print("   3. 仓库为空或只有文档")
    else:
        print(f"✅ 检测到 {len(languages)} 种语言:")
        for lang, bytes_count in languages[:5]:
            percent = (bytes_count / sum(b for _, b in languages)) * 100
            print(f"   - {lang}: {percent:.1f}% ({bytes_count:,} bytes)")
    
    svg = generate_svg(languages)
    save_svg(svg)
    print(f"🎉 完成! 统计更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()