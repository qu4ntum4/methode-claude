# -*- coding: utf-8 -*-
"""
Publie la part partageable de la méthode dans son dépôt public. Ce dossier est la SOURCE ; le
dépôt public ne s'édite jamais à la main, il est réécrit à chaque publication.

    python publier.py                 assemble, compare au clone du dépôt public, commit et push s'il y a du neuf
    python publier.py --verifier      assemble et dit ce qui changerait, sans toucher au réseau ; code de sortie 1
                                      si quelque chose de personnel traîne dans la part partageable
    python publier.py --clone <dossier>   où vit le clone (défaut : un dossier methode-claude à côté de ce projet)

Ce qui part : METHODE.md ; gabarits/ ; outils/ sans hooks/signaler_sessions.py (le capteur des
sessions, propre à une maison), sans __pycache__ et sans outils/public/ ; et outils/public/README.md,
le texte d'accueil du dépôt public, posé à sa racine. Ce qui ne part jamais : ETAT.md, TODO.md, le
CLAUDE.md du projet, docs/ et bilans/ — ils parlent de vrais projets et de vraies personnes.

Garde-fou : la part assemblée ne doit contenir aucun des mots de outils/public/mots-interdits.txt
(une expression régulière par ligne, insensible à la casse) ; sinon rien n'est publié. Cette liste
est le seul endroit de la règle « METHODE.md, gabarits/ et outils/ restent anonymes ».

Relancé sans changement, ne commite ni ne pousse rien. Écrit le 11/11/2026 (registre, même date).
"""
import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
PUBLIC = os.path.join(ICI, "public")
DEPOT = "https://github.com/qu4ntum4/methode-claude.git"
BRANCHE = "main"
CLONE_DEFAUT = os.path.join(os.path.dirname(RACINE), "methode-claude")
# L'auteur des commits du dépôt public : le compte GitHub, avec son adresse de relais, pour qu'aucune
# adresse personnelle ne parte dans l'historique public (choix de l'agent, 11/11/2026, à revoir).
AUTEUR = ("qu4ntum4", "55092429+qu4ntum4@users.noreply.github.com")
EXCLUS_OUTILS = {"signaler_sessions.py"}
GITIGNORE = "__pycache__/\n*.pyc\n"


def git(*args, cwd, entree=None):
    r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", input=entree)
    if r.returncode != 0:
        sys.exit("git %s a échoué dans %s :\n%s" % (" ".join(args), cwd, (r.stderr or r.stdout).strip()))
    return r.stdout


def copier_arbre(source, cible, exclure_fichiers=(), exclure_dossiers=()):
    for racine, dossiers, noms in os.walk(source):
        dossiers[:] = [d for d in dossiers if d != "__pycache__" and d not in exclure_dossiers]
        for n in noms:
            if n.endswith(".pyc") or n in exclure_fichiers:
                continue
            p = os.path.join(racine, n)
            dest = os.path.join(cible, os.path.relpath(p, source))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(p, dest)


def assembler(travail):
    """Pose dans `travail` exactement ce qui part."""
    shutil.copyfile(os.path.join(RACINE, "METHODE.md"), os.path.join(travail, "METHODE.md"))
    copier_arbre(os.path.join(RACINE, "gabarits"), os.path.join(travail, "gabarits"))
    copier_arbre(ICI, os.path.join(travail, "outils"), exclure_fichiers=EXCLUS_OUTILS,
                 exclure_dossiers={"public"})
    shutil.copyfile(os.path.join(PUBLIC, "README.md"), os.path.join(travail, "README.md"))
    with open(os.path.join(travail, ".gitignore"), "w", encoding="utf-8", newline="\n") as f:
        f.write(GITIGNORE)


def mots_interdits():
    lignes = open(os.path.join(PUBLIC, "mots-interdits.txt"), encoding="utf-8").read().splitlines()
    motifs = [l.strip() for l in lignes if l.strip() and not l.startswith("#")]
    return re.compile("|".join("(?:%s)" % m for m in motifs), re.I)


def controler(travail):
    """Les lignes de la part assemblée qui portent un mot interdit : [(fichier, n° de ligne, extrait)]."""
    motif = mots_interdits()
    trouves = []
    for racine, _, noms in os.walk(travail):
        for n in noms:
            p = os.path.join(racine, n)
            try:
                texte = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            for i, ligne in enumerate(texte.splitlines(), 1):
                if motif.search(ligne):
                    trouves.append((os.path.relpath(p, travail).replace("\\", "/"), i, ligne.strip()[:90]))
    return trouves


def preparer_clone(clone):
    """Le clone au niveau du dépôt public, sur la branche de publication ; vide si le dépôt l'est."""
    if not os.path.isdir(os.path.join(clone, ".git")):
        os.makedirs(os.path.dirname(clone) or ".", exist_ok=True)
        git("clone", "-q", DEPOT, clone, cwd=os.path.dirname(clone) or ".")
    else:
        git("fetch", "-q", "origin", cwd=clone)
    git("config", "user.name", AUTEUR[0], cwd=clone)
    git("config", "user.email", AUTEUR[1], cwd=clone)
    distant = subprocess.run(["git", "rev-parse", "--verify", "-q", "origin/" + BRANCHE],
                             cwd=clone, capture_output=True, text=True).returncode == 0
    if distant:
        git("checkout", "-q", "-B", BRANCHE, "origin/" + BRANCHE, cwd=clone)
    else:
        git("symbolic-ref", "HEAD", "refs/heads/" + BRANCHE, cwd=clone)


def synchroniser(travail, clone):
    """Remplace le contenu du clone par la part assemblée ; rend ce que git y voit de changé."""
    for n in os.listdir(clone):
        if n == ".git":
            continue
        p = os.path.join(clone, n)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    copier_arbre(travail, clone)
    git("add", "-A", cwd=clone)
    return git("status", "--porcelain", cwd=clone).strip()


def main():
    verifier = "--verifier" in sys.argv
    clone = CLONE_DEFAUT
    if "--clone" in sys.argv:
        clone = os.path.abspath(sys.argv[sys.argv.index("--clone") + 1])
    if not os.path.isdir(PUBLIC):
        sys.exit("Pas de dossier outils/public/ : ce dossier n'est pas la source de la méthode, rien à publier.")
    travail = tempfile.mkdtemp(prefix="methode-claude-")
    try:
        assembler(travail)
        nb = sum(len(n) for _, _, n in os.walk(travail))
        trouves = controler(travail)
        if trouves:
            print("Rien n'est publié : la part partageable porte quelque chose de personnel.")
            for f, i, l in trouves:
                print("  %s:%d: %s" % (f, i, l))
            sys.exit(1)
        print("Part partageable : %d fichiers, rien de personnel." % nb)
        if verifier and not os.path.isdir(os.path.join(clone, ".git")):
            print("Pas encore de clone du dépôt public dans %s : `python publier.py` le créera." % clone)
            return
        preparer_clone(clone)
        changements = synchroniser(travail, clone)
        if not changements:
            print("Le dépôt public est à jour : rien à publier.")
            return
        print(("Ce qui changerait" if verifier else "Ce qui change") + " dans le dépôt public :\n" + changements)
        if verifier:
            return
        source = git("rev-parse", "--short", "HEAD", cwd=RACINE).strip()
        message = "Publication depuis la source (%s, %s)" % (source, datetime.date.today().strftime("%d/%m/%Y"))
        git("commit", "-q", "-m", message, cwd=clone)
        git("push", "-q", "-u", "origin", BRANCHE, cwd=clone)
        print("Publié : %s — %s" % (git("rev-parse", "--short", "HEAD", cwd=clone).strip(), DEPOT[:-4]))
    finally:
        shutil.rmtree(travail, ignore_errors=True)


if __name__ == "__main__":
    main()
