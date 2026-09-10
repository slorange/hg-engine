#!/usr/bin/env python3
import json
import urllib.request

t = urllib.request.urlopen(
    "https://raw.githubusercontent.com/pret/pokeheartgold/master/src/data/map_headers/map_headers.json",
    timeout=30,
).read()
data = json.loads(t)
for entry in data:
    if entry.get("id") in ("MAP_ROUTE_44", "MAP_R44", "MAP_ROUTE_47"):
        print(entry)
