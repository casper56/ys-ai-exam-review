with open("E:/workspace/agy/AI_TEST/index.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Search for any question text containing "選項" or "選定" or "無法"
# Let's find occurrences in the HTML question text
matches = re.findall(r'"question":\s*"([^"]+)"', content)

found = []
for m in matches:
    if "選項" in m or "選定" in m or "無法" in m or "選" in m:
        found.append(m)

print(f"Found {len(found)} questions containing '選/無法/選定':")
for f in found[:20]:
    print(" -", f)
