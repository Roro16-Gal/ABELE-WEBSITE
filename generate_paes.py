import html
import json
import re
from pathlib import Path

import pypdf


ROOT = Path(r"C:\Users\Asus Tuf\Documents\Codex\2026-06-28\create-a-website-in-a-single")
PDF = Path(r"C:\Users\Asus Tuf\Downloads\Area 2.pdf")
OUT = ROOT / "outputs" / "paes.html"


def clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value.replace("\u2013", "-").replace("\u2014", "-")).strip()
    value = value.replace(" ,", ",").replace(" .", ".")
    return value


def extract_pdf_text(path: Path) -> str:
    reader = pypdf.PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def split_sections(text: str):
    raw_headings = [
        ("GENERAL TERMINOLOGIES", "General Terminologies"),
        ("MATHEMATICS", "Mathematics"),
        ("AQUACULTURE", "Aquaculture"),
        ("PHILIPPINE Agricultural Engineering Standards", "Philippine Agricultural Engineering Standards"),
        ("STATISTICS", "Statistics"),
        ("IRRIGATION AND DRAINAGE ENGINEERING", "Irrigation and Drainage Engineering"),
        ("HYDROLOGY", "Hydrology"),
        ("SOIL AND WATER CONSERVATION ENGINEERING", "Soil and Water Conservation Engineering"),
    ]
    positions = []
    for heading, label in raw_headings:
        idx = text.find(heading)
        if idx >= 0:
            positions.append((idx, heading, label))
    positions.sort()

    sections = {}
    for i, (start, heading, label) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        body = text[start + len(heading) : end]
        sections[label] = body
    return sections


def parse_entries(section_name: str, body: str):
    matches = list(re.finditer(r"(?m)^\s*(\d+)\.\s+", body))
    entries = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = clean_text(body[start:end])
        if " - " in chunk:
            term, definition = chunk.split(" - ", 1)
        elif " – " in chunk:
            term, definition = chunk.split(" – ", 1)
        elif " = " in chunk:
            term, definition = chunk.split(" = ", 1)
        else:
            pieces = chunk.split(" ", 1)
            if len(pieces) == 2:
                term, definition = pieces
            else:
                continue
        term = clean_text(term).strip("-:;")
        definition = clean_text(definition).strip("-:;")
        if len(term) < 1 or len(definition) < 1:
            continue
        entries.append(
            {
                "id": f"{section_name[:3].upper()}-{match.group(1)}",
                "subject": section_name,
                "term": term,
                "definition": definition,
            }
        )
    return entries


def build_bank():
    text = extract_pdf_text(PDF)
    bank = []
    for section, body in split_sections(text).items():
        bank.extend(parse_entries(section, body))
    return bank


def build_html(bank):
    data = json.dumps(bank, ensure_ascii=False)
    subjects = {}
    for item in bank:
        subjects[item["subject"]] = subjects.get(item["subject"], 0) + 1
    counts = ", ".join(f"{html.escape(k)}: {v}" for k, v in subjects.items())

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PAES Area 2 Practice Quiz</title>
  <style>
    :root {{
      --green-950:#052e22; --green-900:#064e3b; --green-800:#065f46; --green-700:#047857;
      --mint:#d1fae5; --teal:#0f766e; --gold:#f59e0b; --red:#dc2626;
      --ink:#0f172a; --muted:#64748b; --line:#dbe3ea; --paper:#ffffff; --wash:#f5f8f6;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; min-height:100vh; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--ink); background:var(--wash); }}
    header {{ position:sticky; top:0; z-index:10; background:var(--green-900); color:white; box-shadow:0 8px 22px rgba(5,46,34,.18); }}
    .bar {{ max-width:1120px; margin:auto; padding:14px 20px; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    .brand {{ display:flex; gap:12px; align-items:center; min-width:0; }}
    .mark {{ width:42px; height:42px; border-radius:8px; display:grid; place-items:center; background:var(--green-700); font-weight:900; }}
    h1 {{ margin:0; font-size:18px; line-height:1.15; }}
    .sub {{ margin:2px 0 0; color:#b7f7d7; font-size:12px; font-weight:600; }}
    main {{ max-width:1120px; margin:auto; padding:24px 20px 48px; }}
    .screen {{ display:none; }} .screen.active {{ display:block; animation:rise .25s ease-out; }}
    @keyframes rise {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
    .panel {{ background:var(--paper); border:1px solid var(--line); border-radius:8px; box-shadow:0 18px 40px rgba(15,23,42,.08); }}
    .home {{ max-width:780px; margin:22px auto; padding:28px; }}
    h2 {{ margin:0; font-size:30px; line-height:1.1; letter-spacing:0; }}
    .lead {{ color:var(--muted); margin:10px 0 24px; line-height:1.55; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:12px; }}
    .subject {{ border:2px solid var(--line); background:white; border-radius:8px; padding:16px; text-align:left; cursor:pointer; transition:.16s ease; min-height:104px; }}
    .subject:hover, .subject.selected {{ border-color:var(--green-700); background:#f0fdf4; transform:translateY(-1px); }}
    .subject b {{ display:block; font-size:15px; margin-bottom:7px; }}
    .subject span {{ color:var(--muted); font-size:13px; }}
    .settings {{ display:grid; grid-template-columns:minmax(180px,1fr) auto; gap:12px; align-items:end; margin-top:22px; padding-top:20px; border-top:1px solid var(--line); }}
    label {{ display:block; font-size:13px; font-weight:800; margin-bottom:7px; color:#334155; }}
    input {{ width:100%; border:1px solid #cbd5e1; border-radius:8px; padding:12px 13px; font:inherit; }}
    button {{ font:inherit; }}
    .primary, .ghost, .danger {{ border:0; border-radius:8px; padding:12px 16px; font-weight:800; cursor:pointer; min-height:44px; }}
    .primary {{ background:var(--green-800); color:white; box-shadow:0 8px 18px rgba(6,95,70,.22); }}
    .primary:hover {{ background:var(--green-950); }}
    .ghost {{ background:#eef5f1; color:#134e4a; }}
    .danger {{ background:white; color:#475569; border:1px solid var(--line); }}
    .quiz-wrap {{ max-width:860px; margin:0 auto; }}
    .progress-row {{ display:flex; justify-content:space-between; gap:12px; color:var(--muted); font-size:13px; font-weight:800; margin:8px 0; }}
    .track {{ height:10px; border-radius:999px; background:#e2e8f0; overflow:hidden; margin-bottom:14px; }}
    .fill {{ height:100%; width:0; background:linear-gradient(90deg,var(--green-700),var(--teal)); transition:width .25s ease; }}
    .question {{ padding:24px; }}
    .tag {{ display:inline-flex; padding:6px 10px; border-radius:999px; color:#065f46; background:#dff9eb; font-size:12px; font-weight:900; margin-bottom:14px; }}
    .qtext {{ font-size:21px; line-height:1.45; margin:0 0 18px; font-weight:800; }}
    .options {{ display:grid; gap:10px; }}
    .option {{ width:100%; display:flex; align-items:center; gap:12px; border:2px solid var(--line); border-radius:8px; background:white; padding:13px; text-align:left; cursor:pointer; min-height:58px; }}
    .option:hover {{ border-color:#94d6bd; background:#fbfffd; }}
    .option.selected {{ border-color:var(--green-700); background:#ecfdf5; }}
    .letter {{ width:32px; height:32px; border-radius:8px; display:grid; place-items:center; background:#eef2f7; color:#475569; font-weight:900; flex:0 0 auto; }}
    .actions {{ display:flex; justify-content:space-between; gap:12px; margin-top:18px; }}
    .results {{ max-width:920px; margin:0 auto; }}
    .score {{ padding:26px; display:grid; gap:18px; grid-template-columns:1fr auto; align-items:center; }}
    .score-num {{ font-size:48px; font-weight:900; color:var(--green-800); }}
    .review {{ margin-top:16px; display:grid; gap:10px; }}
    .review-card {{ padding:16px; border-left:5px solid var(--line); }}
    .review-card.good {{ border-left-color:var(--green-700); }}
    .review-card.bad {{ border-left-color:var(--red); }}
    .review-card p {{ margin:6px 0; line-height:1.45; }}
    .tiny {{ color:var(--muted); font-size:12px; }}
    .hidden {{ display:none !important; }}
    @media (max-width:650px) {{
      .bar {{ align-items:flex-start; }}
      h2 {{ font-size:25px; }}
      .home, .question {{ padding:18px; }}
      .settings, .score {{ grid-template-columns:1fr; }}
      .actions {{ flex-direction:column-reverse; }}
      .primary, .ghost, .danger {{ width:100%; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="bar">
      <div class="brand">
        <div class="mark">A2</div>
        <div>
          <h1>PAES Area 2 Exam Prep</h1>
          <p class="sub">Land and Water Resources Engineering practice quiz</p>
        </div>
      </div>
      <button class="ghost" onclick="resetHome()">Home</button>
    </div>
  </header>

  <main>
    <section id="home" class="screen active">
      <div class="panel home">
        <h2>Choose a subject and start practicing.</h2>
        <p class="lead">Questions are generated from the Area 2 PDF. Each item asks for the correct term from its definition, with four similar choices from the same subject. Answers and score appear only after the quiz is completed.</p>
        <div id="subjects" class="grid"></div>
        <div class="settings">
          <div>
            <label for="count">Number of questions (minimum 10)</label>
            <input id="count" type="number" min="10" value="10">
            <p id="countHelp" class="tiny">Question bank loaded: {len(bank)} items. {counts}.</p>
          </div>
          <button class="primary" onclick="startQuiz()">Start Quiz</button>
        </div>
      </div>
    </section>

    <section id="quiz" class="screen">
      <div class="quiz-wrap">
        <div class="progress-row"><span id="progressText"></span><span id="percentText"></span></div>
        <div class="track"><div id="fill" class="fill"></div></div>
        <div class="panel question">
          <span id="qSubject" class="tag"></span>
          <p id="qText" class="qtext"></p>
          <div id="options" class="options"></div>
          <div class="actions">
            <button class="danger" onclick="resetHome()">Abandon Quiz</button>
            <button id="nextBtn" class="primary" onclick="nextQuestion()" disabled>Next Question</button>
          </div>
        </div>
      </div>
    </section>

    <section id="results" class="screen">
      <div class="results">
        <div class="panel score">
          <div>
            <h2>Quiz complete.</h2>
            <p id="summary" class="lead"></p>
          </div>
          <div class="score-num" id="scoreNum"></div>
          <button class="primary" onclick="resetHome()">Practice Again</button>
        </div>
        <div id="review" class="review"></div>
      </div>
    </section>
  </main>

  <script>
    const questionBank = {data};
    const subjects = [...new Set(questionBank.map(q => q.subject))];
    let selectedSubject = subjects[0];
    let quiz = [];
    let index = 0;
    let answers = [];
    let selected = null;

    const byId = id => document.getElementById(id);

    function shuffle(array) {{
      const copy = [...array];
      for (let i = copy.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
      }}
      return copy;
    }}

    function show(id) {{
      document.querySelectorAll('.screen').forEach(el => el.classList.remove('active'));
      byId(id).classList.add('active');
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function renderSubjects() {{
      byId('subjects').innerHTML = subjects.map(subject => {{
        const total = questionBank.filter(q => q.subject === subject).length;
        return `<button class="subject ${{subject === selectedSubject ? 'selected' : ''}}" onclick="selectSubject('${{subject.replace(/'/g, "\\\\'")}}')">
          <b>${{subject}}</b><span>${{total}} available questions</span>
        </button>`;
      }}).join('');
      updateCountLimit();
    }}

    function selectSubject(subject) {{
      selectedSubject = subject;
      renderSubjects();
    }}

    function updateCountLimit() {{
      const max = questionBank.filter(q => q.subject === selectedSubject).length;
      const count = byId('count');
      count.max = max;
      if (+count.value > max) count.value = max;
      if (+count.value < 10) count.value = Math.min(10, max);
    }}

    function answerKind(text) {{
      const value = String(text).trim();
      const startsNumeric = /^[<>~≈≤≥]?\\s*\\d/.test(value);
      const hasMeasurement = /\\b(sides?|mm|cm|m|km|ha|l\\/sec|mg\\/l|ppm|ppt|kph|year|years|month|months|mins?|w\\/sq\\.?m|%|c)\\b/i.test(value);
      return startsNumeric || (/\\d/.test(value) && hasMeasurement) ? 'value' : 'term';
    }}

    function makeQuestion(item, pool) {{
      const definitionIsValue = answerKind(item.definition) === 'value';
      const answerField = definitionIsValue ? 'definition' : 'term';
      const questionField = definitionIsValue ? 'term' : 'definition';
      const answer = item[answerField];
      const kind = answerKind(answer);
      const sameKind = pool.filter(q => q !== item && answerKind(q[answerField]) === kind && q[answerField] !== answer);
      const fallback = pool.filter(q => q !== item && q[answerField] !== answer);
      const source = sameKind.length >= 3 ? sameKind : fallback;
      const distractors = shuffle(source).slice(0, 3).map(q => q[answerField]);
      const choices = shuffle([answer, ...distractors]);
      return {{ ...item, answer, prompt: item[questionField], choices, correctIndex: choices.indexOf(answer) }};
    }}

    function startQuiz() {{
      const pool = questionBank.filter(q => q.subject === selectedSubject);
      const requested = Math.max(10, Math.min(parseInt(byId('count').value || '10', 10), pool.length));
      byId('count').value = requested;
      quiz = shuffle(pool).slice(0, requested).map(item => makeQuestion(item, pool));
      index = 0;
      answers = [];
      selected = null;
      show('quiz');
      renderQuestion();
    }}

    function renderQuestion() {{
      const q = quiz[index];
      selected = null;
      byId('qSubject').textContent = q.subject;
      byId('qText').textContent = q.prompt;
      byId('progressText').textContent = `Question ${{index + 1}} of ${{quiz.length}}`;
      byId('percentText').textContent = `${{Math.round((index / quiz.length) * 100)}}% complete`;
      byId('fill').style.width = `${{(index / quiz.length) * 100}}%`;
      byId('nextBtn').textContent = index === quiz.length - 1 ? 'Finish Quiz' : 'Next Question';
      byId('nextBtn').disabled = true;
      byId('options').innerHTML = q.choices.map((choice, i) => `
        <button class="option" onclick="choose(${{i}})" id="opt${{i}}">
          <span class="letter">${{String.fromCharCode(65 + i)}}</span>
          <span>${{escapeHtml(choice)}}</span>
        </button>`).join('');
    }}

    function escapeHtml(value) {{
      return String(value).replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
    }}

    function choose(choiceIndex) {{
      selected = choiceIndex;
      document.querySelectorAll('.option').forEach(el => el.classList.remove('selected'));
      byId(`opt${{choiceIndex}}`).classList.add('selected');
      byId('nextBtn').disabled = false;
    }}

    function nextQuestion() {{
      if (selected === null) return;
      answers[index] = selected;
      if (index < quiz.length - 1) {{
        index += 1;
        renderQuestion();
      }} else {{
        showResults();
      }}
    }}

    function showResults() {{
      const correct = quiz.reduce((sum, q, i) => sum + (answers[i] === q.correctIndex ? 1 : 0), 0);
      const pct = Math.round((correct / quiz.length) * 100);
      byId('scoreNum').textContent = `${{pct}}%`;
      byId('summary').textContent = `You scored ${{correct}} out of ${{quiz.length}} in ${{selectedSubject}}. Review the correct answers below.`;
      byId('review').innerHTML = quiz.map((q, i) => {{
        const ok = answers[i] === q.correctIndex;
        return `<div class="panel review-card ${{ok ? 'good' : 'bad'}}">
          <p class="tiny">Question ${{i + 1}} - ${{q.subject}}</p>
          <p><b>Definition:</b> ${{escapeHtml(q.definition)}}</p>
          <p><b>Your answer:</b> ${{escapeHtml(q.choices[answers[i]])}}</p>
          <p><b>Correct answer:</b> ${{escapeHtml(q.answer)}}</p>
        </div>`;
      }}).join('');
      byId('fill').style.width = '100%';
      show('results');
    }}

    function resetHome() {{
      quiz = [];
      answers = [];
      index = 0;
      selected = null;
      renderSubjects();
      show('home');
    }}

    byId('count').addEventListener('input', updateCountLimit);
    renderSubjects();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bank = build_bank()
    OUT.write_text(build_html(bank), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Questions: {len(bank)}")
    counts = {}
    for item in bank:
        counts[item["subject"]] = counts.get(item["subject"], 0) + 1
    for subject, count in counts.items():
        print(f"{subject}: {count}")
