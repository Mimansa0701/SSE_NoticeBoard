import os

def write_file(path, content):
    full_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print('Created:', path)

print('build_full_project ready')
