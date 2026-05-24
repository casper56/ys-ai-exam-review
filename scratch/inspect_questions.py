with open("E:/workspace/agy/AI_TEST/index.html", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "const fullQuestions = ["
start_idx = content.find(start_marker)
if start_idx == -1:
    print("Could not find start marker!")
    exit(1)

# Find the end of the array by tracking the square bracket balance starting after "const fullQuestions = "
# The array starts with '['
balance = 0
array_start = start_idx + len("const fullQuestions = ") - 1 # this is the '['
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
    print("Could not find matching end square bracket!")
    exit(1)

js_array_text = content[array_start : end_idx + 1]
print(f"Extracted JS array length: {len(js_array_text)}")

# Let's parse all objects within this array by tracking brace balance
brace_count = 0
current_obj = ""
in_obj = False
questions = []

import ast

for char in js_array_text:
    if char == '{':
        if brace_count == 0:
            in_obj = True
            current_obj = ""
        brace_count += 1
    
    if in_obj:
        current_obj += char
        
    if char == '}':
        brace_count -= 1
        if brace_count == 0:
            in_obj = False
            # Clean and parse current_obj
            obj_str = current_obj.strip()
            obj_str_cleaned = obj_str.replace("true", "True").replace("false", "False").replace("null", "None")
            try:
                parsed = ast.literal_eval(obj_str_cleaned)
                questions.append(parsed)
            except Exception as e:
                # Let's print the error and a snippet if it fails
                print(f"Failed to parse object: {e}")
                print(obj_str[:150])
                print("...")

print(f"Total parsed questions: {len(questions)}")

# Let's print summary of questions per year
years = {}
for q in questions:
    y = q.get("year")
    years[y] = years.get(y, 0) + 1
print("Questions count per year:", years)

# Check for issues
issues = []
for q in questions:
    q_id = q.get("id")
    year = q.get("year")
    num = q.get("num")
    options = q.get("options", [])
    answer = q.get("answer")
    explanation = q.get("explanation")
    
    # 1. Check if options is a list of 4 elements
    if not isinstance(options, list) or len(options) != 4:
        issues.append(f"Q {q_id}: 'options' is not of length 4. Got {options}")
        
    # 2. Check if answer is A, B, C, or D
    if answer not in ["A", "B", "C", "D"]:
        issues.append(f"Q {q_id}: 'answer' is not A, B, C, or D. Got '{answer}'")
        
    # 3. Check if explanation exists and is detailed
    if not explanation or len(explanation.strip()) < 10:
        issues.append(f"Q {q_id}: 'explanation' is missing or too short. Got '{explanation}'")

if issues:
    print(f"Found {len(issues)} potential issues:")
    for issue in issues:
        print(" -", issue)
else:
    print("No issues found in the full 150 questions array!")
