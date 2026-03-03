from rapidfuzz import fuzz, process

from app.agents.base_agent import BaseUniversityAgent

FUZZY_THRESHOLD = 70

_SMU_SCHOOLS = [
    (
        ["computer science", "computing", "information systems", "software",
         "cybersecurity", "data science", "artificial intelligence", "comp sci",
         "infocomm", "info sec"],
        "https://scis.smu.edu.sg/programmes",
    ),
    (
        ["business", "management", "bba", "finance", "marketing", "operations",
         "biz", "biz admin", "strategic management"],
        "https://business.smu.edu.sg/programmes",
    ),
    (
        ["accountancy", "accounting", "acct", "audit", "tax"],
        "https://accountancy.smu.edu.sg/programmes",
    ),
    (
        ["economics", "econs", "econometrics", "political science", "polisci",
         "public policy"],
        "https://economics.smu.edu.sg/programmes",
    ),
    (
        ["law", "legal", "llb", "jurisprudence"],
        "https://law.smu.edu.sg/programmes",
    ),
    (
        ["social science", "psychology", "sociology", "politics",
         "psych", "socio"],
        "https://socsc.smu.edu.sg/programmes",
    ),
    (
        ["arts", "humanities", "literature", "philosophy", "history",
         "communications", "mass comm", "english", "linguistics"],
        "https://socsc.smu.edu.sg/programmes",
    ),
    (
        ["science", "physics", "chemistry", "biology", "mathematics", "math",
         "statistics", "maths", "stats"],
        "https://scis.smu.edu.sg/programmes",
    ),
]

_ALL_KEYWORDS: list[str] = []
_KEYWORD_TO_URL: dict[str, str] = {}
for _kws, _url in _SMU_SCHOOLS:
    for _kw in _kws:
        _ALL_KEYWORDS.append(_kw)
        _KEYWORD_TO_URL[_kw] = _url

_SMU_COMMON_URLS = [
    "https://admissions.smu.edu.sg/scholarships-financial-aid",
]


class SMUAgent(BaseUniversityAgent):
    def __init__(self) -> None:
        super().__init__(
            university="SMU",
            full_name="Singapore Management University",
            website="smu.edu.sg",
            seed_urls=[
                "https://admissions.smu.edu.sg/programmes",
                "https://admissions.smu.edu.sg/scholarships-financial-aid",
            ],
            color="#0033A0",
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
            urls.append("https://admissions.smu.edu.sg/programmes")

        urls.extend(_SMU_COMMON_URLS)
        return urls
