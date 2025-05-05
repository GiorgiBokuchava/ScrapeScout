# Master configuration that all sites will map to
MASTER_CONFIG = {
    "locations": {
        "ALL": "All Locations",
        # Regions
        "TBILISI": "Tbilisi",
        "ADJARA": "Adjara",
        "IMERETI": "Imereti",
        "KAKHETI": "Kakheti",
        "KVEMO_KARTLI": "Kvemo Kartli",
        "SHIDA_KARTLI": "Shida Kartli",
        "SAMEGRELO": "Samegrelo-Zemo Svaneti",
        "SAMTSKHE": "Samtskhe-Javakheti",
        "MTSKHETA": "Mtskheta-Mtianeti",
        "GURIA": "Guria",
        "ABKHAZIA": "Abkhazia",
        "RACHA": "Racha-Lechkhumi and Kvemo Svaneti",
        # Special locations
        "REMOTE": "Remote",
        "ABROAD": "Abroad",
    },
    "categories": {
        "ALL": "All Categories",
        # Business & Management
        "ADMIN_MANAGEMENT": "Administration/Management",
        "FINANCE": "Finance/Banking",
        "SALES": "Sales",
        "PR_MARKETING": "PR/Marketing",
        # Tech & IT
        "IT_PROGRAMMING": "IT/Programming",
        "TECHNICAL": "Technical/Engineering",
        # Professional Services
        "LAW": "Legal",
        "EDUCATION": "Education/Teaching",
        "MEDICINE": "Healthcare/Medical",
        # Service Industry
        "FOOD_SERVICE": "Food Service",
        "RETAIL": "Retail",
        "BEAUTY": "Beauty/Fashion",
        # Support & Others
        "LOGISTICS": "Logistics/Transportation",
        "SECURITY": "Security",
        "CLEANING": "Cleaning/Maintenance",
        "MEDIA": "Media/Publishing",
        "OTHER": "Other",
    },
}

# Site-specific configurations with mappings to master config
search_config = {
    "jobs_ge": {
        "locations": {
            "": MASTER_CONFIG["locations"]["ALL"],
            1: MASTER_CONFIG["locations"]["TBILISI"],
            15: MASTER_CONFIG["locations"]["ABKHAZIA"],
            14: MASTER_CONFIG["locations"]["ADJARA"],
            9: MASTER_CONFIG["locations"]["GURIA"],
            8: MASTER_CONFIG["locations"]["IMERETI"],
            3: MASTER_CONFIG["locations"]["KAKHETI"],
            4: MASTER_CONFIG["locations"]["MTSKHETA"],
            12: MASTER_CONFIG["locations"]["RACHA"],
            13: MASTER_CONFIG["locations"]["SAMEGRELO"],
            7: MASTER_CONFIG["locations"]["SAMTSKHE"],
            5: MASTER_CONFIG["locations"]["KVEMO_KARTLI"],
            6: MASTER_CONFIG["locations"]["SHIDA_KARTLI"],
            16: MASTER_CONFIG["locations"]["ABROAD"],
            17: MASTER_CONFIG["locations"]["REMOTE"],
        },
        "categories": {
            "": MASTER_CONFIG["categories"]["ALL"],
            1: MASTER_CONFIG["categories"]["ADMIN_MANAGEMENT"],
            3: MASTER_CONFIG["categories"]["FINANCE"],
            2: MASTER_CONFIG["categories"]["SALES"],
            4: MASTER_CONFIG["categories"]["PR_MARKETING"],
            18: MASTER_CONFIG["categories"]["TECHNICAL"],
            5: MASTER_CONFIG["categories"]["LOGISTICS"],
            11: MASTER_CONFIG["categories"]["TECHNICAL"],
            16: MASTER_CONFIG["categories"]["CLEANING"],
            17: MASTER_CONFIG["categories"]["SECURITY"],
            6: MASTER_CONFIG["categories"]["IT_PROGRAMMING"],
            13: MASTER_CONFIG["categories"]["MEDIA"],
            12: MASTER_CONFIG["categories"]["EDUCATION"],
            7: MASTER_CONFIG["categories"]["LAW"],
            8: MASTER_CONFIG["categories"]["MEDICINE"],
            14: MASTER_CONFIG["categories"]["BEAUTY"],
            10: MASTER_CONFIG["categories"]["FOOD_SERVICE"],
            9: MASTER_CONFIG["categories"]["OTHER"],
        },
    },
    "another_site": {
        "locations": {
            "": MASTER_CONFIG["locations"]["ALL"],
            1: "New York",
            2: "San Francisco",
            3: MASTER_CONFIG["locations"]["REMOTE"],
        },
        "categories": {
            "": MASTER_CONFIG["categories"]["ALL"],
            1: MASTER_CONFIG["categories"]["TECHNICAL"],
            2: MASTER_CONFIG["categories"]["PR_MARKETING"],
            3: "Design",
        },
    },
}

job_keyword = ""  # &q=KEYWORD

search_preferences = {
    "job_location": "",
    "job_category": "",
    "job_keyword": job_keyword,
}


def get_master_to_site_mapping(site_name, category_type):
    """Get mapping from master config values to site-specific values.
    Maps from MASTER_CONFIG values to site-specific IDs/values.
    e.g. "Tbilisi" -> "1" for jobs.ge
    """
    mappings = {}
    site_config = search_config.get(site_name, {}).get(category_type, {})
    for site_val, master_val in site_config.items():
        # Skip empty values to avoid incorrect mappings
        if site_val != "":
            mappings[master_val] = site_val
    return mappings


def get_site_to_master_mapping(site_name, category_type):
    """Get mapping from site-specific values to master config values.
    Maps from site-specific IDs/values to MASTER_CONFIG values.
    e.g. "1" -> "Tbilisi" for jobs.ge
    """
    return search_config.get(site_name, {}).get(category_type, {})
