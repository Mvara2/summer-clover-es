import sys, json
import UnityPy
from common import read_mono_name, find_length_prefixed_strings
from patch_filters import get_content_entries

script_name = sys.argv[1]
path = r"C:\Program Files (x86)\Steam\steamapps\common\ConnectionGame\SummerClover\SummerClover_Data\resources.assets.ORIGINAL_BACKUP"
env = UnityPy.load(path)

name_map = json.load(open("extracted/name_map.json", encoding="utf-8"))
candidates = name_map[script_name]

headers = {}
for obj in env.objects:
    for c in candidates:
        if obj.path_id == c["path_id"]:
            raw = obj.get_raw_data()
            hstrs = find_length_prefixed_strings(raw, 0, max_len=300)
            h = None
            for off, text in hstrs:
                if 'localization document' in text:
                    h = text; break
            headers[c["path_id"]] = h

print(json.dumps(headers, ensure_ascii=False, indent=2))

en_id = None
ko_id = None
for pid, h in headers.items():
    if h and 'to English' in h:
        en_id = pid
    if h and 'to Korean' in h:
        ko_id = pid

if en_id is None or ko_id is None:
    raise SystemExit(f"could not find EN/KO path_ids in headers: {headers}")

def load_entries(path_id):
    for obj in env.objects:
        if obj.path_id == path_id:
            raw = obj.get_raw_data()
            name, ds = read_mono_name(raw)
            if name != script_name:
                raise SystemExit(f"name mismatch at {path_id}: {name}")
            return get_content_entries(raw, ds, script_name)
    raise SystemExit(f"path_id {path_id} not found")

en_entries = load_entries(en_id)
ko_entries = load_entries(ko_id)

print("EN entries:", len(en_entries), " KO entries:", len(ko_entries), " KO path_id:", ko_id)

if len(en_entries) != len(ko_entries):
    raise SystemExit("EN/KO count mismatch -- extraction filters disagree, inspect manually")

pairs = []
for (off_en, en_text), (off_ko, ko_text) in zip(en_entries, ko_entries):
    pairs.append({"en": en_text, "ko_bytes": len(ko_text.encode("utf-8"))})

with open(f"{script_name}_pair.json", "w", encoding="utf-8") as f:
    json.dump(pairs, f, ensure_ascii=False, indent=2)

print(f"wrote {script_name}_pair.json with {len(pairs)} entries. KO path_id for patching: {ko_id}")
