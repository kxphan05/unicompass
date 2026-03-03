from rapidfuzz import fuzz, process

from app.agents.base_agent import BaseUniversityAgent

FUZZY_THRESHOLD = 70  # rapidfuzz scores 0-100

# Map of keywords → faculty programme URLs
# Each entry: (keywords, programme_url)
_NUS_FACULTIES = [
    (
        ["computer science", "computing", "information systems", "information security",
         "data science", "business analytics", "software", "artificial intelligence",
         "cybersecurity", "comp sci", "infocomm", "info sec"],
        "https://www.comp.nus.edu.sg/programmes/ug/",
    ),
    (
        ["engineering", "mechanical", "electrical", "chemical", "civil",
         "biomedical engineering", "industrial", "environmental", "materials",
         "mech eng", "elec eng", "chem eng", "biomed eng"],
        "https://cde.nus.edu.sg/engineering/",
    ),
    (
        ["architecture", "urban", "landscape", "industrial design", "built environment",
         "archi"],
        "https://cde.nus.edu.sg/arch/",
    ),
    (
        ["business", "accountancy", "finance", "management", "bba", "biz",
         "biz admin", "acct", "accounting"],
        "https://bba.nus.edu.sg/academic-programmes/",
    ),
    (
        ["law", "legal", "llb"],
        "https://law.nus.edu.sg/programmes/",
    ),
    (
        ["medicine", "medical", "mbbs", "surgery", "med"],
        "https://medicine.nus.edu.sg/education/undergraduate/",
    ),
    (
        ["dentistry", "dental"],
        "https://www.dentistry.nus.edu.sg/Programmes/undergraduate.html",
    ),
    (
        ["pharmacy", "pharmaceutical", "pharma"],
        "https://pharmacy.nus.edu.sg/study-at-pharmacy/",
    ),
    (
        ["science", "physics", "chemistry", "biology", "mathematics", "math",
         "statistics", "life science", "quantitative finance", "food science",
         "maths", "stats", "bio", "chem", "phys"],
        "https://www.science.nus.edu.sg/undergraduates/",
    ),
    (
        ["arts", "social science", "economics", "political science", "psychology",
         "sociology", "history", "philosophy", "literature", "geography",
         "communications", "linguistics", "anthropology", "english",
         "econs", "psych", "polisci", "socio", "mass comm"],
        "https://fass.nus.edu.sg/undergraduate-programmes/",
    ),
]

# Flat list of all keywords for process.extract
_ALL_KEYWORDS: list[str] = []
_KEYWORD_TO_URL: dict[str, str] = {}
for _kws, _url in _NUS_FACULTIES:
    for _kw in _kws:
        _ALL_KEYWORDS.append(_kw)
        _KEYWORD_TO_URL[_kw] = _url

# Always-included URLs
_NUS_COMMON_URLS = [
    "https://www.nus.edu.sg/oam/scholarships",
]


class NUSAgent(BaseUniversityAgent):
    def __init__(self) -> None:
        super().__init__(
            university="NUS",
            full_name="National University of Singapore",
            website="nus.edu.sg",
            seed_urls=[
                "https://www.nus.edu.sg/oam/undergraduate-programmes",
                "https://www.nus.edu.sg/oam/scholarships",
            ],
            color="#003D7C",
        )

    def get_urls_for_course(self, course: str) -> list[str]:
        course_lower = course.lower()

        # Use rapidfuzz to find best matching keywords
        matches = process.extract(
            course_lower,
            _ALL_KEYWORDS,
            scorer=fuzz.WRatio,
            score_cutoff=FUZZY_THRESHOLD,
            limit=5,
        )

        # Deduplicate URLs, preserving order by score
        # Only keep secondary matches if they score within 10 points of the best
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

        # Cap at 2 faculty URLs to keep context manageable
        urls = urls[:2]

        # If no match, fall back to the general OAM programmes page
        if not urls:
            urls.append("https://www.nus.edu.sg/oam/undergraduate-programmes")

        # Always add common URLs
        urls.extend(_NUS_COMMON_URLS)
        return urls
