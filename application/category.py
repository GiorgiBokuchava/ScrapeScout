from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
from collections import defaultdict


@dataclass(frozen=True, slots=True)
class Category:
    key: str
    display: str
    group: str
    site_codes: Dict[str, str | int]


CATEGORIES: List[Category] = [
    Category(
        key="ALL", display="All Categories", group="all", site_codes={"jobs_ge": ""}
    ),
    Category(
        key="ADMIN_MANAGEMENT",
        display="Administration/Management",
        group="Business & Management",
        site_codes={"jobs_ge": 1},
    ),
    Category(
        key="FINANCE",
        display="Finance/Banking",
        group="Business & Management",
        site_codes={"jobs_ge": 3},
    ),
    Category(
        key="SALES",
        display="Sales",
        group="Business & Management",
        site_codes={"jobs_ge": 2},
    ),
    Category(
        key="PR_MARKETING",
        display="PR/Marketing",
        group="Business & Management",
        site_codes={"jobs_ge": 4},
    ),
    Category(
        key="IT_PROGRAMMING",
        display="IT/Programming",
        group="Tech & IT",
        site_codes={"jobs_ge": 6},
    ),
    Category(
        key="TECHNICAL",
        display="Technical/Engineering",
        group="Tech & IT",
        site_codes={"jobs_ge": 11},
    ),
    Category(
        key="LAW",
        display="Legal",
        group="Professional Services",
        site_codes={"jobs_ge": 7},
    ),
    Category(
        key="EDUCATION",
        display="Education/Teaching",
        group="Professional Services",
        site_codes={"jobs_ge": 12},
    ),
    Category(
        key="MEDICINE",
        display="Healthcare/Medical",
        group="Professional Services",
        site_codes={"jobs_ge": 8},
    ),
    Category(
        key="FOOD_SERVICE",
        display="Food Service",
        group="Service Industry",
        site_codes={"jobs_ge": 10},
    ),
    # Category(
    #     key="RETAIL",
    #     display="Retail",
    #     group="Service Industry",
    #     site_codes={},
    # ),
    Category(
        key="BEAUTY",
        display="Beauty/Fashion",
        group="Service Industry",
        site_codes={"jobs_ge": 14},
    ),
    Category(
        key="LOGISTICS",
        display="Logistics/Transportation",
        group="Support & Others",
        site_codes={"jobs_ge": 5},
    ),
    Category(
        key="SECURITY",
        display="Security",
        group="Support & Others",
        site_codes={"jobs_ge": 17},
    ),
    Category(
        key="CLEANING",
        display="Cleaning/Maintenance",
        group="Support & Others",
        site_codes={"jobs_ge": 16},
    ),
    Category(
        key="MEDIA",
        display="Media/Publishing",
        group="Support & Others",
        site_codes={"jobs_ge": 13},
    ),
    Category(
        key="OTHER",
        display="Other",
        group="Support & Others",
        site_codes={"jobs_ge": 9},
    ),
]

CAT_BY_KEY = {c.key: c for c in CATEGORIES}
SITE_TO_CAT = defaultdict(dict)
for cat in CATEGORIES:
    for site, code in cat.site_codes.items():
        SITE_TO_CAT[site][code] = cat


def cat_to_site_code(site: str, key: str) -> str | int | None:
    return CAT_BY_KEY[key].site_codes.get(site)


def site_code_to_cat(site: str, code: str | int) -> Category | None:
    return SITE_TO_CAT[site].get(code)


def groups() -> list[str]:
    return sorted({c.group for c in CATEGORIES if c.group != "ALL"})


def categories() -> list[str]:
    return [c for c in CATEGORIES]


def cats_of(group: str) -> list[Category]:
    return [c for c in CATEGORIES if c.group == group]
