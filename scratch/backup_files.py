import os
import shutil

src = "E:/workspace/agy/AI_TEST/index.html"
dst_dir = "E:/workspace/agy/AI_TEST/backups"
dst = os.path.join(dst_dir, "index.html.bak")

if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

if os.path.exists(src):
    shutil.copy2(src, dst)
    print(f"Successfully backed up {src} to {dst}")
else:
    print(f"Source file {src} does not exist!")
