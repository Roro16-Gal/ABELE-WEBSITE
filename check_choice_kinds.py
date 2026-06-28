import collections
import re

import generate_paes as g


def kind(term):
    value = term.strip()
    starts_numeric = re.search(r"^[<>~≈≤≥]?\s*\d", value)
    has_measure = re.search(
        r"\b(mm|cm|m|km|ha|l/sec|mg/l|ppm|ppt|kph|year|years|month|months|mins?|w/sq\.?m|%|c)\b",
        value,
        re.I,
    )
    return "value" if starts_numeric or (re.search(r"\d", value) and has_measure) else "term"


bank = g.build_bank()
counts = collections.Counter((item["subject"], kind(item["term"])) for item in bank)
for subject in dict.fromkeys(item["subject"] for item in bank):
    print(f"{subject}: terms={counts[(subject, 'term')]}, values={counts[(subject, 'value')]}")
