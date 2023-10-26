#!/opt/homebrew/Caskroom/miniconda/base/bin/python3

import os
import json
import requests
import numpy as np
import urllib.parse
import matplotlib.pyplot as plt
from collections import defaultdict
from mpl_toolkits.basemap import Basemap

KEY="AIzaSyCuMCzvNjdpzYJMFR8BWmbGzO68HbHPkGA"

if os.path.exists("locations.json"):
    with open("locations.json") as inf:
        locations = json.load(inf)
else:
    locations = {}

def lookup_ll(loc):
  if loc in locations:
    return locations[loc]

  print ("looking up %s" % loc)
  q_loc = urllib.parse.quote_plus(loc)
  q = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (
      q_loc, KEY)

  print(q)
  response = requests.get(q)
  print(response)
  r = response.json()

  try:
    ll = r["results"][0]["geometry"]["location"]
  except Exception:
    import pprint
    pprint.pprint(r)
    raise

  pos = round(ll["lat"], 2), round(ll["lng"], 2)

  locations[loc] = pos
  return pos

data = defaultdict(lambda: defaultdict(list)) # type -> value -> [lat, lng]

abbr_locs = {}

try:
    with open("sheet-abbrs.tsv") as inf:
        cols = None
        for line in inf:
            bits = line.rstrip("\n").split("\t")
            if not cols:
                cols = bits
                continue

            abbr, raw_loc, _ = bits
            abbr_locs[abbr.lower()] = lookup_ll(raw_loc)                
finally:
    with open("locations.json", "w") as outf:
        json.dump(locations, outf)

with open("sheet-variation.tsv") as inf:
    cols = None
    for line in inf:
        bits = line.rstrip("\n").split("\t")
        if not cols:
            cols = bits
            continue

        abbr, prm, rlt, star, _ = bits
        abbr = abbr.lower()

        prm = {
            "S": "Skaters",
            "B": "Butterfly",
            "CT": "Courtesy",
        }[prm]

        rlt = {
            "H": "Hands",
            "NH": "No hands",
        }[rlt]

        star = {
            "L": "Center",
            "WG": "Wrist",
            "HA": "Hands Across",
        }[star]
        
        data["prm"][prm].append(abbr_locs[abbr])
        data["rlt"][rlt].append(abbr_locs[abbr])
        data["star"][star].append(abbr_locs[abbr])

for figure in data:
    plt.figure(figsize=(12,6))
    m = Basemap(projection='cyl',
                #llcrnrlat=min(lat for (lat, lng) in locations.values()),
                #urcrnrlat=max(lat for (lat, lng) in locations.values()),
                #llcrnrlon=min(lng for (lat, lng) in locations.values()),
                #urcrnrlon=max(lng for (lat, lng) in locations.values()),
                
                llcrnrlat=24.521208,
                urcrnrlat=49.382808,
                llcrnrlon=-124.736342,
                urcrnrlon=-66.885444,
                
                resolution='c')
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()

    markers = ["o", "p", "s"]
    for option in sorted(data[figure]):
        if option == "Other":
            continue

        # jitter to prevent overlaps
        offset = len(markers) * 0.1
        
        lats = [lat + offset for (lat, lng) in data[figure][option]]
        lngs = [lng + offset for (lat, lng) in data[figure][option]]
        m.scatter(lngs, lats, zorder=5, label=option, marker=markers.pop())

    plt.legend(loc="lower right")
    plt.tight_layout()

    full_figure = {
        "star": "Star Hand Position",
        "rlt": "Right and Left Through Hands",
        "prm": "Promenade Hand Position",
    }[figure]
    
    plt.title("2008: %s" % full_figure)
    plt.savefig("dances-thesis-%s-big.png" % figure, dpi=180)
    plt.clf()
