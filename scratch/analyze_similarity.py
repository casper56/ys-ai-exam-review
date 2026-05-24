import re
import json

# Read index.html to extract the questions
with open("E:/workspace/agy/AI_TEST/index.html", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "const fullQuestions = ["
start_idx = content.find(start_marker)
if start_idx == -1:
    print("Could not find start marker!")
    exit(1)

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

js_array_text = content[array_start : end_idx + 1]

# Quick extraction of question text, year, type, and answer
# Since it is a JS array of objects, let's find all items by splitting or brace matching.
# We will use the same robust logic as inspect_questions_robust
lines = js_array_text.split('\n')
q_blocks = []
current_block = []
brace_level = 0
in_block = False

for line in lines:
    stripped = line.strip()
    if not stripped:
        continue
    if stripped.startswith('{"id":') or stripped.startswith('{ "id":'):
        in_block = True
        current_block = [line]
        brace_level = line.count('{') - line.count('}')
    elif in_block:
        current_block.append(line)
        brace_level += line.count('{') - line.count('}')
        if brace_level <= 0:
            q_blocks.append("\n".join(current_block))
            in_block = False

questions = []
for idx, block in enumerate(q_blocks):
    id_match = re.search(r'"id"\s*:\s*"([^"]+)"', block)
    q_id = id_match.group(1) if id_match else f"UNKNOWN_{idx}"
    
    year_match = re.search(r'"year"\s*:\s*(\d+)', block)
    year = int(year_match.group(1)) if year_match else None
    
    num_match = re.search(r'"num"\s*:\s*(\d+)', block)
    num = int(num_match.group(1)) if num_match else None
    
    type_match = re.search(r'"type"\s*:\s*"([^"]+)"', block)
    q_type = type_match.group(1) if type_match else None
    
    question_match = re.search(r'"question"\s*:\s*"([^"]+)"', block)
    question = question_match.group(1) if question_match else ""
    
    answer_match = re.search(r'"answer"\s*:\s*"([^"]+)"', block)
    answer = answer_match.group(1) if answer_match else ""
    
    questions.append({
        "id": q_id,
        "year": year,
        "num": num,
        "type": q_type,
        "question": question,
        "answer": answer
    })

print(f"Parsed {len(questions)} questions for analysis.")

# Group by year
by_year = {113: [], 114: [], 115: []}
for q in questions:
    by_year[q["year"]].append(q)

# 1. Compute exact duplication or very high similarity
# We can normalize strings by removing non-alphanumeric/Chinese characters.
def normalize(text):
    text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
    return text.lower()

# Calculate Jaccard similarity between two sets of characters or words
def jaccard_similarity(str1, str2):
    s1 = set(normalize(str1))
    s2 = set(normalize(str2))
    if not s1 or not s2:
        return 0
    return len(s1.intersection(s2)) / len(s1.union(s2))

# Find overlapping pairs between years
pairs_113_114 = []
pairs_114_115 = []
pairs_113_115 = []

for q1 in by_year[113]:
    for q2 in by_year[114]:
        sim = jaccard_similarity(q1["question"], q2["question"])
        if sim > 0.8:
            pairs_113_114.append((q1, q2, sim))

for q1 in by_year[114]:
    for q2 in by_year[115]:
        sim = jaccard_similarity(q1["question"], q2["question"])
        if sim > 0.8:
            pairs_114_115.append((q1, q2, sim))

for q1 in by_year[113]:
    for q2 in by_year[115]:
        sim = jaccard_similarity(q1["question"], q2["question"])
        if sim > 0.8:
            pairs_113_115.append((q1, q2, sim))

print(f"Duplicates/High Similarity (>80%):")
print(f" - 113 vs 114: {len(pairs_113_114)} pairs")
for p in pairs_113_114:
    print(f"   * 113 Q{p[0]['num']} vs 114 Q{p[1]['num']} (sim: {p[2]:.2f})")
    print(f"     113: {p[0]['question'][:40]}...")
    print(f"     114: {p[1]['question'][:40]}...")

print(f" - 114 vs 115: {len(pairs_114_115)} pairs")
for p in pairs_114_115:
    print(f"   * 114 Q{p[0]['num']} vs 115 Q{p[1]['num']} (sim: {p[2]:.2f})")
    print(f"     114: {p[0]['question'][:40]}...")
    print(f"     115: {p[1]['question'][:40]}...")

print(f" - 113 vs 115: {len(pairs_113_115)} pairs")
for p in pairs_113_115:
    print(f"   * 113 Q{p[0]['num']} vs 115 Q{p[1]['num']} (sim: {p[2]:.2f})")
    print(f"     113: {p[0]['question'][:40]}...")
    print(f"     115: {p[1]['question'][:40]}...")

# 2. Topic/Knowledge Point classification
# Let's map keywords to knowledge domains
# We scan questions for key terms:
domains = {
    "Math & Arithmetic (數學/數理)": [r"公尺", r"公分", r"公里", r"平方", r"速度", r"工程", r"年齡", r"父親", r"兒子", r"水煎包", r"套餐", r"折", r"元", r"經濟包", r"秤重"],
    "Logical Reasoning & Patterns (邏輯/圖形/規律)": [r"圖形", r"循環", r"三角柱", r"正方形", r"對角線", r"銅板", r"反面", r"正面", r"丟", r"平均數", r"第.*名", r"規律"],
    "Chinese Literature & Proverbs (國文/成語/年齡代稱)": [r"年華", r"花甲", r"弱冠", r"而立", r"及笄", r"古稀", r"五倫", r"成語", r"左右逢源", r"記憶長存", r"喬梓", r"部首", r"出類拔萃", r"慎終追遠", r"賀詞", r"包容", r"梅雨", r"詩作", r"野人", r"濫竽", r"虛字", r"祝壽", r"讀音", r"泠泠", r"李白", r"聞香下馬", r"倚老", r"苦口婆心", r"棒球", r"蚵仔煎", r"精釀", r"疊詞"],
    "C++ / C Programming (C/C++ 程式設計)": [r"C\+\+", r"void", r"main", r"基本資料型態", r"指標", r"二維陣列", r"動態記憶體", r"虛擬函數", r"switch", r"printf", r"int num", r"intpages", r"int pages"],
    "C# Programming (C# 程式設計)": [r"C#", r"類別繼承", r"介面繼承", r"變數名稱", r"char", r"bitwise", r"送分題", r"LblScore", r"timer1", r"msg", r"DateTime"],
    "Python Programming (Python 程式設計)": [r"Python", r"縮排", r"註解", r"元組", r"串列"],
    "Networks & Security (網路與資安)": [r"IP", r"RTP", r"狀態碼", r"瀏覽網站", r"機房", r"網際網路", r"NoSQL", r"FHD", r"IPv6", r"ping", r"NFC", r"非對稱", r"加密", r"PPP", r"CHAP", r"過濾", r"iptables", r"子網路", r"UDP", r"TCP", r"HTTP", r"網址"],
    "Databases & RDBMS (資料庫設計)": [r"資料庫", r"正規化", r"SQL", r"選課資料表", r"MS SQL"],
    "Cloud Computing (雲端運算/Azure)": [r"Azure", r"Artificial Intelligence", r"predictive analytics", r"regions", r"administrator", r"Advisor", r"virtual machine", r"Logic App"],
    "General Science & Common Sense (自然與常識)": [r"紫外線", r"大氣層", r"梅雨", r"磁磚", r"發霉", r"瓦斯", r"熱水器", r"一氧化碳", r"侵蝕作用", r"河流"]
}

year_domain_counts = {113: {}, 114: {}, 115: {}}
for year in [113, 114, 115]:
    for domain in domains:
        year_domain_counts[year][domain] = 0

for q in questions:
    text = q["question"] + " " + q.get("answer", "")
    # Check regular expressions
    classified = False
    for domain, patterns in domains.items():
        for pat in patterns:
            if re.search(pat, text, re.I):
                year_domain_counts[q["year"]][domain] += 1
                classified = True
                break

print("\nKnowledge Domains distribution per year:")
for domain in domains:
    print(f" - {domain}:")
    print(f"   * 113: {year_domain_counts[113][domain]} questions")
    print(f"   * 114: {year_domain_counts[114][domain]} questions")
    print(f"   * 115: {year_domain_counts[115][domain]} questions")
