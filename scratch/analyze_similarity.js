const fs = require('fs');

const content = fs.readFileSync('E:/workspace/agy/AI_TEST/index.html', 'utf8');

const startMarker = 'const fullQuestions = [';
const startIdx = content.indexOf(startMarker);
if (startIdx === -1) {
    console.error("Could not find start marker!");
    process.exit(1);
}

let balance = 0;
let arrayStart = startIdx + startMarker.length - 1;
let endIdx = -1;

for (let i = arrayStart; i < content.length; i++) {
    if (content[i] === '[') balance++;
    else if (content[i] === ']') {
        balance--;
        if (balance === 0) {
            endIdx = i;
            break;
        }
    }
}

const jsArrayText = content.slice(arrayStart, endIdx + 1);
const fullQuestions = eval(jsArrayText);

console.log(`Parsed ${fullQuestions.length} questions.`);

// Group by year
const byYear = { 113: [], 114: [], 115: [] };
fullQuestions.forEach(q => {
    byYear[q.year].push(q);
});

// Helper to tokenize questions (returns set of words/Chinese characters)
function tokenize(text) {
    if (!text) return new Set();
    
    // Replace punctuation with spaces
    const clean = text.replace(/[\.,\?!;:"'\(\)\[\]\{\}\-\+\=\*\/&\|<>·\n\r]/g, ' ');
    const tokens = [];
    
    // Extract English words and Chinese characters separately
    // 1. Chinese characters
    const chMatches = clean.match(/[\u4e00-\u9fff]/g) || [];
    chMatches.forEach(c => tokens.push(c));
    
    // 2. English words and numbers
    const enMatches = clean.match(/[a-zA-Z0-9]+/g) || [];
    enMatches.forEach(w => {
        if (w.length > 1) { // ignore single letter words
            tokens.push(w.toLowerCase());
        }
    });
    
    return new Set(tokens);
}

// Calculate token Jaccard similarity
function calculateSimilarity(str1, str2) {
    const s1 = tokenize(str1);
    const s2 = tokenize(str2);
    
    if (s1.size === 0 || s2.size === 0) return 0;
    
    let intersection = 0;
    s1.forEach(token => {
        if (s2.has(token)) intersection++;
    });
    
    return intersection / (s1.size + s2.size - intersection);
}

console.log("\n=== CONCEPT & WORD OVERLAP (Token Jaccard Similarity >= 45%) ===");
const years = [113, 114, 115];
const pairs = [];

for (let i = 0; i < years.length; i++) {
    for (let j = i + 1; j < years.length; j++) {
        const y1 = years[i];
        const y2 = years[j];
        
        byYear[y1].forEach(q1 => {
            byYear[y2].forEach(q2 => {
                const sim = calculateSimilarity(q1.question, q2.question);
                if (sim >= 0.45) {
                    pairs.push({ q1, q2, sim });
                }
            });
        });
    }
}

console.log(`Found ${pairs.length} high similarity question pairs.`);
pairs.forEach(p => {
    console.log(`- [${p.q1.year} Q${p.q1.num}] vs [${p.q2.year} Q${p.q2.num}] (Similarity: ${(p.sim * 100).toFixed(1)}%)`);
    console.log(`  ${p.q1.year}: ${p.q1.question}`);
    console.log(`  ${p.q2.year}: ${p.q2.question}`);
    console.log(`  Answers: ${p.q1.year}=(${p.q1.answer}), ${p.q2.year}=(${p.q2.answer})`);
});
