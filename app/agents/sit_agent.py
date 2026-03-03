from rapidfuzz import fuzz, process

from app.agents.base_agent import BaseUniversityAgent

FUZZY_THRESHOLD = 70

# SIT offers applied degree programmes, many with overseas university partners
_SIT_CLUSTERS = [
    (
        ["computer science", "computing", "software", "cybersecurity",
         "data science", "artificial intelligence", "comp sci", "infocomm",
         "info sec", "information systems", "digital communications"],
        "https://www.singaporetech.edu.sg/undergraduate-programmes/infocomm-technology",
    ),
    (
        ["engineering", "mechanical", "electrical", "civil", "aerospace",
         "sustainable infrastructure", "systems", "telematics",
         "mech eng", "elec eng", "naval architecture", "marine",
         "robotics"],
        "https://www.singaporetech.edu.sg/undergraduate-programmes/engineering",
    ),
    (
        ["business", "accountancy", "accounting", "finance", "management",
         "hospitality", "tourism", "biz", "biz admin", "acct",
         "supply chain", "logistics", "marketing"],
        "https://www.singaporetech.edu.sg/undergraduate-programmes/business",
    ),
    (
        ["food science", "food technology", "nutrition", "dietetics",
         "chemical engineering", "pharmaceutical"],
        "https://www.singaporetech.edu.sg/undergraduate-programmes/food-technology-science",
    ),
    (
        ["health science", "nursing", "physiotherapy", "occupational therapy",
         "radiography", "diagnostic", "radiation therapy", "sonography",
         "speech therapy"],
        "https://www.singaporetech.edu.sg/undergraduate-programmes/health-social-sciences",
    ),
    (
        ["design", "architecture", "interior", "game design", "animation",
         "archi", "built environment"],
        "https://www.singaporetech.edu.sg/undergraduate-programmes/design-specialised-businesses",
    ),
    (
        ["science", "mathematics", "math", "physics", "chemistry", "biology",
         "maths", "stats", "statistics"],
        "https://www.singaporetech.edu.sg/undergraduate-programmes/engineering",
    ),
    (
        ["arts", "social science", "economics", "psychology", "sociology",
         "communications", "econs", "psych"],
        "https://www.singaporetech.edu.sg/undergraduate-programmes/health-social-sciences",
    ),
]

_ALL_KEYWORDS: list[str] = []
_KEYWORD_TO_URL: dict[str, str] = {}
for _kws, _url in _SIT_CLUSTERS:
    for _kw in _kws:
        _ALL_KEYWORDS.append(_kw)
        _KEYWORD_TO_URL[_kw] = _url

_SIT_COMMON_URLS = [
    "https://www.singaporetech.edu.sg/admissions/scholarships-awards",
]


class SITAgent(BaseUniversityAgent):
    def __init__(self) -> None:
        super().__init__(
            university="SIT",
            full_name="Singapore Institute of Technology",
            website="singaporetech.edu.sg",
            seed_urls=[
                "https://www.singaporetech.edu.sg/undergraduate-programmes",
                "https://www.singaporetech.edu.sg/admissions/scholarships-awards",
            ],
            color="#0073CE",
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
            urls.append("https://www.singaporetech.edu.sg/undergraduate-programmes")

        urls.extend(_SIT_COMMON_URLS)
        return urls
