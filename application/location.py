from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from collections import defaultdict


@dataclass(frozen=True, slots=True)
class Location:
    """A city (or special place like Remote/Abroad)."""

    key: str
    display: str
    region: str
    site_codes: Dict[str, str | int]
    children: list[str] = field(default_factory=list)


LOCATIONS: List[Location] = [
    Location(
        key="ALL",
        display="All Locations",
        region="",
        site_codes={"jobs_ge": ""},
    ),
    Location(
        key="TBILISI",
        display="Tbilisi",
        region="Tbilisi",
        site_codes={"jobs_ge": 1, "jobs_am": 1},
        children=[],
    ),
    Location(
        key="ADJARA",
        display="Adjara",
        region="Adjara",
        site_codes={"jobs_ge": 14, "jobs_am": 14},
        children=sorted(
            [
                "Batumi",
                "Chakvi",
                "Gonio",
                "Keda",
                "Khelvachauri",
                "Khulo",
                "Kobuleti",
                "Makho",
                "Mukhaestate",
                "Ochkhamuri",
                "Sarpi",
                "Shuakhevi",
                "Tsikhisdziri",
            ]
        ),
    ),
    Location(
        key="IMERETI",
        display="Imereti",
        region="Imereti",
        site_codes={"jobs_ge": 8, "jobs_am": 8},
        children=sorted(
            [
                "Baghdati",
                "Boriti",
                "Chiatura",
                "Chikhori",
                "Chorvila",
                "Chqvishi",
                "Dghnorisa",
                "Etseri",
                "Godogani",
                "Gvishtibi",
                "Kharagauli",
                "Khoni",
                "Kulashi",
                "Kutaisi",
                "Kvakhchiri",
                "Kveda Sakara",
                "Mukhiani",
                "Puti",
                "Sachkhere",
                "Samtredia",
                "Shorapani",
                "Shrosha",
                "Skande",
                "Terjola",
                "Tsqaltubo",
                "Tqibuli",
                "Ubisi",
                "Vani",
                "Vartsikhe",
                "Zeda Sakara",
                "Zeda Simoneti",
                "Zestaponi",
                "Zovreti",
                "Zvare",
            ]
        ),
    ),
    Location(
        key="KVEMO_KARTLI",
        display="Kvemo Kartli",
        region="Kvemo Kartli",
        site_codes={"jobs_ge": 5, "jobs_am": 5},
        children=sorted(
            [
                "aghmamedlo",
                "akhkerpi",
                "algeti",
                "araplo",
                "azizkendi",
                "baidari",
                "bolnisi",
                "dmanisi",
                "gardabani",
                "khojorni",
                "kvemo orozmani",
                "kvemo sarali",
                "marneuli",
                "norio",
                "qizil-ajlo",
                "rustavi",
                "sabirkendi",
                "sadakhlo",
                "samshvilde",
                "sartichala",
                "tetri tsqaro",
                "tsalka",
            ]
        ),
    ),
    Location(
        key="SAMEGRELO",
        display="Samegrelo-Zemo Svaneti",
        region="Samegrelo-Zemo Svaneti",
        site_codes={"jobs_ge": 13, "jobs_am": 13},
        children=sorted(
            [
                "Abasha",
                "Abastumani",
                "Anaklia",
                "Bandza",
                "Bulvani",
                "Chkhorotsqu",
                "Dzveli Abasha",
                "Dzveli Khibula",
                "Gachedili",
                "Ganmukhuri",
                "Ingiri",
                "Jvari",
                "Khobi",
                "Kirovi",
                "Marani",
                "Martvili",
                "Mestia",
                "Nakhunavo",
                "Narazeni",
                "Poti",
                "Potskho-Etseri",
                "Senaki",
                "Tsalenjikha",
                "Zugdidi",
            ]
        ),
    ),
    Location(
        key="KAKHETI",
        display="Kakheti",
        region="Kakheti",
        site_codes={"jobs_ge": 3, "jobs_am": 3},
        children=sorted(
            [
                "Akhmeta",
                "Arboshiki",
                "Dedoplistsqaro",
                "Duisi",
                "Gurjaani",
                "Iormughanlo",
                "Kisiskhevi",
                "Kondoli",
                "Lagodekhi",
                "Mirzaani",
                "Nasamkhrali",
                "Ozaani",
                "Pshaveli",
                "Qvareli",
                "Sagarejo",
                "Sighnaghi",
                "Telavi",
                "Tsinandali",
                "Tsnori",
                "Zinobiani",
            ]
        ),
    ),
    Location(
        key="SHIDA_KARTLI",
        display="Shida Kartli",
        region="Shida Kartli",
        site_codes={"jobs_ge": 6, "jobs_am": 6},
        children=sorted(
            [
                "ali",
                "gori",
                "kareli",
                "kaspi",
                "kemperi",
                "khashuri",
                "kvemo chala",
                "kvishkheti",
                "tkotsa",
                "tsaghvli",
                "tskhinvali",
            ]
        ),
    ),
    Location(
        key="MTSKHETA",
        display="Mtskheta-Mtianeti",
        region="Mtskheta-Mtianeti",
        site_codes={"jobs_ge": 4, "jobs_am": 4},
        children=sorted(
            [
                "akhalgori",
                "dusheti",
                "java",
                "mtskheta",
                "natakhtari",
                "stepantsminda",
                "tianeti",
            ]
        ),
    ),
    Location(
        key="REMOTE",
        display="Remote",
        region="Remote",
        site_codes={"jobs_ge": 17},
        children=[],
    ),
    Location(
        key="GURIA",
        display="Guria",
        region="Guria",
        site_codes={"jobs_ge": 9, "jobs_am": 9},
        children=sorted(
            [
                "akhalsopeli",
                "askana",
                "baghdadi",
                "baileti",
                "bokhvauri",
                "chala",
                "chanieti",
                "chokhatauri",
                "dabali etseri",
                "dvabzu",
                "gaghma dvabzu",
                "gantiadi",
                "gomi",
                "grigoleti",
                "gurianta",
                "jumati",
                "kakuti",
                "khrialeti",
                "khvarbeti",
                "konchkati",
                "kvachalati",
                "kveda bakhvi",
                "kveda dzimiti",
                "kvemo makvaneti",
                "kvemo natanebi",
                "kviriketi",
                "lanchkhuti",
                "likhauri",
                "melekeduri",
                "meria",
                "motsvnari",
                "naghobilevi",
                "nagomari",
                "niabauri",
                "ozurgeti",
                "pampaleti",
                "shemokmedi",
                "shroma",
                "shua isnari",
                "silauri",
                "tkhinvali",
                "tsikhisperdi",
                "tsitelmta",
                "tskhemliskhidi",
                "vake",
                "vakijvari",
                "zeda bakhvi",
                "zeda dzimiti",
                "zeda uchkhubi",
                "zemo makvaneti",
                "zemo natanebi",
            ]
        ),
    ),
    Location(
        key="SAMTSKHE",
        display="Samtskhe-Javakheti",
        region="Samtskhe-Javakheti",
        site_codes={"jobs_ge": 7, "jobs_am": 7},
        children=sorted(
            [
                "Abastumani",
                "Adigeni",
                "Akhaldaba",
                "Akhalkalaki",
                "Akhaltsikhe",
                "Aspindza",
                "Borjomi",
                "Ninotsminda",
            ]
        ),
    ),
    Location(
        key="ABROAD",
        display="Abroad",
        region="Abroad",
        site_codes={"jobs_ge": 16},
        children=[],
    ),
    Location(
        key="RACHA",
        display="Racha-Lechkhumi and Kvemo Svaneti",
        region="Racha-Lechkhumi and Kvemo Svaneti",
        site_codes={"jobs_ge": 12, "jobs_am": 12},
        children=[
            "Ambrolauri",
            "Lentekhi",
            "Oni",
            "Tsageri",
        ],
    ),
    Location(
        key="ABKHAZIA",
        display="Abkhazia",
        region="Abkhazia",
        site_codes={"jobs_ge": 15},
        children=sorted(
            [
                "akhali atoni",
                "bedia",
                "beslakhuba",
                "bichvinta",
                "gagra",
                "gali",
                "ganarjiis mukhuri",
                "ghvada",
                "kultubani",
                "likhni",
                "machara",
                "mokvi",
                "ochamchire",
                "sokhumi",
                "tamishi",
                "tqvarcheli",
            ]
        ),
    ),
]


# Canonical key -> object
LOC_BY_KEY = {loc.key: loc for loc in LOCATIONS}
# For every site, map “site-specific code” -> Location
SITE_TO_LOC: dict[str, dict[str | int, Location]] = defaultdict(dict)
for loc in LOCATIONS:
    for site, code in loc.site_codes.items():
        SITE_TO_LOC[site][code] = loc

# from locations import LOC_BY_KEY, SITE_TO_LOC


# canonical -> site-specific
def loc_to_site_code(site: str, key: str) -> str | int | None:
    return LOC_BY_KEY[key].site_codes.get(site)


# site-specific -> canonical
def site_code_to_loc(site: str, code: str | int):
    return SITE_TO_LOC[site].get(code)  # returns Location | None


def regions() -> list[Location]:
    # return [loc for loc in LOCATIONS if loc.children]
    return [loc for loc in LOCATIONS]


def cities_of(region_key: str) -> list[Location]:
    return [LOC_BY_KEY[k] for k in LOC_BY_KEY[region_key].children]
