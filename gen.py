import os, sys, base64

def write(pl_b64, path):
    data = base64.b64decode(pl_b64)
    full_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'wb') as f:
        f.write(data)
    print(f'Wrote {path}')
