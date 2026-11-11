# -*- coding: utf-8 -*-
"""
Tient le sommaire des chantiers de TODO.md : les comptes de tâches ouvertes, l'ordre par
priorité, et les chantiers qui dorment.

    python chantiers.py [dossier du projet]            rapport, rien n'est écrit
    python chantiers.py [dossier du projet] --ecrire   met à jour TODO.md

Le sommaire est la table de TODO.md dont chaque ligne est, avec ou sans colonne de priorité :
    | [`nom.md`](docs/chantiers/nom.md) | <P> | <ouvertes> | <description> |
    | [`nom.md`](docs/chantiers/nom.md) | <ouvertes> | <description> |
Le script ne touche qu'à la colonne des comptes, à l'ordre des lignes (par P quand toutes en ont
une) et au suffixe « · dort depuis le JJ/MM » de la description. Il compte aussi les marques
[P1] en tête de tâche. Il ne crée ni n'archive rien : un chantier à zéro ou absent du sommaire
est signalé, et c'est le point d'étape qui décide. Écrit le 18/10/2026, priorités le 03/11/2026.
"""
import datetime as dt
import os
import re
import subprocess
import sys

JOURS_AVANT_SOMMEIL = 30
CASE_OUVERTE = re.compile(r"^\s*- \[ \]", re.M)
MARQUE_P1 = re.compile(r"^\s*- \[ \]\s*\[P1\]", re.M)
LIEN = re.compile(r"^\[`([^`]+)`\]\(docs/chantiers/[^)]+\)$")
SUFFIXE = re.compile(r"\s*·\s*dort depuis le \d\d/\d\d(/\d{4})?\s*$")


def dernier_mouvement(projet, chemin):
    try:
        r = subprocess.run(["git", "-C", projet, "log", "-1", "--format=%cs", "--", chemin],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return dt.date.fromisoformat(r.stdout.strip())
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return dt.date.fromtimestamp(os.path.getmtime(os.path.join(projet, chemin)))


def lire_ligne(l):
    """-> (nom, priorite ou None, compte, description) si c'est une ligne de chantier, sinon None."""
    if not l.startswith("|"):
        return None
    cellules = [c.strip() for c in l.strip().strip("|").split("|")]
    if len(cellules) not in (3, 4):
        return None
    m = LIEN.match(cellules[0])
    if not m:
        return None
    if len(cellules) == 4:
        p, compte, desc = cellules[1], cellules[2], cellules[3]
        if not p.isdigit() or not compte.isdigit():
            return None
        return m.group(1), int(p), int(compte), desc
    if not cellules[1].isdigit():
        return None
    return m.group(1), None, int(cellules[1]), cellules[2]


def ecrire_ligne(nom, p, compte, desc):
    cellules = ["[`%s`](docs/chantiers/%s)" % (nom, nom)] + ([str(p)] if p is not None else []) + [str(compte), desc]
    return "| " + " | ".join(cellules) + " |"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    projet = os.path.abspath(args[0] if args else os.getcwd())
    ecrire = "--ecrire" in sys.argv
    dossier = os.path.join(projet, "docs", "chantiers")
    todo = os.path.join(projet, "TODO.md")
    if not os.path.isdir(dossier) or not os.path.isfile(todo):
        print("Pas de docs/chantiers/ ou de TODO.md ici : rien à faire.")
        return

    aujourdhui = dt.date.today()
    chantiers = {}
    for nom in sorted(os.listdir(dossier)):
        if not nom.endswith(".md") or nom.upper().startswith("GABARIT"):
            continue
        rel = "docs/chantiers/" + nom
        with open(os.path.join(dossier, nom), encoding="utf-8", errors="replace") as f:
            texte = f.read()
        ouvertes, urgentes = len(CASE_OUVERTE.findall(texte)), len(MARQUE_P1.findall(texte))
        depuis = dernier_mouvement(projet, rel)
        dort = ouvertes > 0 and (aujourdhui - depuis).days >= JOURS_AVANT_SOMMEIL
        chantiers[nom] = (ouvertes, urgentes, depuis, dort)

    with open(todo, encoding="utf-8") as f:
        lignes = f.read().split("\n")

    # Les lignes de chantier, et le bloc contigu qu'elles forment (pour le tri)
    rangs = [(i, lire_ligne(l)) for i, l in enumerate(lignes)]
    rangs = [(i, r) for i, r in rangs if r]
    vus, changements, nouvelles = set(), [], {}
    for i, (nom, p, compte, desc) in rangs:
        vus.add(nom)
        if nom not in chantiers:
            changements.append("%s : dans le sommaire, mais le fichier n'existe pas" % nom)
            nouvelles[i] = lignes[i]
            continue
        ouvertes, urgentes, depuis, dort = chantiers[nom]
        desc_propre = SUFFIXE.sub("", desc)
        nouvelle_desc = desc_propre + (" · dort depuis le %s" % depuis.strftime("%d/%m") if dort else "")
        if compte != ouvertes:
            changements.append("%s : %d → %d ouvertes" % (nom, compte, ouvertes))
        if dort and not SUFFIXE.search(desc):
            changements.append("%s : dort depuis le %s" % (nom, depuis.strftime("%d/%m")))
        if not dort and SUFFIXE.search(desc):
            changements.append("%s : s'est réveillé" % nom)
        nouvelles[i] = ecrire_ligne(nom, p, ouvertes, nouvelle_desc)

    # Tri par priorité : seulement si le bloc est contigu et que toutes les lignes ont un P
    indices = sorted(nouvelles)
    if indices and indices == list(range(indices[0], indices[-1] + 1)) and all(r[1] is not None for _, r in rangs):
        ordre = sorted(rangs, key=lambda x: (x[1][1], x[1][0]))
        reordonnees = [nouvelles[i] for i, _ in ordre]
        if reordonnees != [nouvelles[i] for i in indices]:
            changements.append("sommaire réordonné par priorité")
        for i, l in zip(indices, reordonnees):
            lignes[i] = l
    else:
        for i, l in nouvelles.items():
            lignes[i] = l
    sans_p = [r[0] for _, r in rangs if r[1] is None]
    if sans_p and len(sans_p) == len(rangs):
        changements.append("le sommaire n'a pas de colonne P : à ajouter au point d'étape (priorités à demander)")

    for nom, (ouvertes, urgentes, depuis, dort) in chantiers.items():
        if nom not in vus:
            changements.append("%s : %d ouvertes, ABSENT du sommaire" % (nom, ouvertes))
        if ouvertes == 0:
            changements.append("%s : zéro tâche ouverte — à archiver (git mv docs/chantiers/%s docs/archives/)" % (nom, nom))
    urgentes = {n: c[1] for n, c in chantiers.items() if c[1]}
    if urgentes:
        print("Tâches [P1] ouvertes : " + ", ".join("%s %d" % (n, c) for n, c in urgentes.items()))

    if not changements:
        print("Sommaire à jour : %d chantiers, %d tâches ouvertes." % (len(chantiers), sum(c[0] for c in chantiers.values())))
        return
    print("\n".join(changements))
    if ecrire:
        with open(todo, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lignes))
        print("TODO.md mis à jour (comptes, ordre, sommeil ; l'archivage et la colonne P restent à faire à la main).")
    else:
        print("Rien n'est écrit : relancer avec --ecrire.")


if __name__ == "__main__":
    main()
