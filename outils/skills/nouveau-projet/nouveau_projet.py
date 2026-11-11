# -*- coding: utf-8 -*-
"""
Pose les fichiers de la méthode dans un dossier de projet, sans rien écraser.

    python nouveau_projet.py <dossier>

Copie, là où rien n'existe : CLAUDE.md, ETAT.md, TODO.md, docs/decisions.md, docs/pieges.md,
docs/chantiers/GABARIT.md ; crée docs/archives/ ; `git init` s'il n'y a pas de dépôt ; un
.gitignore de départ s'il n'y en a pas. Les gabarits viennent du dossier `gabarits/` à côté de
ce script. Écrit le 18/10/2026.
"""
import os
import shutil
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
GABARITS = os.path.join(ICI, "gabarits")
FICHIERS = {
    "CLAUDE.md": "CLAUDE.md",
    "ETAT.md": "ETAT.md",
    "TODO.md": "TODO.md",
    "decisions.md": os.path.join("docs", "decisions.md"),
    "pieges.md": os.path.join("docs", "pieges.md"),
    "chantier.md": os.path.join("docs", "chantiers", "GABARIT.md"),
    "divers.md": os.path.join("docs", "chantiers", "divers.md"),
}
GITIGNORE = """# Secrets et identifiants — jamais versionnés
.env
*.key
*.pem
secrets.*

# Données personnelles ou volumineuses — à compléter selon le projet
donnees/
*.sqlite
*.db

# Produit par les outils
__pycache__/
*.pyc
node_modules/
.cache/
"""


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage : python nouveau_projet.py <dossier>")
    projet = os.path.abspath(sys.argv[1])
    os.makedirs(projet, exist_ok=True)
    faits, laisses = [], []
    for source, dest in FICHIERS.items():
        cible = os.path.join(projet, dest)
        if os.path.exists(cible):
            laisses.append(dest)
            continue
        os.makedirs(os.path.dirname(cible) or projet, exist_ok=True)
        shutil.copyfile(os.path.join(GABARITS, source), cible)
        faits.append(dest)
    os.makedirs(os.path.join(projet, "docs", "archives"), exist_ok=True)
    if not os.path.isdir(os.path.join(projet, ".git")):
        r = subprocess.run(["git", "init", "-q", "-b", "main", projet], capture_output=True, text=True)
        faits.append(".git (dépôt initialisé)" if r.returncode == 0 else ".git : échec — " + r.stderr.strip())
    gi = os.path.join(projet, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w", encoding="utf-8", newline="\n") as f:
            f.write(GITIGNORE)
        faits.append(".gitignore (de départ, à compléter)")
    print("Projet : " + projet)
    print("Posés   : " + (", ".join(faits) or "rien"))
    if laisses:
        print("Laissés : " + ", ".join(laisses) + " (existaient déjà)")
    print("Suite : remplacer les « guillemets » des gabarits, puis premier commit.")


if __name__ == "__main__":
    main()
