"""Write the starting input files for the demo. Run once."""
import csv, yaml, pathlib
COLS = "vehicle,parameter,scenario,wealth_quintile,sex,value,units,source,year,decision,note".split(",")
root = pathlib.Path(__file__).parent.parent / "inputs"

def write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(COLS)
        for r in rows: w.writerow([r.get(c, "") for c in COLS])

# ---- nigeria/vehicle.csv
V = []
shares = {"wheat": [.282,.191,.236,.274,.318,.391], "maize": [.412,.498,.455,.421,.377,.309],
          "salt": [.981,.972,.979,.983,.985,.986], "bouillon": [.953,.931,.948,.957,.962,.967]}
means = {"wheat": [16.1,21.4,26.0,31.2,40.3], "maize": [88.2,79.5,71.3,60.8,44.9],
         "salt": [6.9,7.1,7.2,7.4,7.5], "bouillon": [2.1,2.3,2.4,2.6,2.7]}
sds = {"wheat": [13.26,15.9,18.4,21.7,27.5], "maize": [51.3,47.0,43.8,39.1,31.6],
       "salt": [2.4,2.4,2.5,2.6,2.6], "bouillon": [1.1,1.2,1.2,1.3,1.4]}
gf = {"wheat": (1, .63, .85, 9), "maize": (.31, .38, .70, 10), "salt": (.92, .81, .95, 11), "bouillon": (.88, .12, .60, 12)}
for v in shares:
    for q, s in zip(["total",1,2,3,4,5], shares[v]):
        V.append(dict(vehicle=v, parameter="consumption_share", wealth_quintile=q, value=s, units="proportion",
                      source="NFCMS, Table 146, p 191", year=2021, note=f"Share of WRA who eat {v}" if q=="total" else ""))
    for q, m, s in zip(range(1,6), means[v], sds[v]):
        V.append(dict(vehicle=v, parameter="consumption_mean", wealth_quintile=q, value=m, units="g/day",
                      source="NFCMS, Table 147, p 193", year=2021, note="Per capita over all WRA" if q==1 else ""))
        if v == "wheat":
            V.append(dict(vehicle=v, parameter="consumption_sd", wealth_quintile=q, units="g/day", source="computed:consumer_cv",
                          decision="D007", note="Survey SD is too small for the zero-inflated model" if q==1 else ""))
            V.append(dict(vehicle=v, parameter="survey_consumption_sd", wealth_quintile=q, value=s, units="g/day",
                          source="NFCMS, Table 147, p 193", year=2021))
        else:
            V.append(dict(vehicle=v, parameter="consumption_sd", wealth_quintile=q, value=s, units="g/day",
                          source="NFCMS, Table 147, p 193", year=2021))
    cons, cur, tgt, row = gf[v]
    V.append(dict(vehicle=v, parameter="current_consolidation", value=cons, units="proportion", source=f"GF background data, Burden x Vehicle Matrix O{row}", year=2026))
    V.append(dict(vehicle=v, parameter="current_compliance", value=cur, units="proportion", source=f"GF background data, Burden x Vehicle Matrix R{row}", year=2026))
    V.append(dict(vehicle=v, parameter="target_compliance", value=tgt, units="proportion", source=f"GF background data, Coverage Over Time M{row-1}", year=2026))
write(root/"nigeria/vehicle.csv", V)

# ---- nigeria/folate.csv
F = []
conc = {"wheat": 2.6, "maize": 2.6, "salt": 0, "bouillon": 80}
for v in conc:
    if v == "wheat":
        F.append(dict(vehicle=v, parameter="baseline_share_fortified", value=0, units="proportion", source="Assumption", decision="P001", note="No folic acid in Nigeria wheat flour today"))
        F.append(dict(vehicle=v, parameter="baseline_effectiveness", value=0, units="proportion", source="NFCMS, Figure 71", year=2021))
        F.append(dict(vehicle=v, parameter="baseline_concentration", value=2.6, units="mcg/g", source="TechnoServe"))
    else:
        F.append(dict(vehicle=v, parameter="baseline_share_fortified", units="proportion", source="computed:gf_baseline_share"))
        F.append(dict(vehicle=v, parameter="baseline_effectiveness", units="proportion", source="computed:gf_effectiveness"))
        F.append(dict(vehicle=v, parameter="baseline_concentration", value=conc[v], units="mcg/g", source="TechnoServe 2019, Table 2", year=2019))
    F.append(dict(vehicle=v, parameter="intervention_coverage", scenario="intervention", units="proportion", source="computed:gf_target"))
    F.append(dict(vehicle=v, parameter="intervention_effectiveness", scenario="intervention", units="proportion", source="computed:gf_target"))
    F.append(dict(vehicle=v, parameter="intervention_concentration", scenario="intervention", value=conc[v] or 40, units="mcg/g", source="TechnoServe 2019, Table 2", year=2019))
write(root/"nigeria/folate.csv", F)

# ---- nigeria/folate.yaml : same content, nested vehicle -> parameter, blank fields omitted
doc = {}
for r in F:
    d = {k: r[k] for k in ["value","units","source","year","decision","note"] if r.get(k, "") != ""}
    if "value" not in d: d = {"value": None, **d}
    doc.setdefault(r["vehicle"], {})[r["parameter"]] = d
with open(root/"nigeria/folate.yaml", "w") as f:
    f.write("# Same content as folate.csv. Scenario is implied by the intervention_ prefix.\n")
    for v, params in doc.items():
        f.write(f"\n{v}:\n")
        for p, d in params.items():
            f.write(f"  {p}:\n")
            for line in yaml.safe_dump(d, sort_keys=False, width=1000).splitlines():
                f.write(f"    {line}\n")

with open(root/"decisions.csv", "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow("decision_id,status,title,rationale,decided_by,date".split(","))
    w.writerow(["D007","active","Consumer CV for Nigeria wheat SD","NFCMS usual-intake SDs are incompatible with the zero-inflated model at 19-35% coverage; give consumers the NFCMS CV","Nathaniel","2026-10-02"])
    w.writerow(["P001","active","No baseline folic acid in Nigeria wheat","Wheat flour standard does not require folic acid; treat baseline share as zero","Nathaniel","2026-09-18"])
