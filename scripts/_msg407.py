#!/usr/bin/env python3
import re
import urllib.request

t = urllib.request.urlopen(
    "https://raw.githubusercontent.com/pret/pokeheartgold/master/files/msgdata/msg/msg_0407_R47.gmm",
    timeout=30,
).read().decode()
for i, m in enumerate(re.findall(r'<language name="English">(.*?)</language>', t, re.S)):
    text = m.replace("\\n", " / ").replace("\\r", " ")[:120]
    print(f"[{i}] {text}")
