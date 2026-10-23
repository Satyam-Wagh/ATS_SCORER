from rapidfuzz import fuzz

SKILL_ALIASES: dict[str, str] = {
    'reactjs':       'react',
    'react.js':      'react',
    'angularjs':     'angular',
    'vuejs':         'vue',
    'vue.js':        'vue',
    'nextjs':        'next.js',
    'nodejs':        'node.js',
    'node':          'node.js',
    'expressjs':     'express',
    'express.js':    'express',
    'springboot':    'spring boot',
    'golang':        'go',
    'ml':            'machine learning',
    'ai':            'artificial intelligence',
    'nlp':           'natural language processing',
    'cv':            'computer vision',
    'k8s':           'kubernetes',
    'sklearn':       'scikit-learn',
    'postgres':      'postgresql',
    'dotnet':        '.net',
    'tailwindcss':   'tailwind',
    'amazon web services': 'aws',
    'google cloud':  'gcp',
    'pyspark':       'spark',
    'huggingface':   'hugging face',
}

def normalize_skill(skill):
    cleaned=skill.strip().lower()
    return SKILL_ALIASES.get(cleaned,cleaned)

def fuzzy_match_keywords(
        resume_kewords:list,
        jd_keyword:list,
        threshold:int=80
):
    resume_normlized={normalize_skill(kw):kw for kw in resume_kewords}
    jd_normlized={normalize_skill(jw):jw for jw in jd_keyword}

    matched_jd_original=[]
    missing_jd_original=[]

    for jd_canon,jd_original in jd_normlized.items():
        #match cannonical(exact) keywords
        if jd_canon in resume_normlized:
            matched_jd_original.append(jd_original)
            continue

        #for fuzzy word
        best_score=0
        #cheak for each resume_key words with jd_canno
        for resume_cannon in resume_kewords:
            best_score=max(best_score,fuzz.token_sort_ratio(jd_canon,resume_cannon))

        if best_score>=threshold:
            matched_jd_original.append(jd_original)
        else:
            missing_jd_original.append(jd_original)

    return {
        "matched":matched_jd_original,
        "missing":missing_jd_original
    }