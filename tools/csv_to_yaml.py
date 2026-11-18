"""Convert an inputs CSV to nested YAML: vehicle -> parameter -> [quintile ->] fields.
Blank fields are omitted. Usage: csv_to_yaml.py in.csv out.yaml"""
import csv, sys, yaml

def num(s):
    try: return int(s)
    except ValueError: return float(s)

src, dst = sys.argv[1:3]
doc = {}
for r in csv.DictReader(open(src)):
    d = {"value": num(r["value"]) if r["value"] != "" else None}
    for k in ["units", "source", "year", "decision", "note"]:
        if r[k] != "": d[k] = int(r[k]) if k == "year" else r[k]
    node = doc.setdefault(r["vehicle"], {}).setdefault(r["parameter"], {})
    q = r["wealth_quintile"]
    if q == "": node.update(d)
    else: node["total" if q == "total" else f"q{q}"] = d

with open(dst, "w") as f:
    f.write(f"# Same content as {src.split('/')[-1]}. Blank fields are omitted.\n")
    for v, params in doc.items():
        f.write(f"\n{v}:\n")
        for line in yaml.safe_dump(params, sort_keys=False, width=1000).splitlines():
            f.write(f"  {line}\n")
