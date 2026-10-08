import os, base64

def write_b64(path, b64_str):
    full_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'wb') as f:
        f.write(base64.b64decode(b64_str))
    print(f"Wrote {path}")
