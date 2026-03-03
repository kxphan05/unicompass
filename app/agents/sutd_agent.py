from rapidfuzz import fuzz, process

from app.agents.base_agent import BaseUniversityAgent

FUZZY_THRESHOLD = 70

# SUTD has a unique pillar system rather than traditional faculties
_SUTD_PILLARS = [
    (
        ["computer science", "computing", "software", "cybersecurity",
         "data science", "artificial intelligence", "comp sci", "infocomm",
         "info sec", "information systems"],
        "https://istd.sutd.edu.sg/",
    ),
    (
        ["engineering", "mechanical", "electrical", "chemical", "civil",
         "biomedical engineering", "environmental", "materials", "aerospace",
         "mech eng", "elec eng", "chem eng", "biomed eng", "robotics",
         "systems", "product development"],
        "https://epd.sutd.edu.sg/",
    ),
    (
        ["architecture", "urban", "landscape", "built environment",
         "sustainable design", "archi", "design"],
        "https://asd.sutd.edu.sg/",
    ),
    (
        ["science", "mathematics", "math", "physics", "chemistry", "biology",
         "maths", "stats", "statistics"],
        "https://smt.sutd.edu.sg/",
    ),
    (
        ["business", "management", "entrepreneurship", "innovation",
         "technology management", "biz"],
        "https://hass.sutd.edu.sg/",
    ),
    (
        ["arts", "humanities", "social science", "economics", "psychology",
         "philosophy", "sociology", "econs", "psych"],
        "https://hass.sutd.edu.sg/",
    ),
    (
        ["design", "industrial design", "product design", "ux", "ui",
         "user experience", "interaction design"],
        "https://dai.sutd.edu.sg/",
    ),
]

_ALL_KEYWORDS: list[str] = []
_KEYWORD_TO_URL: dict[str, str] = {}
for _kws, _url in _SUTD_PILLARS:
    for _kw in _kws:
        _ALL_KEYWORDS.append(_kw)
        _KEYWORD_TO_URL[_kw] = _url

_SUTD_COMMON_URLS = [
    "https://www.sutd.edu.sg/admissions/undergraduate/scholarships",
]


class SUTDAgent(BaseUniversityAgent):
    def __init__(self) -> None:
        super().__init__(
            university="SUTD",
            full_name="Singapore University of Technology and Design",
            website="sutd.edu.sg",
            seed_urls=[
                "https://www.sutd.edu.sg/admissions/undergraduate",
                "https://www.sutd.edu.sg/admissions/undergraduate/scholarships",
            ],
            color="#E4002B",
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
            urls.append("https://www.sutd.edu.sg/admissions/undergraduate")

        urls.extend(_SUTD_COMMON_URLS)
        return urls
