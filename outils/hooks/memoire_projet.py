# -*- coding: utf-8 -*-
"""
Automatismes de mémoire de projet, pour Claude Code. Inactifs dans tout dossier sans ETAT.md.

    memoire_projet.py demarrage   SessionStart (startup, resume, clear, compact) :
                                  injecte l'état de la copie de travail (ETAT.md, ou celui de
                                  son outil — voir fichier_etat), l'état git et les derniers
                                  commits ; avertit si l'état dépasse la limite.
    memoire_projet.py message     UserPromptSubmit :
                                  - alerte quand le contexte de la conversation dépasse un seuil ;
                                  - si le message ressemble à une validation (« ok », « d'accord »,
                                    « 1. … »), rappelle de consigner la décision — au plus une fois
                                    par tâche, et seulement si le registre n'a pas bougé depuis.
    memoire_projet.py question    PostToolUse sur AskUserQuestion : même rappel, mêmes limites.
    memoire_projet.py compaction  PreCompact : dicte au résumé ce qu'il doit garder pour que la
                                  session reprenne — qui elle est, la tâche, la prochaine action,
                                  les décisions non consignées, les fichiers non commités —, à la
                                  place du plan par défaut du résumé ; et note chaque appel dans
                                  ~/.claude/memoire_projet/compactions.jsonl (heure locale, session,
                                  déclencheur, taille de la consigne émise, erreur éventuelle).
    memoire_projet.py fin_de_tour Stop : au-dessus du seuil de contexte, fait continuer Claude une
                                  fois, pour qu'il propose le point d'étape avant de rendre la main.

Écrit le 04/10/2026, revu le 18/10/2026 (alerte de contexte, rappel moins bavard), le
19/10/2026 (un état par outil dans un dépôt à plusieurs outils) et le 08/11/2026 (consigne du
résumé, proposition de point d'étape en fin de tour ; le soir, après la première compaction
d'absence observée : la consigne remplace le plan par défaut, et le journal des appels). Ne
bloque jamais une session : le seul « blocage » est celui d'une fin de tour, une fois, le temps
d'une phrase ; en cas d'erreur, il se tait (code de sortie 0).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

LIMITE_ETAT = 60
SEUIL_CONTEXTE = 300_000      # jetons envoyés par échange, au-delà : proposer un point d'étape
PAS_ALERTE = 150_000          # ne pas répéter l'alerte avant que le contexte ait grossi d'autant
VALIDATIONS_AVANT_RAPPEL = 8  # entre deux rappels sans mouvement du registre
REGISTRES = ("docs/decisions.md", "decisions.md", "DECISIONS.md", "docs/historique.md")
JOURNAL_COMPACTIONS = os.path.join(os.path.expanduser("~"), ".claude", "memoire_projet", "compactions.jsonl")

RAPPEL = (
    "Rappel automatique (mémoire de projet) : si ce qui vient d'être répondu tranche un arbitrage, "
    "l'écrire d'abord dans le registre des décisions du projet (date, formulation de l'utilisateur, "
    "pourquoi, ce qui a été écarté — ou la marque [décision de l'agent, à revoir]), avant ou avec "
    "le code. Si rien n'a été tranché, ignorer ce rappel."
)
ALERTE = (
    "Alerte automatique (mémoire de projet) : le contexte de cette conversation atteint %s jetons "
    "par échange (seuil %s). Dès que l'étape en cours est vérifiée, proposer un point d'étape "
    "(/checkpoint) puis /clear plutôt que d'enchaîner ; ne pas couper au milieu d'une étape."
)
PROPOSITION = (
    "Automatisme (mémoire de projet) : le contexte de cette conversation atteint %s jetons. Avant de "
    "rendre la main, ajouter une ligne à la réponse : proposer à l'utilisateur le point d'étape "
    "(/checkpoint) dès que l'étape en cours est vérifiée, puis /clear — sans le lancer sans son oui, "
    "sans reprendre le travail, sans répéter ce qui vient d'être dit. Si une question lui est déjà "
    "posée, la proposition s'y ajoute. Puis terminer le tour."
)
CONSIGNE_RESUME = """Consigne de résumé (mémoire de projet). Ce projet suit une méthode où l'état vit dans des fichiers ; après ce résumé, CLAUDE.md et le fichier d'état (%(etat)s) seront relus automatiquement : ne pas les paraphraser, ne pas en recopier les règles, même sous un titre « contraintes à garder » ou « règles du projet » : elles reviendront d'elles-mêmes. Le résumé doit permettre à la session de reprendre exactement là où elle en était.
Cette consigne remplace le plan habituel du résumé : pas de sections « Primary Request and Intent », « Key Technical Concepts », « Files and Code Sections », « Errors and fixes », « All user messages », « Pending Tasks », « Current Work », ni leurs équivalents. Le résumé est écrit en français, sans extrait de code (la session relira les fichiers), et n'a que ces six sections, numérotées, dans cet ordre :
1. Qui est cette session : la principale du projet, ou une session annexe qui porte un chantier — lequel, sa copie de travail, sa branche, son port d'essai.
2. La tâche en cours, avec les mots de l'utilisateur quand il les a donnés, et son « fini quand ».
3. La prochaine action, précise, et ce qui a été fait depuis le dernier point d'étape (/checkpoint dans cette conversation : %(quand)s), y compris les erreurs corrigées qui comptent encore. Si le point d'étape est dû, le dire en première ligne du résumé.
4. Les décisions que l'utilisateur a validées et qui ne sont pas encore écrites au registre des décisions, avec sa formulation.
5. Les questions posées à l'utilisateur restées sans réponse, et ce qu'on attend d'autres sessions.
6. Les fichiers modifiés non commités dans cette copie de travail au moment du résumé (d'autres sessions peuvent partager le dossier) :
%(fichiers)s
Rien d'autre : ni liste de tous les messages de l'utilisateur, ni inventaire des fichiers lus, ni rappel des règles.
"""
VALIDATION = re.compile(
    r"^\s*(ok\b|okay\b|oui\b|yes\b|d'?accord\b|dac\b|go\b|vas[- ]?y\b|valid|je valide|parfait\b"
    r"|c'?est bon\b|ça me va|ca me va|on part sur|on garde|tranch|exact\b|1\s*[.):])",
    re.IGNORECASE,
)


# --- entrée, sortie, état ---------------------------------------------------------------------

def lire_entree():
    try:
        return json.loads(sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
    except ValueError:
        return {}


def repondre(evenement, texte):
    sortie = {"hookSpecificOutput": {"hookEventName": evenement, "additionalContext": texte}}
    sys.stdout.buffer.write(json.dumps(sortie, ensure_ascii=False).encode("utf-8"))


def chemin_etat_session(entree):
    """Un petit fichier d'état par session : compteurs de rappels et d'alertes."""
    dossier = entree.get("scratchpad_dir") or os.path.join(tempfile.gettempdir(), "memoire_projet")
    os.makedirs(dossier, exist_ok=True)
    return os.path.join(dossier, "memoire_projet_%s.json" % (entree.get("session_id") or "session"))


def lire_etat_session(entree):
    try:
        with open(chemin_etat_session(entree), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def ecrire_etat_session(entree, etat):
    try:
        with open(chemin_etat_session(entree), "w", encoding="utf-8") as f:
            json.dump(etat, f)
    except OSError:
        pass


def git(projet, *args):
    try:
        r = subprocess.run(["git", "-C", projet] + list(args), capture_output=True, timeout=8)
        return r.stdout.decode("utf-8", "replace").strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def fichier_etat(projet):
    """L'état de cette copie de travail : ETAT.md, sauf dans la copie d'un outil.

    Un dépôt qui porte plusieurs outils menés en parallèle donne à chacun son état,
    docs/<outil>/ETAT.md, que seules les sessions de cet outil réécrivent. Une copie de travail
    dont la branche s'appelle <outil>, ou commence par « <outil>- », affiche cet état-là ; toute
    autre copie affiche ETAT.md. Renvoie le chemin relatif, avec « / ».
    """
    branche = git(projet, "rev-parse", "--abbrev-ref", "HEAD")
    if branche:
        try:
            outils = sorted(os.listdir(os.path.join(projet, "docs")))
        except OSError:
            outils = []
        for outil in outils:
            if branche == outil or branche.startswith(outil + "-"):
                if os.path.isfile(os.path.join(projet, "docs", outil, "ETAT.md")):
                    return "docs/%s/ETAT.md" % outil
    return "ETAT.md"


# --- les services ---------------------------------------------------------------------------

def demarrage(projet, entree):
    rel = fichier_etat(projet)
    etat = open(os.path.join(projet, *rel.split("/")), encoding="utf-8", errors="replace").read().strip()
    n = etat.count("\n") + 1
    parties = ["## %s — affiché automatiquement (%s)" % (rel, entree.get("source", "?")), "", etat]
    if n > LIMITE_ETAT:
        parties.append("\n> %s fait %d lignes, au-delà des %d visées : le réécrire, plus court, "
                       "au prochain point d'étape." % (rel, n, LIMITE_ETAT))
    statut = git(projet, "status", "--short", "--branch")
    if statut:
        lignes = statut.splitlines()
        parties += ["", "## git status", "```", "\n".join(lignes[:25])
                    + ("\n… (%d lignes de plus)" % (len(lignes) - 25) if len(lignes) > 25 else ""), "```"]
        journal = git(projet, "log", "-3", "--format=%h %ad %s", "--date=format:%d/%m %H:%M")
        if journal:
            parties += ["", "## Derniers commits", "```", journal, "```"]
        branches = git(projet, "branch", "--no-merged")
        if branches.strip():
            parties += ["", "## Branches non fusionnées", "```", branches, "```"]
    repondre("SessionStart", "\n".join(parties))


def contexte_courant(transcript):
    """La taille du contexte au dernier échange : lue en fin de journal, sans tout charger."""
    if not transcript or not os.path.isfile(transcript):
        return None
    try:
        taille = os.path.getsize(transcript)
        with open(transcript, "rb") as f:
            f.seek(max(0, taille - 2_000_000))
            queue = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    for ligne in reversed(queue.splitlines()):
        if '"cache_read_input_tokens"' not in ligne and '"input_tokens"' not in ligne:
            continue
        try:
            d = json.loads(ligne)
        except ValueError:
            continue
        m = d.get("message")
        if not isinstance(m, dict) or m.get("role") != "assistant":
            continue
        u = m.get("usage") or {}
        total = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                 + u.get("cache_creation_input_tokens", 0))
        if total:
            return total
    return None


def registre_modifie_depuis(projet, instant):
    """Le registre du projet, ou celui d'un de ses outils (docs/<outil>/decisions.md), a-t-il bougé ?"""
    chemins = [os.path.join(projet, *rel.split("/")) for rel in REGISTRES]
    try:
        docs = os.path.join(projet, "docs")
        chemins += [os.path.join(docs, d, "decisions.md") for d in os.listdir(docs)]
    except OSError:
        pass
    connus = [c for c in chemins if os.path.isfile(c)]
    # pas de registre connu : on se fie aux compteurs seuls
    return any(os.path.getmtime(c) > instant for c in connus)


def message(projet, entree, evenement, validation):
    """Alerte de contexte, puis rappel de consignation — chacun sous ses propres limites."""
    etat = lire_etat_session(entree)
    textes = []

    ctx = contexte_courant(entree.get("transcript_path"))
    if ctx and ctx > SEUIL_CONTEXTE and ctx - etat.get("alerte_contexte", 0) >= PAS_ALERTE:
        textes.append(ALERTE % (format(ctx, ",").replace(",", " "), format(SEUIL_CONTEXTE, ",").replace(",", " ")))
        etat["alerte_contexte"] = ctx

    if validation:
        etat["validations"] = etat.get("validations", 0) + 1
        depuis = etat["validations"] - etat.get("rappel_a_la_validation", 0)
        premier = "rappel_a_la_validation" not in etat
        registre_bouge = registre_modifie_depuis(projet, etat.get("rappel_ts", 0))
        if premier or (depuis >= VALIDATIONS_AVANT_RAPPEL and not registre_bouge):
            textes.append(RAPPEL)
            etat["rappel_a_la_validation"] = etat["validations"]
            etat["rappel_ts"] = time.time()

    ecrire_etat_session(entree, etat)
    if textes:
        repondre(evenement, "\n\n".join(textes))


def journaliser_compaction(entree, projet, consigne, erreur=""):
    """Une ligne par appel du hook de compaction, hors de tout dépôt.

    Le 08/11/2026, à la première compaction d'absence observée, un résumé ne portait aucune trace
    de la consigne, et rien ne disait si elle avait été émise. Heure locale, comme le relevé de la
    sonde ; les journaux de session, eux, sont en UTC.
    """
    try:
        os.makedirs(os.path.dirname(JOURNAL_COMPACTIONS), exist_ok=True)
        ligne = {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "session_id": entree.get("session_id"),
                 "trigger": entree.get("trigger"), "projet": projet,
                 "consigne": len(consigne), "erreur": erreur}
        with open(JOURNAL_COMPACTIONS, "a", encoding="utf-8") as f:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    except OSError:
        pass


def compaction(projet, entree):
    """Avant toute compaction : la consigne du résumé, en texte brut sur la sortie standard
    (Claude Code en fait les instructions du résumé, jusqu'à 10 000 caractères), et une ligne au journal."""
    texte, erreur = "", ""
    try:
        etat = lire_etat_session(entree)
        rel = fichier_etat(projet)
        statut = git(projet, "status", "--short")
        lignes = statut.splitlines() if statut else []
        if lignes:
            fichiers = "\n".join("   " + l for l in lignes[:20])
            if len(lignes) > 20:
                fichiers += "\n   … (%d de plus)" % (len(lignes) - 20)
        else:
            fichiers = "   (aucun : la copie est propre)"
        dernier = etat.get("checkpoint_ts")
        quand = time.strftime("le %d/%m à %H:%M", time.localtime(dernier)) if dernier else "aucun dans cette conversation"
        texte = CONSIGNE_RESUME % {"etat": rel, "quand": quand, "fichiers": fichiers}
    except Exception as e:  # la consigne manque, mais le journal le dira
        erreur = "%s: %s" % (type(e).__name__, e)
    journaliser_compaction(entree, projet, texte, erreur)
    if texte:
        sys.stdout.buffer.write(texte.encode("utf-8"))


def fin_de_tour(projet, entree):
    """Fin d'un tour au-dessus du seuil : Claude continue une fois, pour proposer le point d'étape."""
    if entree.get("stop_hook_active"):  # c'est déjà nous qui l'avons fait continuer
        return
    etat = lire_etat_session(entree)
    ctx = contexte_courant(entree.get("transcript_path"))
    if not ctx or ctx <= SEUIL_CONTEXTE:
        return
    if ctx - etat.get("proposition_fin_de_tour", 0) < PAS_ALERTE:  # une fois par niveau, et par tâche
        return
    etat["proposition_fin_de_tour"] = ctx
    etat["alerte_contexte"] = max(etat.get("alerte_contexte", 0), ctx)  # l'alerte du message suivant se tait
    ecrire_etat_session(entree, etat)
    sortie = {"decision": "block", "reason": PROPOSITION % format(ctx, ",").replace(",", " ")}
    sys.stdout.buffer.write(json.dumps(sortie, ensure_ascii=False).encode("utf-8"))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    entree = lire_entree()
    projet = os.environ.get("CLAUDE_PROJECT_DIR") or entree.get("cwd") or os.getcwd()
    if not os.path.isfile(os.path.join(projet, "ETAT.md")):
        if mode == "compaction":  # le journal dit aussi quand la consigne n'a pas été émise, et pourquoi
            journaliser_compaction(entree, projet, "", "pas d'ETAT.md dans ce dossier : consigne non émise")
        return
    if mode == "demarrage":
        demarrage(projet, entree)
    elif mode == "message":
        texte = entree.get("prompt") or ""
        if entree.get("slash_command") or texte.lstrip().startswith("/"):
            if "checkpoint" in texte:  # un point d'étape ouvre une nouvelle tâche : les compteurs repartent
                etat = lire_etat_session(entree)
                etat.pop("rappel_a_la_validation", None)
                etat.pop("proposition_fin_de_tour", None)
                etat["validations"] = 0
                etat["checkpoint_ts"] = time.time()
                ecrire_etat_session(entree, etat)
            return
        valide = bool(VALIDATION.match(texte)) or "je suis d'accord" in texte.lower()
        message(projet, entree, "UserPromptSubmit", valide)
    elif mode == "question":
        message(projet, entree, "PostToolUse", True)
    elif mode == "compaction":
        compaction(projet, entree)
    elif mode == "fin_de_tour":
        fin_de_tour(projet, entree)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # un automatisme ne doit jamais gêner la session
        pass
    sys.exit(0)
