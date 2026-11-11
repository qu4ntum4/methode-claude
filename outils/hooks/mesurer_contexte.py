# -*- coding: utf-8 -*-
"""
Mesure la taille du contexte envoyé à chaque échange, à partir des journaux de session de
Claude Code. Sert à vérifier que la méthode « une tâche = une session » tient ses promesses.

    python mesurer_contexte.py <fragment du nom de projet> [--depuis AAAA-MM-JJ]
    python mesurer_contexte.py mdr-schedule --depuis 2026-10-05

Référence du 04/10/2026, avant la méthode : contexte médian 515 000 jetons (horaires) et
531 000 (Home Assistant) ; 76 % des échanges au-delà de 300 000 ; 98 % des jetons en relecture (relecture du cache rapportée au total lu, écrit et produit).
"""
import glob
import json
import os
import statistics
import sys

racine = os.path.expanduser("~/.claude/projects")
fragment = sys.argv[1] if len(sys.argv) > 1 else ""
depuis = sys.argv[sys.argv.index("--depuis") + 1] if "--depuis" in sys.argv else ""

for dossier in sorted(glob.glob(os.path.join(racine, "*%s*" % fragment))):
    tailles, lu, ecrit, produit, sessions = [], 0, 0, 0, 0
    for f in glob.glob(os.path.join(dossier, "*.jsonl")):
        compte = 0
        with open(f, encoding="utf-8", errors="replace") as fh:
            for ligne in fh:
                try:
                    d = json.loads(ligne)
                except ValueError:
                    continue
                if depuis and d.get("timestamp", "") < depuis:
                    continue
                m = d.get("message")
                if not isinstance(m, dict) or m.get("role") != "assistant":
                    continue
                u = m.get("usage") or {}
                c = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                if c:
                    tailles.append(c)
                    lu += u.get("cache_read_input_tokens", 0)
                    ecrit += u.get("cache_creation_input_tokens", 0)
                    produit += u.get("output_tokens", 0)
                    compte += 1
        sessions += 1 if compte else 0
    if not tailles:
        continue
    print(os.path.basename(dossier))
    print("  sessions %d, échanges %d" % (sessions, len(tailles)))
    print("  contexte médian %d, p90 %d, max %d" % (statistics.median(tailles),
          sorted(tailles)[int(len(tailles) * 0.9)], max(tailles)))
    print("  au-delà de 300 000 : %d %%" % (100 * sum(t > 300000 for t in tailles) // len(tailles)))
    total = lu + ecrit + produit
    print("  part relue en cache : %.1f %%" % (100.0 * lu / total if total else 0))
