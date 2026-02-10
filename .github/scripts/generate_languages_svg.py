#!/usr/bin/env python3
"""
生成 GitHub 语言统计 SVG（环形图/甜甜圈图样式）
布局：左侧图例，右侧环形图
"""
import os
import sys
import requests
from datetime import datetime
import math

# 配置
USERNAME = "KeLuoJun"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_FILE = "stats/languages.svg"
# 修改：移除 HTML 从过滤列表，但保留 Jupyter Notebook 的过滤选项
IGNORED_LANGS = {"CSS", "TeX", "Dockerfile", "Makefile", "YAML", "JSON", "Shell", "PowerShell"}
# 可选：如果不想统计 Jupyter Notebook，取消下一行注释
# IGNORED_LANGS.add("Jupyter Notebook")

# GitHub 官方语言颜色映射
LANG_COLORS = {
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
    "Vue": "#41b883",
    "Svelte": "#ff3e00",
    "React": "#61dafb",
    "Angular": "#dd0031",
    "Docker": "#0db7ed",
    "Kubernetes": "#326ce5",
    "HTML": "#e34c26",
}

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
    """生成环形图（甜甜圈图）SVG - 左侧图例，右侧环形图"""
    if not languages:
        return f'''<svg width="600" height="350" viewBox="0 0 600 350" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title {{ font: 600 18px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #0366d6; }}
    .legend-text {{ font: 400 14px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #24292e; }}
    .legend-color {{ font: 400 14px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #57606a; }}
    .update-time {{ font: 400 12px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #6a737d; }}
  </style>
  <rect width="600" height="350" fill="#ffffff" rx="10"/>
  <text x="300" y="40" class="title" text-anchor="middle">Top Languages by Repo</text>
  <text x="300" y="180" class="legend-text" text-anchor="middle">No languages detected</text>
  <text x="300" y="210" class="legend-text" text-anchor="middle">Check: repo visibility / token permissions</text>
  <text x="300" y="330" class="update-time" text-anchor="middle">Updated: {datetime.now().strftime('%Y-%m-%d')}</text>
</svg>'''

    # 计算总字节数
    total = sum(bytes_count for _, bytes_count in languages)
    
    # 准备环形图参数 - 调整位置到右侧
    cx, cy = 450, 180  # 圆心坐标移到右侧
    radius = 100  # 外半径
    inner_radius = 50  # 内半径
    start_angle = -90  # 起始角度（-90度表示从顶部开始）
    
    # 生成环形图
    paths = []
    legend_items = []
    angle = start_angle
    
    for i, (lang, bytes_count) in enumerate(languages[:top_n]):
        percent = (bytes_count / total) * 100
        end_angle = angle + (percent / 100) * 360
        
        # 计算扇形路径
        x1 = cx + radius * math.cos(math.radians(angle))
        y1 = cy + radius * math.sin(math.radians(angle))
        x2 = cx + radius * math.cos(math.radians(end_angle))
        y2 = cy + radius * math.sin(math.radians(end_angle))
        
        # 计算内环坐标
        ix1 = cx + inner_radius * math.cos(math.radians(angle))
        iy1 = cy + inner_radius * math.sin(math.radians(angle))
        ix2 = cx + inner_radius * math.cos(math.radians(end_angle))
        iy2 = cy + inner_radius * math.sin(math.radians(end_angle))
        
        # 生成路径数据
        large_arc = 1 if (end_angle - angle) > 180 else 0
        path_data = (
            f"M {x1} {y1} "
            f"A {radius} {radius} 0 {large_arc} 0 {x2} {y2} "
            f"L {ix2} {iy2} "
            f"A {inner_radius} {inner_radius} 0 {large_arc} 1 {ix1} {iy1} "
            f"Z"
        )
        
        # 生成图例项 - 左侧布局
        color = LANG_COLORS.get(lang, "#cccccc")
        legend_items.append(
            f'<g transform="translate(70,{110 + i * 28})">'
            f'  <rect x="0" y="0" width="15" height="15" fill="{color}" rx="2"/>'
            f'  <text x="25" y="12" class="legend-text">{lang}</text>'
            f'</g>'
        )
        
        # 添加到路径列表
        paths.append(
            f'<path d="{path_data}" fill="{color}" opacity="0.95" stroke="#ffffff" stroke-width="2"/>'
        )
        
        angle = end_angle
    
    # 生成SVG - 修改布局
    svg = f'''<svg width="600" height="350" viewBox="0 0 600 350" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.15"/>
    </filter>
  </defs>
  
  <style>
    .title {{ font: 600 22px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #0969da; }}
    .legend-text {{ font: 400 14px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #1f2328; }}
    .update-time {{ font: 400 11px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #656d76; }}
  </style>
  
  <!-- 背景 -->
  <rect width="600" height="350" fill="#ffffff" rx="6"/>
  
  <!-- 标题 -->
  <text x="300" y="45" class="title" text-anchor="middle">Top Languages by Repo</text>
  
  <!-- 图例 - 左侧 -->
  <g>
    {"".join(legend_items)}
  </g>
  
  <!-- 环形图 - 右侧 -->
  <g filter="url(#shadow)">
    {"".join(paths)}
  </g>
  
  <!-- 更新时间 -->
  <text x="300" y="330" class="update-time" text-anchor="middle">
    Updated: {datetime.now().strftime('%Y-%m-%d')}
  </text>
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
        print("   2. 仓库只有被忽略的语言（CSS 等）")
        print("   3. 仓库为空或只有文档")
    else:
        total_bytes = sum(b for _, b in languages)
        print(f"✅ 检测到 {len(languages)} 种语言:")
        for lang, bytes_count in languages[:8]:
            percent = (bytes_count / total_bytes) * 100
            print(f"   - {lang}: {percent:.1f}% ({bytes_count:,} bytes)")
    
    svg = generate_svg(languages)
    save_svg(svg)
    print(f"🎉 完成! 统计更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()