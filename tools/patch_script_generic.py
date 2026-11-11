import os, sys, json, struct, UnityPy
from common import read_mono_name
from patch_filters import get_content_entries

script_name = sys.argv[1]
ko_path_id = int(sys.argv[2])
es_file = sys.argv[3]
RESOURCES_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\ConnectionGame\SummerClover\SummerClover_Data\resources.assets"
OUT_DIR = sys.argv[4] if len(sys.argv) > 4 else r"C:\Users\varam\AppData\Local\Temp\claude\0c634e3b31f16935\39e888d1-0b7e-40fc-853f-7ddfc9a2076a\scratchpad\clover_tools\patched_generic"
os.makedirs(OUT_DIR, exist_ok=True)

spanish_ordered = json.load(open(es_file, encoding="utf-8"))

env = UnityPy.load(RESOURCES_PATH)

target_obj = None
for obj in env.objects:
    if obj.path_id == ko_path_id:
        target_obj = obj
        break

if target_obj is None:
    raise SystemExit(f"path_id {ko_path_id} not found")

raw = target_obj.get_raw_data()
name, ds = read_mono_name(raw)
if name != script_name:
    raise SystemExit(f"name mismatch: expected {script_name}, got {name}")

ko_entries = get_content_entries(raw, ds, script_name)
print("Korean content entries found:", len(ko_entries))
print("Spanish translations available:", len(spanish_ordered))

if len(ko_entries) != len(spanish_ordered):
    print("MISMATCH! dumping both for inspection:")
    for i, (off, t) in enumerate(ko_entries):
        print(i, off, repr(t))
    raise SystemExit("Aborting: count mismatch, refusing to patch blindly")

# IMPORTANT: each individual entry must keep EXACTLY its own original byte length
# (not just the aggregate total) -- otherwise the game crashes on locale switch,
# confirmed empirically. So pad (if shorter) per-entry; abort listing any entry
# that is LONGER than its own original slot, so the translation can be shortened.
offset_info = {}
overflow = []
for (off, ko_text), es in zip(ko_entries, spanish_ordered):
    orig_len = len(ko_text.encode('utf-8'))
    es_bytes = es.encode('utf-8')
    if len(es_bytes) < orig_len:
        es_bytes = es_bytes + b' ' * (orig_len - len(es_bytes))
    elif len(es_bytes) > orig_len:
        overflow.append((off, orig_len, len(es_bytes), ko_text, es))
    offset_info[off] = (orig_len, es_bytes)

if overflow:
    print(f"{len(overflow)} entries exceed their individual original byte budget:")
    for off, orig_len, new_len, ko_text, es in overflow:
        print(f"  offset={off} orig_len={orig_len} new_len={new_len} over_by={new_len-orig_len}")
        print(f"    ko: {ko_text!r}")
        print(f"    es: {es!r}")
    raise SystemExit("Aborting: shorten the Spanish text for the entries listed above "
                      "so each individually fits within its original byte length.")

def patch_blob(raw, data_start, offset_map):
    out = bytearray(raw[:data_start])
    i = data_start
    n = len(raw)
    replaced = 0
    while i <= n - 4:
        length = struct.unpack_from('<i', raw, i)[0]
        if 0 < length <= 4000 and i + 4 + length <= n:
            chunk = raw[i+4:i+4+length]
            try:
                text = chunk.decode('utf-8')
            except Exception:
                text = None
            if text is not None:
                bad = sum(1 for c in text if ord(c) < 9)
                if bad == 0 and len(text) > 0:
                    if i in offset_map:
                        orig_len, new_bytes = offset_map[i]
                        out += struct.pack('<i', len(new_bytes))
                        out += new_bytes
                        replaced += 1
                    else:
                        out += raw[i:i+4+length]
                    i += 4 + length
                    continue
        out.append(raw[i])
        i += 1
    out += raw[i:]
    return bytes(out), replaced

new_raw, replaced = patch_blob(raw, ds, offset_info)
print(f"path_id={ko_path_id} name={name} replaced={replaced} old_size={len(raw)} new_size={len(new_raw)}")
assert len(new_raw) == len(raw), f"TOTAL SIZE MISMATCH: {len(new_raw)} vs {len(raw)}"
target_obj.set_raw_data(new_raw)

env.save(out_path=OUT_DIR)
print("saved to", OUT_DIR)
