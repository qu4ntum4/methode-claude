# -*- coding: utf-8 -*-
"""
Archive les conversations de Claude Code en texte lisible : la mémoire de dernier recours.

    python archiver_conversations.py           ce qui a changé depuis le dernier passage
    python archiver_conversations.py --tout    tout, de nouveau

Une conversation brute (~/.claude/projects/<projet>/<id>.jsonl) pèse jusqu'à 100 Mo, dont 98 %
de sorties d'outils et de métadonnées. L'archive n'en garde que les messages de l'utilisateur et les
réponses de Claude, plus les résumés de compaction : environ 2 % du poids, lisible et cherchable.

    ~\\Documents\\Claude\\archives-conversations\\<projet>\\AAAA-MM-JJ_<titre>_<id>.md

**Hors de tout dépôt git et non synchronisé** : une conversation peut porter des données
personnelles. Ces fichiers ne se lisent que sur demande explicite de l'utilisateur
(règle dans ~/.claude/CLAUDE.md). Lancé au démarrage de chaque session par un automatisme ;
ne réécrit que les conversations modifiées. Écrit le 07/10/2026.
"""
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

SOURCE = os.path.expanduser("~/.claude/projects")
# Le dossier d'archive se calcule depuis le profil de l'utilisateur (11/11/2026) ; le libellé de ses
# messages dans l'archive est neutre, pour que l'outil se partage tel quel.
CIBLE = os.path.join(os.path.expanduser("~"), "Documents", "Claude", "archives-conversations")
UTILISATEUR = "Utilisateur"
ETAT = os.path.join(CIBLE, ".etat.json")
RAPPELS = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)


def heure_locale(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()
    except (ValueError, AttributeError):
        return None


def nettoyer(nom):
    nom = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", nom)
    return re.sub(r"\s+", " ", nom).strip()[:60].rstrip(" .")


def texte_de(contenu):
    if isinstance(contenu, str):
        return contenu
    morceaux = [x.get("text", "") for x in contenu or []
                if isinstance(x, dict) and x.get("type") == "text"]
    return "\n\n".join(m for m in morceaux if m)


def encoder(cwd):
    """Le nom du dossier où Claude Code range les conversations d'un dossier de travail."""
    return re.sub(r"[^A-Za-z0-9]", "-", cwd)


def lire(chemin):
    # Le projet est celui où Claude Code range la conversation, pas le dossier du premier
    # message : une conversation peut commencer ailleurs (constaté le 07/10 sur celle de HA).
    rangement = os.path.basename(os.path.dirname(chemin))
    titre, cwd, debut, blocs = None, None, None, []
    vus = []
    with open(chemin, encoding="utf-8", errors="replace") as fh:
        for ligne in fh:
            try:
                d = json.loads(ligne)
            except ValueError:
                continue
            t = d.get("type")
            if t == "custom-title" and d.get("customTitle"):
                titre = d["customTitle"]
                continue
            if t not in ("user", "assistant") or d.get("isSidechain") or d.get("isMeta"):
                continue
            m = d.get("message")
            if not isinstance(m, dict):
                continue
            if d.get("cwd") and d["cwd"] not in vus:
                vus.append(d["cwd"])
            quand = heure_locale(d.get("timestamp"))
            debut = debut or quand
            texte = RAPPELS.sub("", texte_de(m.get("content"))).strip()
            if not texte or texte.startswith("<local-command") or texte.startswith("[Request interrupted"):
                continue
            if d.get("isCompactSummary"):
                qui = "Résumé automatique (compaction)"
            elif m.get("role") == "user":
                qui = UTILISATEUR
                cmd = re.search(r"<command-name>(/[^<]+)</command-name>", texte)
                if cmd:
                    texte = "*(commande `%s`)*" % cmd.group(1)
                elif texte.startswith("Base directory for this skill"):
                    continue  # le texte d'une commande, déjà signalée
            else:
                qui = "Claude"
            if blocs and blocs[-1][0] == qui == "Claude":
                blocs[-1][2].append(texte)  # une réponse en plusieurs morceaux = un seul bloc
            else:
                blocs.append((qui, quand, [texte]))
    cwd = next((c for c in vus if encoder(c) == rangement), vus[0] if vus else None)
    if cwd and encoder(cwd) != rangement:
        cwd = None  # aucun dossier ne correspond : on se rabat sur le nom du rangement
    return titre, cwd or rangement, debut, blocs


def ecrire(chemin_source, etat):
    titre, cwd, debut, blocs = lire(chemin_source)
    if not blocs:
        return None
    ident = os.path.splitext(os.path.basename(chemin_source))[0]
    projet = nettoyer(os.path.basename((cwd or "").rstrip("\\/")) or "sans-dossier")
    nom = etat.get(ident, {}).get("fichier")
    if not nom:  # le nom est fixé au premier passage : un titre qui change ne crée pas de doublon
        premier = next((b[2][0] for b in blocs if b[0] == UTILISATEUR), "")
        libelle = nettoyer(titre or premier) or "conversation"
        nom = os.path.join(projet, "%s_%s_%s.md" % ((debut or datetime.now()).strftime("%Y-%m-%d"),
                                                    libelle, ident[:8]))
    dest = os.path.join(CIBLE, nom)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    fin = next((b[1] for b in reversed(blocs) if b[1]), debut)
    lignes = ["# %s" % (titre or "Conversation"), "",
              "- Dossier : `%s`" % (cwd or "?"),
              "- Du %s au %s" % (debut.strftime("%d/%m/%Y %H:%M") if debut else "?",
                                 fin.strftime("%d/%m/%Y %H:%M") if fin else "?"),
              "- Source : `%s` (complète, sorties d'outils comprises)" % chemin_source, "",
              "> Archive brute, non relue. **Ce qui fait foi est dans les fichiers du projet**, pas ici.",
              ""]
    for qui, quand, textes in blocs:
        lignes += ["---", "", "### %s — %s" % (qui, quand.strftime("%d/%m %H:%M") if quand else ""), "",
                   "\n\n".join(textes), ""]
    with open(dest + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lignes))
    os.replace(dest + ".tmp", dest)
    etat[ident] = {"fichier": nom, "mtime": os.path.getmtime(chemin_source)}
    return dest


def main():
    tout = "--tout" in sys.argv
    os.makedirs(CIBLE, exist_ok=True)
    try:
        etat = json.load(open(ETAT, encoding="utf-8"))
    except (OSError, ValueError):
        etat = {}
    faits = 0
    for chemin in glob.glob(os.path.join(SOURCE, "*", "*.jsonl")):
        ident = os.path.splitext(os.path.basename(chemin))[0]
        if not tout and etat.get(ident, {}).get("mtime") == os.path.getmtime(chemin):
            continue
        try:
            if ecrire(chemin, etat):
                faits += 1
        except Exception as e:  # une conversation illisible ne doit pas bloquer les autres
            print("Ignorée %s : %s" % (ident, e), file=sys.stderr)
    with open(ETAT, "w", encoding="utf-8") as f:
        json.dump(etat, f, ensure_ascii=False, indent=1)
    print("%d conversation(s) archivée(s) dans %s" % (faits, CIBLE))


if __name__ == "__main__":
    main()
