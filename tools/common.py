import struct

def read_mono_name(raw):
    if len(raw) < 32:
        return None, None
    length = struct.unpack_from('<i', raw, 28)[0]
    if length < 0 or 32 + length > len(raw):
        return None, None
    try:
        name = raw[32:32+length].decode('utf-8')
    except Exception:
        return None, None
    pad = (4 - length % 4) % 4
    data_start = 32 + length + pad
    return name, data_start

def find_length_prefixed_strings(data, start=0, max_len=4000):
    """Find [int32 LE length][utf8 bytes] entries from start. Returns list of (offset_of_length_field, text)."""
    results = []
    n = len(data)
    i = start
    while i <= n - 4:
        length = struct.unpack_from('<i', data, i)[0]
        if 0 < length <= max_len and i + 4 + length <= n:
            chunk = data[i+4:i+4+length]
            try:
                text = chunk.decode('utf-8')
            except Exception:
                i += 1
                continue
            bad = sum(1 for c in text if ord(c) < 9)
            if bad == 0 and len(text) > 0:
                results.append((i, text))
                i += 4 + length
                continue
        i += 1
    return results
