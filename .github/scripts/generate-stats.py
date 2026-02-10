import requests
import json
from datetime import datetime

def get_language_stats(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    repos = response.json()
    
    languages = {}
    for repo in repos:
        if not repo['fork']:
            lang_url = repo['languages_url']
            lang_response = requests.get(lang_url)
            lang_data = lang_response.json()
            
            for lang, bytes_count in lang_data.items():
                if lang in languages:
                    languages[lang] += bytes_count
                else:
                    languages[lang] = bytes_count
    
    # 排序并格式化
    sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    return sorted_languages

def update_readme(languages):
    # 读取README
    with open('README.md', 'r') as f:
        content = f.read()
    
    # 生成新的语言统计部分
    stats_html = '<div align="right">\n'
    stats_html += '<table>\n<tr><th>Language</th><th>Usage</th></tr>\n'
    
    total = sum([bytes_count for _, bytes_count in languages])
    for lang, bytes_count in languages[:10]:  # 只显示前10
        percentage = (bytes_count / total) * 100
        stats_html += f'<tr><td>{lang}</td><td>{percentage:.1f}%</td></tr>\n'
    
    stats_html += '</table>\n</div>'
    
    # 更新README
    # 这里需要根据你的README结构来更新
    # 可以使用正则表达式或标记来定位和替换
    
    with open('README.md', 'w') as f:
        f.write(content)
    
    return stats_html

if __name__ == "__main__":
    username = "KeLuoJun"
    languages = get_language_stats(username)
    update_readme(languages)