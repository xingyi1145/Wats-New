import os
import glob

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The most common pattern:
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # project_root = os.path.dirname(current_dir) if os.path.basename(current_dir) == 'src' else current_dir

    new_block = """current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
while os.path.basename(project_root) in ['src', 'scrapers', 'tests']:
    project_root = os.path.dirname(project_root)"""

    import re
    
    # 1. Single line assignment
    content = re.sub(
        r"current_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\n.*?project_root = os\.path\.dirname\(current_dir\) if os\.path\.basename\(current_dir\) == 'src' else current_dir",
        new_block,
        content,
        flags=re.DOTALL
    )

    # 2. Multi-line assignment
    content = re.sub(
        r"current_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\nproject_root = \(\n    os\.path\.dirname\(current_dir\)\n    if os\.path\.basename\(current_dir\) == \"src\"\n    else current_dir\n\)",
        new_block,
        content,
        flags=re.DOTALL
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for root, _, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            patch_file(os.path.join(root, file))

