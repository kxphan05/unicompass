from rapidfuzz import fuzz, process

from app.agents.base_agent import BaseUniversityAgent

FUZZY_THRESHOLD = 70  # rapidfuzz scores 0-100

# Map of keywords → NTU school page (pattern: ntu.edu.sg/<school>)
_NTU_SCHOOLS = [
    (
        ["computer science", "computing", "data science", "information systems",
         "artificial intelligence", "cybersecurity", "software", "comp sci",
         "infocomm", "info sec"],
        "https://www.ntu.edu.sg/computing",
    ),
    (
        ["engineering", "mechanical", "electrical", "chemical", "civil",
         "biomedical engineering", "aerospace", "materials", "environmental",
         "mech eng", "elec eng", "chem eng", "biomed eng"],
        "https://www.ntu.edu.sg/engineering",
    ),
    (
        ["business", "accountancy", "finance", "management", "bba", "biz",
         "biz admin", "acct", "accounting", "marketing"],
        "https://www.ntu.edu.sg/business",
    ),
    (
        ["medicine", "medical", "mbbs", "surgery", "med"],
        "https://www.ntu.edu.sg/medicine",
    ),
    (
        ["science", "physics", "chemistry", "biology", "mathematics", "math",
         "statistics", "life science", "maths", "stats", "bio", "chem", "phys"],
        "https://www.ntu.edu.sg/science",
    ),
    (
        ["arts", "social science", "economics", "political science", "psychology",
         "sociology", "history", "philosophy", "literature", "linguistics",
         "english", "econs", "psych", "polisci", "chinese"],
        "https://www.ntu.edu.sg/humanities-arts-social-sciences",
    ),
    (
        ["education", "teaching", "nie", "pedagogy"],
        "https://www.ntu.edu.sg/education",
    ),
    (
        ["communication", "media", "journalism", "mass comm", "comms"],
        "https://www.ntu.edu.sg/communication",
    ),
    (
        ["art", "design", "animation", "film", "visual", "photography",
         "product design", "art design media"],
        "https://www.ntu.edu.sg/art-design-media",
    ),
    (
        ["law", "legal", "llb"],
        "https://www.ntu.edu.sg/law",
    ),
]

# Flat list for rapidfuzz
_ALL_KEYWORDS: list[str] = []
_KEYWORD_TO_URL: dict[str, str] = {}
for _kws, _url in _NTU_SCHOOLS:
    for _kw in _kws:
        _ALL_KEYWORDS.append(_kw)
        _KEYWORD_TO_URL[_kw] = _url

# Always-included URLs
_NTU_COMMON_URLS = [
    "https://www.ntu.edu.sg/admissions/undergraduate/scholarships",
]


class NTUAgent(BaseUniversityAgent):
    def __init__(self) -> None:
        super().__init__(
            university="NTU",
            full_name="Nanyang Technological University",
            website="ntu.edu.sg",
            seed_urls=[
                "https://www.ntu.edu.sg/admissions/undergraduate-programmes",
                "https://www.ntu.edu.sg/admissions/undergraduate/scholarships",
            ],
            color="#C4122F",
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
            # Skip short keywords that match as substrings of unrelated words
            if len(keyword) < 4 and score < 100:
                continue
            url = _KEYWORD_TO_URL[keyword]
            if url not in urls:
                urls.append(url)

        # Cap at 2 school URLs
        urls = urls[:2]

        # Fallback to general admissions page
        if not urls:
            urls.append("https://www.ntu.edu.sg/admissions/undergraduate-programmes")

        urls.extend(_NTU_COMMON_URLS)
        return urls
