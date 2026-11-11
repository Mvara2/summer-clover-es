import re
from common import find_length_prefixed_strings

BASE_KNOWN = {"Naninovel","Elringus.Naninovel.Runtime","EmptyScriptLine","LabelScriptLine",
         "CommentScriptLine","GenericTextScriptLine","Naninovel.Commands","PrintText",
         "UnityEngine.DMAT","FAKE_ASM","Terminus","{Me}", "ChoiceScriptLine",
         "Naninovel.Commands.CG", "AudioScriptLine", "CommandScriptLine",
         "GirlA","Sizuko","Sizuko2","Kasumi","Ayano","Shizuku","All","PlaySfx",
         "WaitForInput","ModifyCharacter","Ayano2","Kasumi2","Shizuku2","Sizuko3",
         "InputCustomVariable","Me","Protagonist","KasumiFace","AyanoFace","ShizukuFace",
         "SizukoFace","KasumiFree","AyanoFree","ShizukuFree","SizukoFree","주인공",
         "AddChoice","ChoiceScriptLine","SkipInput","Goto","End","01_Main",
         "Ayano?","Kasumi?","Shizuku?","Sizuko?","ShowToastUI","ShowToastUI2",
         "ModifyBackground","ModifyCharacter2","PlayAnimation"}
hex_re = re.compile(r"^[0-9a-f]{5,10}$")
sfx_re = re.compile(r"^SE\d+$")
assign_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*[!=<>]=?\s*-?\d+$")
varref_re = re.compile(r"^\{[A-Za-z_][A-Za-z0-9_]*\}$")
colorhex_re = re.compile(r"^#[0-9a-fA-F]{3,8}$")
cgname_re = re.compile(r"^[A-Za-z]+CG\d+")

def is_metadata(text, script_name):
    if text in BASE_KNOWN or text == script_name: return True
    if hex_re.match(text): return True
    if sfx_re.match(text): return True
    if assign_re.match(text): return True
    if varref_re.match(text): return True
    if colorhex_re.match(text): return True
    if cgname_re.match(text): return True
    if text.startswith("Chinese (T)"): return True
    if text.startswith("@"): return True
    if len(text) <= 1: return True
    return False

def get_content_entries(raw, ds, script_name=None):
    strs = find_length_prefixed_strings(raw, ds)
    out = []
    for off, text in strs:
        if is_metadata(text, script_name): continue
        if any('一' <= c <= '鿿' for c in text): continue
        if re.match(r'^\{?[A-Za-z_][A-Za-z0-9_]*\}?:\s', text): continue
        out.append((off, text))
    return out
