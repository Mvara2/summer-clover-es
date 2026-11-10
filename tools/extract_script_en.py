import sys, re, json
import UnityPy
from common import read_mono_name, find_length_prefixed_strings

script_name = sys.argv[1]
path = r"C:\Program Files (x86)\Steam\steamapps\common\ConnectionGame\SummerClover\SummerClover_Data\resources.assets.ORIGINAL_BACKUP"
env = UnityPy.load(path)

name_map = json.load(open("extracted/name_map.json", encoding="utf-8"))
candidates = name_map[script_name]

KNOWN = {"Naninovel","Elringus.Naninovel.Runtime","EmptyScriptLine","LabelScriptLine",
         "CommentScriptLine","GenericTextScriptLine","Naninovel.Commands","PrintText",
         script_name,"UnityEngine.DMAT","FAKE_ASM","Terminus","{Me}", "ChoiceScriptLine",
         "Naninovel.Commands.CG", "AudioScriptLine", "CommandScriptLine",
         "GirlA","Sizuko","Sizuko2","Kasumi","Ayano","Shizuku","All","PlaySfx",
         "WaitForInput","ModifyCharacter","CommandScriptLine"}
hex_re = re.compile(r"^[0-9a-f]{5,10}$")
sfx_re = re.compile(r"^SE\d+$")

def is_metadata(text):
    if text in KNOWN: return True
    if hex_re.match(text): return True
    if sfx_re.match(text): return True
    if text.startswith("Chinese (T)"): return True
    if text.startswith("@"): return True
    if len(text) <= 1: return True
    return False

def get_content(raw, ds, exclude_cjk):
    strs = find_length_prefixed_strings(raw, ds)
    out = []
    for off, text in strs:
        if is_metadata(text): continue
        if exclude_cjk and any('\u4e00' <= c <= '\u9fff' for c in text): continue
        if exclude_cjk and re.match(r'^[A-Za-z_][A-Za-z0-9_]*:\s', text): continue
        if len(text) < 1: continue
        out.append((off, text))
    return out

headers = {}
for obj in env.objects:
    for c in candidates:
        if obj.path_id == c["path_id"]:
            raw = obj.get_raw_data()
            name, ds = read_mono_name(raw)
            hstrs = find_length_prefixed_strings(raw, 0, max_len=300)
            h = None
            for off, text in hstrs:
                if 'localization document' in text:
                    h = text; break
            headers[c["path_id"]] = h

print(json.dumps(headers, ensure_ascii=False, indent=2))

en_id = None
for pid, h in headers.items():
    if h and 'to English' in h:
        en_id = pid
for obj in env.objects:
    if obj.path_id == en_id:
        raw = obj.get_raw_data()
        name, ds = read_mono_name(raw)
        content = get_content(raw, ds, exclude_cjk=True)
        print("EN path_id:", en_id, "entries:", len(content))
        with open(f"{script_name}_en.json", "w", encoding="utf-8") as f:
            json.dump([t for off, t in content], f, ensure_ascii=False, indent=2)
        break
