# -*- coding: utf-8 -*-
"""
Installe la méthode dans Claude Code. Ce dossier est la SOURCE ; ~/.claude reçoit ce qui doit y
être, et rien d'autre.

    python installer.py            installe (ou met à jour)
    python installer.py --verifier dit seulement ce qui diverge, code de sortie 1 s'il y a un écart

Ce qui est fait :
  - les commandes de outils/skills/ sont copiées dans ~/.claude/skills/ (Claude Code ne lit que
    là) ; /nouveau-projet reçoit aussi une copie de gabarits/ ;
  - ~/.claude/settings.json est complété : les automatismes de la méthode pointent directement
    sur outils/hooks/ de ce dossier (pas de copie). L'installeur reconnaît les siens à leur
    script, remplace ceux-là et laisse à leur place ceux que d'autres outils ont posés ;
    --verifier ne répond que sur les siens (20/11). cleanupPeriodDays est posé, ainsi que le
    seuil de la compaction d'absence (env CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS, 08/11). Une
    sauvegarde settings.json.avant-installation est prise la première fois, et
    settings.json.avant-derniere-installation avant chaque écriture (20/11). Les autres clés
    sont gardées ;
  - les automatismes du capteur des sessions (hooks/signaler_sessions.py, chantier tableau-claude)
    ne sont posés que si ce script est là : il ne fait pas partie de la méthode publiée (11/11) ;
  - ~/.claude/CLAUDE.md, les règles valables dans tous les projets, est posé depuis
    gabarits/CLAUDE-global.md seulement s'il n'existe pas encore ; s'il existe, il n'y est pas
    touché, et l'installeur le dit (11/11).

Écrit le 18/10/2026.
"""
import filecmp
import json
import os
import re
import shutil
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
CLAUDE = os.path.expanduser("~/.claude")
PYTHON = sys.executable.replace("\\", "/")
HOOKS = os.path.join(ICI, "hooks").replace("\\", "/")
SKILLS_SOURCE = os.path.join(ICI, "skills")
SKILLS_CIBLE = os.path.join(CLAUDE, "skills")
# Les règles globales : un gabarit, posé une seule fois ; ensuite le fichier appartient à l'utilisateur.
GLOBAL_SOURCE = os.path.join(RACINE, "gabarits", "CLAUDE-global.md")
GLOBAL_CIBLE = os.path.join(CLAUDE, "CLAUDE.md")
# La compaction d'absence (idleCompaction) résume une session restée sans échange une heure environ,
# si son contexte dépasse ce seuil. 300 000 = le seuil où memoire_projet.py réclame déjà un point
# d'étape (l'utilisateur, 08/11/2026 ; défaut de Claude Code : 200 000, plancher 100 000).
ENV_VOULU = {"CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS": "300000"}


def commande(script, mode, timeout, **plus):
    h = {"type": "command", "command": PYTHON, "timeout": timeout,
         "args": ["-X", "utf8", HOOKS + "/" + script] + ([mode] if mode else [])}
    h.update(plus)
    return h


HOOKS_VOULUS = {
    "SessionStart": [
        {"matcher": "startup|resume|clear|compact",
         "hooks": [commande("memoire_projet.py", "demarrage", 15, statusMessage="Lecture de ETAT.md…")]},
        {"matcher": "startup",
         "hooks": [commande("archiver_conversations.py", None, 120)] },
    ],
    "UserPromptSubmit": [{"hooks": [commande("memoire_projet.py", "message", 10)]}],
    "PostToolUse": [{"matcher": "AskUserQuestion", "hooks": [commande("memoire_projet.py", "question", 10)]}],
    "PreCompact": [{"hooks": [commande("memoire_projet.py", "compaction", 10)]}],
    "Stop": [{"hooks": [commande("memoire_projet.py", "fin_de_tour", 10)]}],
}
HOOKS_VOULUS["SessionStart"][1]["hooks"][0]["async"] = True
# Capteur des sessions du chantier tableau-claude (08/11/2026) : publie l'état de chaque session
# dans MQTT, en arrière-plan. Les événements sont ceux dont il se sert (registre, 08/11). Sauf
# SessionEnd : Claude Code n'y attend pas un automatisme en arrière-plan, et se termine avant que
# le capteur ait noté la fermeture ; il y est donc attendu (registre, 08/11, « À la fermeture »).
# Le capteur ne fait pas partie de la méthode publiée : ses automatismes ne se posent que si son
# script est là, et --verifier suit la même règle (registre, 11/11/2026).
CAPTEUR = ["SessionStart", "SessionEnd", "UserPromptSubmit", "PreToolUse", "PostToolUse",
           "PostToolUseFailure", "PermissionRequest", "PermissionDenied", "SubagentStart",
           "SubagentStop", "Stop", "StopFailure", "PreCompact"]
CAPTEUR_PRESENT = os.path.exists(os.path.join(ICI, "hooks", "signaler_sessions.py"))
for _ev in (CAPTEUR if CAPTEUR_PRESENT else []):
    HOOKS_VOULUS.setdefault(_ev, []).append(
        {"hooks": [commande("signaler_sessions.py", None, 10,
                            **({} if _ev == "SessionEnd" else {"async": True}))]})
CLEANUP = 3650
# Les scripts que la méthode branche, ou a branchés un jour (sonde_evenements.py, retiré le 08/11).
# C'est à eux que l'installeur reconnaît SES automatismes dans settings.json, où que soit le
# dossier : il ne remplace que ceux-là, et ne touche pas à ceux d'un autre outil (20/11/2026).
SCRIPTS_METHODE = ("memoire_projet.py", "archiver_conversations.py", "signaler_sessions.py",
                   "sonde_evenements.py")
_SIEN = re.compile(r"/outils/hooks/(?:%s)(?![\w.-])" % "|".join(re.escape(s) for s in SCRIPTS_METHODE))


def est_de_la_methode(automatisme):
    """Vrai si la commande de cet automatisme lance un des scripts de la méthode."""
    if not isinstance(automatisme, dict):
        return False
    args = automatisme.get("args")
    morceaux = [automatisme.get("command")] + (args if isinstance(args, list) else [])
    return any(_SIEN.search(re.sub(r"[\\/]+", "/", m)) for m in morceaux if isinstance(m, str))


def partager(groupes):
    """Les groupes d'un événement, séparés : (ceux de la méthode, ceux des autres outils)."""
    siens, autres = [], []
    for g in groupes if isinstance(groupes, list) else []:
        contenu = g.get("hooks") if isinstance(g, dict) else None
        if not isinstance(contenu, list):
            autres.append(g)
            continue
        a_elle = [h for h in contenu if est_de_la_methode(h)]
        pas_a_elle = [h for h in contenu if not est_de_la_methode(h)]
        if a_elle:
            siens.append(dict(g, hooks=a_elle))
        if pas_a_elle or not a_elle:
            autres.append(dict(g, hooks=pas_a_elle) if a_elle else g)
    return siens, autres


def automatismes_fusionnes(actuels):
    """Ce qu'il faut écrire sous « hooks » : les automatismes de la méthode tels qu'elle les veut,
    puis ceux des autres outils, inchangés. Rend aussi le nombre de ces derniers, et si ceux de
    la méthode étaient déjà les bons : alors rien n'est à écrire, quel que soit leur ordre."""
    actuels = actuels if isinstance(actuels, dict) else {}
    fusion, gardes, a_jour = {}, 0, True
    for ev in list(actuels) + [e for e in HOOKS_VOULUS if e not in actuels]:
        siens, autres = partager(actuels.get(ev))
        voulus = HOOKS_VOULUS.get(ev, [])
        if siens != voulus:
            a_jour = False
        gardes += sum(len(g["hooks"]) if isinstance(g, dict) and isinstance(g.get("hooks"), list) else 1
                      for g in autres)
        if voulus or autres:
            fusion[ev] = voulus + autres
    return fusion, gardes, a_jour


def arbre(dossier):
    for racine, _, noms in os.walk(dossier):
        for n in noms:
            if n.endswith(".pyc") or "__pycache__" in racine:
                continue
            p = os.path.join(racine, n)
            yield os.path.relpath(p, dossier), p


def skills_attendus():
    """{chemin relatif dans ~/.claude/skills : fichier source}"""
    attendus = {}
    for rel, p in arbre(SKILLS_SOURCE):
        attendus[rel] = p
    for rel, p in arbre(os.path.join(RACINE, "gabarits")):
        if rel == os.path.basename(GLOBAL_SOURCE):
            continue  # les règles globales ne se posent pas dans un projet
        attendus[os.path.join("nouveau-projet", "gabarits", rel)] = p
    return attendus


def main():
    verifier = "--verifier" in sys.argv
    ecarts = []
    for rel, source in skills_attendus().items():
        cible = os.path.join(SKILLS_CIBLE, rel)
        if not os.path.exists(cible) or not filecmp.cmp(source, cible, shallow=False):
            ecarts.append("skills/" + rel.replace("\\", "/"))
            if not verifier:
                os.makedirs(os.path.dirname(cible), exist_ok=True)
                shutil.copyfile(source, cible)
    if os.path.exists(GLOBAL_SOURCE) and not os.path.exists(GLOBAL_CIBLE):
        ecarts.append("CLAUDE.md global (posé depuis gabarits/CLAUDE-global.md)")
        if not verifier:
            os.makedirs(CLAUDE, exist_ok=True)
            shutil.copyfile(GLOBAL_SOURCE, GLOBAL_CIBLE)
    elif os.path.exists(GLOBAL_CIBLE) and not verifier:
        print("~/.claude/CLAUDE.md existe déjà : laissé tel quel.")
    chemin = os.path.join(CLAUDE, "settings.json")
    try:
        reglages = json.load(open(chemin, encoding="utf-8"))
    except (OSError, ValueError):
        reglages = {}
    voulu = dict(reglages)
    quoi = []  # ce qui diffère dans les réglages, dit avec les mots de l'utilisateur
    automatismes, gardes, a_jour = automatismes_fusionnes(reglages.get("hooks"))
    if not a_jour:
        voulu["hooks"] = automatismes
        quoi.append("automatismes de la méthode")
    if reglages.get("cleanupPeriodDays") != CLEANUP:
        voulu["cleanupPeriodDays"] = CLEANUP
        quoi.append("conservation des conversations")
    env = dict(reglages.get("env") or {})
    env.update(ENV_VOULU)
    if env != reglages.get("env"):
        voulu["env"] = env
        quoi.append("seuil du résumé d'absence")
    if quoi:
        ecarts.append("settings.json (" + ", ".join(quoi) + ")")
        if not verifier:
            if os.path.exists(chemin):
                premiere = chemin + ".avant-installation"
                if not os.path.exists(premiere):
                    shutil.copyfile(chemin, premiere)
                shutil.copyfile(chemin, chemin + ".avant-derniere-installation")
            with open(chemin, "w", encoding="utf-8", newline="\n") as f:
                json.dump(voulu, f, ensure_ascii=False, indent=2)
                f.write("\n")
    if not ecarts:
        print("Tout est installé et au niveau de la source.")
        return
    print(("À installer : " if verifier else "Installé : ") + ", ".join(ecarts))
    if verifier:
        sys.exit(1)
    if gardes and not a_jour:
        print("Automatismes posés par d'autres outils, gardés tels quels : %d." % gardes)
    print("Les commandes et les automatismes s'appliquent aux nouvelles sessions : en ouvrir une pour les voir.")


if __name__ == "__main__":
    main()
