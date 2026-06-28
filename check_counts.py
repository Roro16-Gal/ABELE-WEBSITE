import re

import generate_paes as g


text = g.extract_pdf_text(g.PDF)
for section, body in g.split_sections(text).items():
    matches = list(re.finditer(r"(?m)^\s*(\d+)\.\s+", body))
    parsed = g.parse_entries(section, body)
    if len(matches) == len(parsed):
        continue
    print("---", section, "raw", len(matches), "parsed", len(parsed))
    parsed_nums = {p["id"].split("-")[-1] for p in parsed}
    for i, match in enumerate(matches):
        num = match.group(1)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = g.clean_text(body[start:end])
        if num not in parsed_nums and chunk:
            print(num, chunk[:260])
