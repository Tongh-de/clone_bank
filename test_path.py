"""测试静态文件路径"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")
css_path = os.path.join(BASE_DIR, "static", "css", "style.css")

print(f"BASE_DIR: {BASE_DIR}")
print(f"static exists: {os.path.exists(static_path)}")
print(f"style.css exists: {os.path.exists(css_path)}")
print(f"css_path: {css_path}")
