"""Measure Fog Index for all documents and compute target value for ACUERDOS-POS."""
import textstat, json, statistics, ast as _ast

with open('../dataset_isomorfico.json', encoding='utf-8') as f:
    ds = json.load(f)

# All n=8 original document/CI artifacts
original_doc_ids = {
    'SMP-DOCUMENTAL-NEG', 'SMP-DOCUMENTAL-POS', 'SMP-CALIDAD-POS',
    'SMP-GOBERNANZA-POS', 'SMP-RESPALDO-NEG', 'SMP-RESPALDO-POS',
    'SMP-ACUERDOS-NEG', 'SMP-ACUERDOS-POS',
}
original_code_ids = {
    'SMP-CALIDAD-NEG', 'SMP-GOBERNANZA-NEG', 'SMP-GOBERNANZA-POS',
    'SMP-SEGURIDAD-NEG', 'SMP-SEGURIDAD-POS',
    'SMP-TRAZABILIDAD-NEG', 'SMP-TRAZABILIDAD-POS', 'SMP-TRAZABILIDAD-POS',
    'SMP-PRUEBAS-NEG', 'SMP-PRUEBAS-POS', 'SMP-INFRA-NEG', 'SMP-INFRA-POS',
}

print("=== FOG INDEX — n=8 original documents ===")
fogs = {}
seen = set()
for s in ds:
    sid = s['id_muestra']
    if sid in original_doc_ids and s['tipo_artefacto'] in ('documento_texto', 'pipeline_ci'):
        key = sid
        if sid == 'SMP-GOBERNANZA-POS' and s['tipo_artefacto'] == 'codigo_fuente':
            continue
        f = textstat.gunning_fog(s['contenido_texto'])
        if key not in seen:
            fogs[key] = f
            seen.add(key)
            print(f"  {sid:<28} Fog={f:.2f}")

mean8 = statistics.mean(fogs.values())
print(f"\n  n=8 MEAN: {mean8:.2f}  (target: 18.61±1.0, i.e. ≤19.61)")
print(f"  |Δμ| = |{mean8:.2f} - 18.61| = {abs(mean8-18.61):.2f}")
if abs(mean8 - 18.61) <= 1.0:
    print("  STATUS: PASSES ✓")
else:
    excess = abs(mean8 - 18.61) - 1.0
    print(f"  STATUS: FAILS ✗  (exceeds threshold by {excess:.2f} units)")
    total = sum(fogs.values())
    target_mean = 18.80
    new_acuerdos = target_mean*8 - (total - fogs.get('SMP-ACUERDOS-POS', 0))
    print(f"\n  SMP-ACUERDOS-POS target to reach mean={target_mean}: Fog={new_acuerdos:.2f}")
    print(f"  (current SMP-ACUERDOS-POS Fog = {fogs.get('SMP-ACUERDOS-POS', '?'):.2f})")

print("\n=== AST DEPTH — n=20 code files (all, incl. adversarial) ===")
depths = []
for s in ds:
    if s['tipo_artefacto'] == 'codigo_fuente':
        text = s['contenido_texto']
        try:
            tree = _ast.parse(text)
            def d(node):
                ch = list(_ast.iter_child_nodes(node))
                return 1 + max((d(c) for c in ch), default=0)
            depth = d(tree)
        except:
            depth = 0
        depths.append(depth)

mean_d = statistics.mean(depths)
print(f"  n=20 mean AST depth: {mean_d:.2f}  (D_private: 7.84)")
print(f"  |Δμ_AST| = {abs(mean_d - 7.84):.2f}")
if abs(mean_d - 7.84) <= 1.0:
    print("  STATUS: PASSES (with ε_AST=1.0) ✓")
else:
    print("  STATUS: Consider larger threshold")

print("\n=== V(G) — n=12 original code files ===")
from radon.complexity import cc_visit
vg_original = []
seen_code = set()
for s in ds:
    if s['id_muestra'] in original_code_ids and s['tipo_artefacto'] == 'codigo_fuente':
        key = s['id_muestra'] + s['archivo']
        if key in seen_code:
            continue
        seen_code.add(key)
        try:
            res = cc_visit(s['contenido_texto'])
            vg = round(sum(r.complexity for r in res)/len(res), 2) if res else 1.0
        except:
            vg = 1.0
        vg_original.append(vg)

import statistics as st
mean_vg = st.mean(vg_original)
var_vg = st.variance(vg_original) if len(vg_original) > 1 else 0
print(f"  n={len(vg_original)} mean V(G): {mean_vg:.3f}  var: {var_vg:.3f}")
print(f"  D_private: mean=1.844  var=10.468")
print(f"  |Δμ| = {abs(mean_vg-1.844):.3f}  (ε=0.5) {'✓' if abs(mean_vg-1.844)<=0.5 else '✗'}")
print(f"  |Δσ²| = {abs(var_vg-10.468):.3f}  (δ=0.25) {'✓' if abs(var_vg-10.468)<=0.25 else '✗'}")
