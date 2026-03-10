import os
import re

filepath = 'src/api.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

new_block = """base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = base_dir
    while os.path.basename(project_root) in ['src', 'scrapers', 'tests']:
        project_root = os.path.dirname(project_root)"""

content = re.sub(
    r"base_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\n\s*if os\.path\.basename\(base_dir\) == 'src':\n\s*project_root = os\.path\.dirname\(base_dir\)\n\s*else:\n\s*project_root = base_dir",
    new_block,
    content,
    flags=re.DOTALL
)

content = re.sub(
    r"base_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\n\s*project_root = os\.path\.dirname\(base_dir\) if os\.path\.basename\(base_dir\) == 'src' else base_dir",
    new_block,
    content,
    flags=re.DOTALL
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
