import json
import re


html = open("outputs/paes.html", encoding="utf-8").read()
bank = json.loads(re.search(r"const questionBank = (\[.*?\]);", html, re.S).group(1))


def answer_kind(text):
    value = str(text).strip()
    starts_numeric = re.search(r"^[<>~≈≤≥]?\s*\d", value)
    has_measure = re.search(
        r"\b(sides?|mm|cm|m|km|ha|l/sec|mg/l|ppm|ppt|kph|year|years|month|months|mins?|w/sq\.?m|%|c)\b",
        value,
        re.I,
    )
    return "value" if starts_numeric or (re.search(r"\d", value) and has_measure) else "term"


def make_question(item, pool):
    definition_is_value = answer_kind(item["definition"]) == "value"
    term_is_value = answer_kind(item["term"]) == "value"
    answer_field = "definition" if definition_is_value else "term"
    question_field = "term" if definition_is_value else "definition"
    answer = item[answer_field]
    kind = answer_kind(answer)
    source = [
        q
        for q in pool
        if q is not item and answer_kind(q[answer_field]) == kind and q[answer_field] != answer
    ]
    choices = [answer] + [q[answer_field] for q in source[:3]]
    return {
        "prompt": item[question_field],
        "answer": answer,
        "kinds": [answer_kind(choice) for choice in choices],
        "choices": choices,
        "term_is_value": term_is_value,
    }


for subject, term in [("Mathematics", "Quadrilateral"), ("Aquaculture", "5ppm"), ("General Terminologies", "Aquifer")]:
    pool = [q for q in bank if q["subject"] == subject]
    item = next(q for q in pool if q["term"] == term)
    print(subject, term, make_question(item, pool))
