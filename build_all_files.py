import os

def w(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text.strip() + '\n')
    print('Wrote', path)

print('build_all_files.py initialized')
