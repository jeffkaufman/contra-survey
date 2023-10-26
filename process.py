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

try:
    with open("sheet-raw.tsv") as inf:
        cols = None
        for line in inf:
            bits = line.rstrip("\n").split("\t")
            if not cols:
                cols = bits
                continue

            raw_loc = bits[cols.index("Where is your home dance?")]
            if raw_loc in ["M", "(currently none)"]:
                continue

            if raw_loc == "Greenfield":
                raw_loc = "Greenfield, MA"
            elif raw_loc in ["BIDA", "BIDA, MA"]:
                raw_loc = "Cambridge, MA"
            elif raw_loc == "Boston GLBTQ contra":
                raw_loc = "Jamaica Plain Boston MA"

            pos = lookup_ll(raw_loc)

            prm = bits[cols.index(
                "At your home dance, what's the main "
                "hand position for a promenade?")]
            rlt = bits[cols.index(
                "At your home dance, what's the main way "
                "people start a right and left through?")]
            star = bits[cols.index(
                "At your home dance, what's the main hand "
                "position for a star?")]
            ct = bits[cols.index(
                "On a courtesy turn, do people at your home dance twirl?")]
            pt = bits[cols.index(
                "After a Petronella twirl, do people "
                "at your home dance clap?")]
            fn = bits[cols.index(
                "When balancing or going forward in long lines, "
                "do people at your home dance make noise with their feet?")]

            if prm in [
                    "Robin's hand at hip, Lark's arm behind.",

                    "At my home dance, it’s the courtesy turn but I do "
                    "skaters bc that’s how I grew up dancing.",

                    "Greenfield is courtesy turn and Indianapolis was skaters",
            ]:
                prm = "Courtesy turn: Robin/Lady's right hand behind the back"

            if prm == "Courtesy turn: Robin/Lady's right hand behind the back":
                prm = "Courtesy"
            elif prm == "Butterfly: Robin/Lady's right hand on the shoulder":
                prm = "Butterfly"
            elif prm == "Skater's: both hands in front of the dancers":
                prm = "Skaters"
            else:
                prm = "Other"

            data["prm"][prm].append(pos)

            if rlt == "Pass through across the set":
                rlt = "No hands"
            elif rlt == "With your right hand, pull by across the set":
                rlt = "Hands"
            else:
                rlt = "Other"

            data["rlt"][rlt].append(pos)
                
            if star in [
                    "Greenfield, hold the wrist. Louisville, hold "
                    "hands across.",

                    "if not told, hold the wrist of the person in front "
                    "of you",

                    "I've experienced mostly wrist position stars but "
                    "some dances call for hands across for a specific reason.",

                    "My dances it was wrist grip. In KY and South it was "
                    "hands across",

                    "Usually holding the wrist, except for a few dances "
                    "where the caller will specify it's better to hold "
                    "hands with the person across",
            ]:
                star = "Hold the wrist of the person in front of you"
            elif star in [
                    "Hands across (but I prefer the wrist Star)"
            ]:
                star = "Hold hands with the person across from you"
            elif star in [
                    "Panicked indecision",
            ]:
                star = "Put them in the center and don't worry about it"

            if star == "Hold the wrist of the person in front of you":
                star = "Wrist"
            elif star == "Hold hands with the person across from you":
                star = "Hands Across"
            elif star == "Put them in the center and don't worry about it":
                star = "Center"
            else:
                star = "Other"

            data["star"][star].append(pos)
                
            if ct in [
                    "About 50/50 - strong focus on consent",
                    "More experienced dancers do about half the time or more",
                    "Some dancers always do some dancers never ",
                    "depends on the person I'm dancing with. I prefer twirling",
                    "Highly variable ",
                    "It's personal choice - perhaps a third twirl",
                    "Some of the more experienced dancers used to almost "
                    "always twirl reguardless of the appropriateness.  We "
                    "have introduced backspins, which has lead to most folks "
                    "being more intentional about which courtesy turn to chose.",
            ]:
                ct = "Often"
            elif ct in [
                    "Maybe ¼-½ the time?",

                    "Competent Larks may offer a twirl and Robins can decide "
                    "whether to twirl or not ",

                    "Dependant upon the dancer and their range of mobility.",

                    "More often with people who know each other; Rarely "
                    "if not.",

                    "Only with people who show a willingness to be twirled ",

                    "Optionally. Either the raises the arm to invite or "
                    "the Robin pushes up to indicate they’d like one. It’s "
                    "certainly not required ",

                    "Sometimes",

                    "Sometimes courtesy turn and sometimes twirl",

                    "Sometimes, more often younger dancers.",

                    "Somewhere between \"often\" and \"rarely.\" We're "
                    "pretty attuned to beginners, and we have a lot of them, "
                    "so twirls mostly happen between more experienced "
                    "dancers.",

                    "Those who dance in Richmond also twirl, those who "
                    "only dance locally don't",

                    "When invited as a flourish, sometimes, which is not "
                    "an option not provided here in between often and rarely.",

                    "depends on the dance, but somewhere between rarely and "
                    "often",

                    "sometimes",
            ]:
                ct = "Rarely"

            if ct not in [
                    "Never, or almost never",
                    "Always, or almost always",
                    "Rarely",
                    "Often",
            ]:
                ct = "Other"

            data["ct"][ct].append(pos)

            if pt not in [
                    "Never, or almost never",
                    "Always, or almost always",
                    "Rarely",
                    "Often",
            ]:
                pt = "Other"
                
            data["pt"][pt].append(pos)

            if fn in [
                    "A select few always do, most do not (knees)",

                    "Certain people do all the time, most people don't",

                    "No, because the floor doesn't really make noise. I "
                    "would if I could.",

                    "Not a lot.  Not like St. Louis or Sautee Nacoochee "

                    "where it is clear and in sync",

                    "Not since the hall requested that we didn't",

                    "Occasionally stompy but little embellishment; hard to "
                    "tell if it's intentional, the skill level these days / "
                    "beginner influx means that long lines are seldom "
                    "together/on the beat, sigh",

                    "Only about 3 dancers do",

                    "We make a little noise but nothing like I've seen in "
                    "videos of New England dances.",

                    "Sometimes",
            ]:
                fn = "Rarely"
            elif fn in [
                    "Long lines almost always, balancing rarely",
                    "Often for long lines (on 4); rarely for balance. ",
                    "Rehoboth MA dance: often. Ithaca NY dance: rarely",
            ]:
                fn = "Often"
            elif fn in [
                    "always, except at folklife where the dance floor is "
                    "built of sound absorbing boards..",
            ]:
                fn = "Always, or almost always"


            if fn not in [
                    "Never, or almost never",
                    "Always, or almost always",
                    "Rarely",
                    "Often",
            ]:
                fn = "Other"

            data["fn"][fn].append(pos)
                
finally:
    with open("locations.json", "w") as outf:
        json.dump(locations, outf)

for figure in data:
    if figure not in ["star", "rlt", "prm"]:
        continue
    
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
    
    plt.title("2023: %s" % full_figure)
    plt.savefig("dances-%s-big.png" % figure, dpi=180)
    plt.clf()
