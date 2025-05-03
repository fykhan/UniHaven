import json
import os
from django.conf import settings

DATA_PATH = os.path.join(settings.BASE_DIR, 'data/universities.json')

def load_universities():
    with open(DATA_PATH) as f:
        return json.load(f)["universities"]

def get_university_choices():
    return [(u["code"], u["name"]) for u in load_universities()]

def get_all_locations():
    result = {}
    for u in load_universities():
        for label, coords in u["campuses"].items():
            key = f"{u['code']} - {label}"
            result[key] = tuple(coords)
    return result
