import io, os

# ---- A. gate: band expectations -> three-rule span; label rename; T55 wiring ----
gp = '../scripts/verify_paper_numbers_l8.py'
g = io.open(gp, encoding='utf-8').read()

old_label = '("library caliber", r"library[-\\s]?caliber'
new_label = '("library convention", r"library[-\\s]?(?:convention|caliber)'
assert g.count(old_label) == 1, ('label', g.count(old_label))
g = g.replace(old_label, new_label)

# add span keys to t54_expectations (after cf loading block)
anchor_cf = '        exp[("cf_rate", fam)] = cf[fam]["violation_rate_median"]'
assert g.count(anchor_cf) == 1
g = g.replace(anchor_cf, anchor_cf + '''
    repagg = _load(V5 / "counterfactual_fd" / "counterfactual_repairs_agg.json")
    _meds = [repagg[f]["median_gap_pp"][r] for f in ("R2F", "R3H")
             for r in ("drop_later", "priority_aware", "retime")]
    exp["cf_gap_span_lo"] = round(min(_meds))
    exp["cf_gap_span_hi"] = round(max(_meds))''')

# both band handlers -> span keys
old_band = '''                   (int(m.group(1)), round(e[("cf_gap", "R3H")]), 0.5, "cf gap band lo"),
                   (int(m.group(2)), round(e[("cf_gap", "R2F")]), 0.5, "cf gap band hi")]),'''
assert g.count(old_band) == 2
g = g.replace(old_band, '''                   (int(m.group(1)), e["cf_gap_span_lo"], 0.5, "cf gap band lo"),
                   (int(m.group(2)), e["cf_gap_span_hi"], 0.5, "cf gap band hi")]),''')

# T55 wiring
old_wire = """        f54, p54, seen54 = check_t54(text, p.name, t54)
        fails += f54
        passes += p54
        seen += seen54"""
assert g.count(old_wire) == 1
g = g.replace(old_wire, old_wire + """
        from verify_t55_group import check_t55, t55_expectations as _t55_exp
        t55 = _t55_exp()
        f55, p55, seen55 = check_t55(text, p.name, t55)
        fails += f55
        passes += p55
        seen += seen55""")

old_print = 'f"({seen54} T54), "'
assert g.count(old_print) == 1
g = g.replace(old_print, 'f"({seen54} T54, {seen55} T55), "')

io.open(gp + '.new', 'w', encoding='utf-8', newline=chr(10)).write(g)
os.replace(gp + '.new', gp)
print('gate patched: span keys + label + wiring')

# ---- B. manuscript: conclusion span + 90-units wording ----
mp = 'main.tex'
s = io.open(mp, encoding='utf-8').read()

old_concl = ("The fixed-dwell counterfactual quantifies what the endogenous dwell buys: "
             "planned with the library dwell, the dense families violate the transfer "
             "constraint in 20--29\\% of consecutive pairs and land 18--30 percentage "
             "points short.")
new_concl = ("The fixed-dwell counterfactual quantifies what the endogenous dwell buys: "
             "planned with the library dwell, the dense families violate the transfer "
             "constraint in 20--29\\% of consecutive pairs and, after repair, land 7--30 "
             "points short, the span depending on the repair rule "
             "(Section~\\ref{sec:counterfactual}).")
assert s.count(old_concl) == 1, ('concl', s.count(old_concl))
s = s.replace(old_concl, new_concl)

old_90 = ("The registered-policy arm reproduces the "
          "stored sweep anchors exactly on all 90 units, so the comparison is anchored.")
new_90 = ("The registered-policy arm reproduces the "
          "stored sweep anchors exactly on all 90 replayed units, so the comparison is "
          "anchored.")
assert s.count(old_90) == 1, ('u90', s.count(old_90))
s = s.replace(old_90, new_90)

io.open(mp + '.new', 'w', encoding='utf-8', newline=chr(10)).write(s)
os.replace(mp + '.new', mp)
print('manuscript patched: conclusion span + 90-units wording')
