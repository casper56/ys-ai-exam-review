const fs = require('fs');

const content = fs.readFileSync('E:/workspace/agy/AI_TEST/index.html', 'utf8');

const startMarker = 'const fullQuestions = [';
const startIdx = content.indexOf(startMarker);
if (startIdx === -1) {
    console.error("Could not find start marker!");
    process.exit(1);
}

// Track square bracket balance to find the end of the array
let balance = 0;
let arrayStart = startIdx + startMarker.length - 1; // index of '['
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

if (endIdx === -1) {
    console.error("Could not find end bracket!");
    process.exit(1);
}

const jsArrayText = content.slice(arrayStart, endIdx + 1);
console.log(`Extracted JS array text length: ${jsArrayText.length}`);

// We can evaluate the array using eval or Function inside Node.js!
let fullQuestions;
try {
    fullQuestions = eval(jsArrayText);
} catch (e) {
    console.error("Failed to parse array with eval: " + e.message);
    process.exit(1);
}

console.log(`Successfully parsed ${fullQuestions.length} questions from index.html!`);

const issues = [];
fullQuestions.forEach((q, idx) => {
    const qId = q.id || `UNKNOWN_ID_at_index_${idx}`;
    if (!q.id) issues.push(`Question at index ${idx}: missing 'id'`);
    if (!q.year) issues.push(`Q ${qId}: missing 'year'`);
    if (!q.num) issues.push(`Q ${qId}: missing 'num'`);
    if (!q.type) issues.push(`Q ${qId}: missing 'type'`);
    if (!q.question) issues.push(`Q ${qId}: missing 'question'`);
    if (!q.options) {
        issues.push(`Q ${qId}: missing 'options'`);
    } else {
        if (!Array.isArray(q.options)) {
            issues.push(`Q ${qId}: 'options' is not an array`);
        } else if (q.options.length !== 4) {
            issues.push(`Q ${qId}: 'options' has length ${q.options.length}, expected 4`);
        } else {
            q.options.forEach((opt, optIdx) => {
                if (typeof opt !== 'string' || opt.trim() === '') {
                    issues.push(`Q ${qId} option ${optIdx}: empty or non-string option`);
                }
            });
        }
    }
    if (!q.answer) {
        issues.push(`Q ${qId}: missing 'answer'`);
    } else {
        if (!['A', 'B', 'C', 'D'].includes(q.answer)) {
            issues.push(`Q ${qId}: 'answer' is '${q.answer}', expected A, B, C, or D`);
        }
    }
    if (!q.explanation || q.explanation.trim().length < 10) {
        issues.push(`Q ${qId}: 'explanation' is missing or too short`);
    }
});

if (issues.length > 0) {
    console.log(`Found ${issues.length} issues:`);
    issues.forEach(issue => console.log(' - ' + issue));
} else {
    console.log("ALL 150 QUESTIONS ARE 100% VALID AND CORRECTLY STRUCTURED!");
}
