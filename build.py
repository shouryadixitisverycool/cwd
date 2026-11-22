#!/usr/bin/env python3
"""Scan <semester>/<course>/ folders and write index.html (the course catalogue).
Run after adding or removing files:  python3 build.py"""
import os, re, json, subprocess, html

ROOT = os.path.dirname(os.path.abspath(__file__))

COURSES = {   # folder -> (code, full name)
    'DnA': ('DnA', 'Data and Applications'),
    'AAD': ('AAD', 'Algorithm Analysis and Design'),
    'PnS': ('PnS', 'Probability and Statistics'),
    'History': ('HIST', 'History'),
}
SEMESTERS = {'2-1': 'Monsoon · Year 2'}

# nicer titles for files whose name or metadata says too little
TITLES = {
    'AAD/AAD-post-midsem-endsem-question-map.pdf': 'End-sem question map (post-mid-sem, Lec 14–24)',
    'AAD/AAD-post-midsem-study-guide.pdf': 'Post-mid-sem study guide',
    'AAD/midsem-study-guide.pdf': 'Mid-sem study guide',
    'AAD/midsem-question-map.pdf': 'Mid-sem question map',
    'AAD/hashing-question-map.pdf': 'Randomized hashing question map',
    'AAD/maxcut-exercises-solutions.pdf': 'Max-cut exercises with solutions',
    'AAD/max-flow-max-cut.pdf': 'Max-flow / min-cut',
    'AAD/max-flow-max-cut-one-hour.pdf': 'Max-flow / min-cut in one hour',
    'AAD/np-reductions-question-map.pdf': 'NP reductions question map',
    'AAD/randomized-approximation-quiz-practice.pdf': 'Randomized and approximation algorithms: quiz practice',
    'DnA/01-databases.pdf': 'Databases and database users (older PDF)',
    'DnA/dna-endsem-question-map.pdf': 'End-sem question map',
    'DnA/phase4_eval_prep.pdf': 'Phase 4 evaluation prep',
    'DnA/sql-guide.pdf': 'SQL guide',
    'History/quiz2_prep.pdf': 'Quiz 2 prep',
    'History/quiz2_model_answers.pdf': 'Quiz 2 model answers',
    'PnS/alternative_source_list.pdf': 'Alternative source list',
    'PnS/gaussian_iterated_expectation_sources.pdf': 'Gaussian and iterated expectation sources',
    'PnS/mgf_questions_solutions.pdf': 'MGF questions with solutions',
    'PnS/midsem_question_bank.pdf': 'Mid-sem question bank',
    'PnS/midsem_source_list.pdf': 'Mid-sem source list',
    'PnS/PnS_L21-L25_Question_List.pdf': 'Lectures 21–25 question list',
    'PnS/quiz2_question_list.pdf': 'Quiz 2 question list',
}

def pdf_pages(p):
    try:
        out = subprocess.run(['pdfinfo', p], capture_output=True, text=True).stdout
        m = re.search(r'^Pages:\s*(\d+)', out, re.M); return int(m.group(1)) if m else None
    except FileNotFoundError: return None

def pretty(name):
    s = re.sub(r'\.\w+$', '', name).replace('_', ' ').replace('-', ' ')
    return s[:1].upper() + s[1:]

data = []
for sem in sorted(d for d in os.listdir(ROOT) if re.fullmatch(r'\d-\d', d)):
    for course in sorted(os.listdir(os.path.join(ROOT, sem))):
        cdir = os.path.join(ROOT, sem, course)
        if not os.path.isdir(cdir): continue
        code, name = COURSES.get(course, (course, course))
        items = []
        for f in sorted(os.listdir(cdir)):
            path = os.path.join(cdir, f); rel = course + '/' + f
            if f.endswith('.html'):
                t = re.search(r'<title>(.*?)</title>', open(path, errors='ignore').read(4000), re.S)
                title = html.unescape(t.group(1).strip()) if t else pretty(f)
                m = re.match(r'DnA (\d+) · (.*)', title)
                kind, num = 'Guide', None
                if m: num, title = int(m.group(1)), m.group(2)
                items.append({'href': sem + '/' + rel, 'title': TITLES.get(rel, title), 'kind': 'guide',
                              'over': 'Topic %d' % num if num else 'Guide', 'meta': 'Interactive guide', 'num': num})
            elif f.endswith('.pdf'):
                n = pdf_pages(path)
                items.append({'href': sem + '/' + rel, 'title': TITLES.get(rel, pretty(f)), 'kind': 'pdf',
                              'over': 'PDF', 'meta': '%d pages' % n if n else 'PDF', 'num': None})
        items.sort(key=lambda x: (x['kind'] != 'guide', x['num'] or 0, x['title'].lower()))
        data.append({'id': course, 'code': code, 'name': name, 'term': SEMESTERS.get(sem, sem), 'items': items})

tpl = open(os.path.join(ROOT, 'index.template.html')).read()
open(os.path.join(ROOT, 'index.html'), 'w').write(tpl.replace('/*DATA*/[]', json.dumps(data, ensure_ascii=False)))
print('index.html:', ', '.join('%s (%d)' % (c['code'], len(c['items'])) for c in data))
