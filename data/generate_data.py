import csv, random

high = [
    "there is a fire in the building", "major accident on highway", "person collapsed on street",
    "electric wire fallen on road", "robbery at my house", "flood in our area", "gas leak in apartment",
    "building collapsed near school", "dengue outbreak in locality", "someone being attacked",
    "transformer exploded near houses", "child missing in our area", "sewage burst on main road",
    "tree fell on person", "electrocution accident near pole", "mob violence in street",
    "water contamination making people sick", "serious injury in road accident", "fire in market",
    "emergency no water for 3 days in summer", "dead animal near water supply", "live wire on footpath",
    "hospital refusing emergency patient", "chemical smell from drain", "manhole open on busy road"
]

medium = [
    "streetlight not working", "garbage not collected for 3 days", "pothole on main road",
    "water supply irregular", "drainage overflow near houses", "broken footpath", "mosquito breeding",
    "public toilet not clean", "water leakage from pipe", "electricity fluctuation",
    "road needs repair near school", "dustbin overflowing in market", "bus stop broken",
    "sewer line blocked", "no street light in lane", "water pressure low in morning",
    "stray dogs near school", "illegal parking blocking road", "foul smell from drain",
    "broken playground equipment", "road marking faded", "public tap not working",
    "construction debris on road", "encroachment on footpath", "noise from factory at night"
]

low = [
    "please paint the park benches", "suggestion to add more dustbins", "name board faded",
    "minor crack on footpath", "request to plant more trees", "feedback about park cleanliness",
    "small pothole near corner", "suggestion for better lighting", "request for area beautification",
    "minor water pressure issue", "request for speed breaker", "old bench in park needs repair",
    "suggestion to add CCTV", "request for zebra crossing paint", "feedback on road cleanliness",
    "request to trim overgrown trees", "suggestion for more bus stops", "minor drain blockage",
    "request for pedestrian path", "suggestion to improve park"
]

rows = []
for _ in range(180):
    rows.append([random.choice(high), "High"])
for _ in range(180):
    rows.append([random.choice(medium), "Medium"])
for _ in range(140):
    rows.append([random.choice(low), "Low"])

random.shuffle(rows)

with open("data/priority_master.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["text", "priority"])
    writer.writerows(rows)

print(f"Generated {len(rows)} rows!")
