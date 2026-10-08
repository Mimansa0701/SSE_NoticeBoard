import base64, os

def w(path, b64_content):
    full_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'wb') as f:
        f.write(base64.b64decode(b64_content))
    print("Created:", path)

print("generate_all.py initialized")
