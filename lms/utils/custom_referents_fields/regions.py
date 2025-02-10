# ugly as sin but usable as-is and more compact
regions = [
    {"code_region": "01","nom_region": "Guadeloupe"},
    {"code_region": "02","nom_region": "Martinique"},
    {"code_region": "03","nom_region": "Guyane"},
    {"code_region": "04","nom_region": "La Réunion"},
    {"code_region": "06","nom_region": "Mayotte"},
    {"code_region": "11","nom_region": "Île-de-France"},
    {"code_region": "24","nom_region": "Centre-Val de Loire"},
    {"code_region": "27","nom_region": "Bourgogne-Franche-Comté"},
    {"code_region": "28","nom_region": "Normandie"},
    {"code_region": "32","nom_region": "Hauts-de-France"},
    {"code_region": "44","nom_region": "Grand Est"},
    {"code_region": "52","nom_region": "Pays de la Loire"},
    {"code_region": "53","nom_region": "Bretagne"},
    {"code_region": "75","nom_region": "Nouvelle-Aquitaine"},
    {"code_region": "76","nom_region": "Occitanie"},
    {"code_region": "84","nom_region": "Auvergne-Rhône-Alpes"},
    {"code_region": "93","nom_region": "Provence-Alpes-Côte d'Azur"},
    {"code_region": "94","nom_region": "Corse"}
]

region_dict = {region["nom_region"]: region["code_region"] for region in regions}

def lookup_region_code(region_name):
    return region_dict.get(region_name)