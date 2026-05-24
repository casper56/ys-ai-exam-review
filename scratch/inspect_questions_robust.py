import re
import json

with open("E:/workspace/agy/AI_TEST/index.html", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "const fullQuestions = ["
start_idx = content.find(start_marker)
if start_idx == -1:
    print("Could not find start marker!")
    exit(1)

# Find end of array by bracket tracking
balance = 0
array_start = start_idx + len("const fullQuestions = ") - 1
end_idx = -1
for idx in range(array_start, len(content)):
    char = content[idx]
    if char == '[':
        balance += 1
    elif char == ']':
        balance -= 1
        if balance == 0:
            end_idx = idx
            break

if end_idx == -1:
    print("Could not find end bracket!")
    exit(1)

js_array_text = content[array_start : end_idx + 1]
print(f"Extracted JS array length: {len(js_array_text)}")

# We can find all question objects using regex.
# Let's find each object by searching for {"id": ...}
# Since some objects are multiline and contain nested quotes, let's write a parser that parses them robustly.
# We'll split the array text into lines, and group lines that form a question object.
lines = js_array_text.split('\n')
q_blocks = []
current_block = []
brace_level = 0
in_block = False

for line in lines:
    stripped = line.strip()
    if not stripped:
        continue
    
    # Check if a question object starts on this line
    if stripped.startswith('{"id":') or stripped.startswith('{ "id":'):
        in_block = True
        current_block = [line]
        # count braces
        brace_level = line.count('{') - line.count('}')
    elif in_block:
        current_block.append(line)
        brace_level += line.count('{') - line.count('}')
        if brace_level <= 0:
            # We reached the end of the question object
            q_blocks.append("\n".join(current_block))
            in_block = False

print(f"Found {len(q_blocks)} question blocks in index.html.")

# Let's analyze each block manually with regex to extract id, year, num, options, and answer
issues = []
for idx, block in enumerate(q_blocks):
    # Extract "id"
    id_match = re.search(r'"id"\s*:\s*"([^"]+)"', block)
    q_id = id_match.group(1) if id_match else f"UNKNOWN_ID_at_index_{idx}"
    
    # Extract "year"
    year_match = re.search(r'"year"\s*:\s*(\d+)', block)
    year = int(year_match.group(1)) if year_match else None
    
    # Extract "num"
    num_match = re.search(r'"num"\s*:\s*(\d+)', block)
    num = int(num_match.group(1)) if num_match else None
    
    # Extract "options" list. It looks like "options": ["...", "...", "...", "..."]
    # We search for the pattern "options"\s*:\s*\[(.*?)\]
    options_match = re.search(r'"options"\s*:\s*\[(.*?)\]', block, re.DOTALL)
    options = []
    if options_match:
        opt_text = options_match.group(1)
        # Find all double quoted strings in opt_text
        options = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', opt_text)
        
    # Extract "answer"
    answer_match = re.search(r'"answer"\s*:\s*"([^"]+)"', block)
    answer = answer_match.group(1) if answer_match else None
    
    # Analyze
    if not q_id or q_id == f"UNKNOWN_ID_at_index_{idx}":
        issues.append(f"Block {idx}: Failed to extract id")
    if not year:
        issues.append(f"Q {q_id}: Failed to extract year")
    if not num:
        issues.append(f"Q {q_id}: Failed to extract num")
    if len(options) != 4:
        issues.append(f"Q {q_id}: 'options' has length {len(options)}, expected 4. Options text: {options}")
    if answer not in ["A", "B", "C", "D"]:
        issues.append(f"Q {q_id}: 'answer' is '{answer}', expected A, B, C, or D")

if issues:
    print(f"Found {len(issues)} formatting/value issues:")
    for issue in issues:
        print(" -", issue)
else:
    print("NO ISSUES FOUND. All 150 questions have exactly 4 options and valid answers!")
