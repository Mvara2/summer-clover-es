import os, json, UnityPy

RESOURCES_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\ConnectionGame\SummerClover\SummerClover_Data\resources.assets"

translations = json.load(open(
    r"C:\Users\varam\AppData\Local\Temp\claude\0c634e3b31f16935\39e888d1-0b7e-40fc-853f-7ddfc9a2076a\scratchpad\clover_tools\menu_translations2.json",
    encoding="utf-8"))

target_map = {
  "Shop": 874, "Riverside": 888, "Actor": 927, "Abandoned": 944,
  "Sex": 969, "Story": 973, "Mountain": 991
}

base_dir = r"C:\Users\varam\AppData\Local\Temp\claude\0c634e3b31f16935\39e888d1-0b7e-40fc-853f-7ddfc9a2076a\scratchpad\clover_tools\extracted\resources_text"
manifest = json.load(open(os.path.join(base_dir, "_manifest.json"), encoding="utf-8"))
pid_to_file = {m["path_id"]: m["file"] for m in manifest}

env = UnityPy.load(RESOURCES_PATH)

def build_new_content(category, ko_path_id):
    fpath = os.path.join(base_dir, pid_to_file[ko_path_id])
    with open(fpath, encoding="utf-8") as f:
        lines = f.read().splitlines()
    trans = translations.get(category, {})
    out_lines = []
    replaced = 0
    total_keys = 0
    for line in lines:
        if line.startswith(";") or ":" not in line:
            out_lines.append(line)
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        total_keys += 1
        if key in trans:
            out_lines.append(f"{key}: {trans[key]}")
            replaced += 1
        else:
            out_lines.append(line)
    if out_lines and out_lines[0].startswith(";"):
        out_lines[0] = "; Chinese (T) <zh-TW> to Spanish <es> localization document for `" + category + "` managed text document"
    return "\n".join(out_lines), replaced, total_keys

patched_objects = 0
for obj in env.objects:
    if obj.type.name != "TextAsset":
        continue
    data = obj.read()
    name = data.m_Name
    if name in target_map and obj.path_id == target_map[name]:
        new_content, replaced, total_keys = build_new_content(name, obj.path_id)
        data.m_Script = new_content
        data.save()
        patched_objects += 1
        print(f"{name} (path_id={obj.path_id}): replaced {replaced}/{total_keys} keys")

print("total TextAssets patched:", patched_objects)

env.save(out_path=r"C:\Users\varam\AppData\Local\Temp\claude\0c634e3b31f16935\39e888d1-0b7e-40fc-853f-7ddfc9a2076a\scratchpad\clover_tools\patched_menu2")
print("saved")
