from rapidfuzz import fuzz, process

from app.agents.base_agent import BaseUniversityAgent

FUZZY_THRESHOLD = 70

_SUSS_SCHOOLS = [
    (
        ["business", "management", "finance", "marketing", "accounting",
         "accountancy", "bba", "biz", "biz admin", "acct", "human resource",
         "supply chain", "logistics"],
        "https://www.suss.edu.sg/programmes?category=S.R.+Nathan+School+of+Human+Development",
    ),
    (
        ["computer science", "computing", "information systems", "software",
         "cybersecurity", "data science", "artificial intelligence", "comp sci",
         "infocomm", "info sec", "analytics"],
        "https://www.suss.edu.sg/programmes?category=School+of+Science+and+Technology",
    ),
    (
        ["science", "mathematics", "math", "statistics", "engineering",
         "maths", "stats", "physics", "chemistry", "biology"],
        "https://www.suss.edu.sg/programmes?category=School+of+Science+and+Technology",
    ),
    (
        ["arts", "social science", "humanities", "psychology", "sociology",
         "economics", "english", "chinese", "mass communication",
         "communications", "literature", "linguistics", "econs", "psych",
         "socio", "polisci", "political science", "counselling",
         "early childhood", "social work", "education", "teaching"],
        "https://www.suss.edu.sg/programmes?category=S.R.+Nathan+School+of+Human+Development",
    ),
    (
        ["law", "legal", "llb"],
        "https://www.suss.edu.sg/programmes?category=School+of+Law",
    ),
]

_ALL_KEYWORDS: list[str] = []
_KEYWORD_TO_URL: dict[str, str] = {}
for _kws, _url in _SUSS_SCHOOLS:
    for _kw in _kws:
        _ALL_KEYWORDS.append(_kw)
        _KEYWORD_TO_URL[_kw] = _url

_SUSS_COMMON_URLS = [
    "https://www.suss.edu.sg/part-time-undergraduate/scholarships-and-financial-aid",
]


class SUSSAgent(BaseUniversityAgent):
    def __init__(self) -> None:
        super().__init__(
            university="SUSS",
            full_name="Singapore University of Social Sciences",
            website="suss.edu.sg",
            seed_urls=[
                "https://www.suss.edu.sg/full-time-undergraduate",
                "https://www.suss.edu.sg/part-time-undergraduate/scholarships-and-financial-aid",
            ],
            color="#5B2D8E",
        )

    def get_urls_for_course(self, course: str) -> list[str]:
        course_lower = course.lower()

        matches = process.extract(
            course_lower,
            _ALL_KEYWORDS,
            scorer=fuzz.WRatio,
            score_cutoff=FUZZY_THRESHOLD,
            limit=5,
        )

        urls: list[str] = []
        best_score = matches[0][1] if matches else 0
        for keyword, score, _idx in matches:
            if score < best_score - 10:
                break
            if len(keyword) < 4 and score < 100:
                continue
            url = _KEYWORD_TO_URL[keyword]
            if url not in urls:
                urls.append(url)

        urls = urls[:2]

        if not urls:
            urls.append("https://www.suss.edu.sg/full-time-undergraduate")

        urls.extend(_SUSS_COMMON_URLS)
        return urls
