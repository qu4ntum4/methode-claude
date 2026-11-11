---
name: reprendre
description: Reprendre le travail sur un projet en début de session — état du projet, état git, une seule tâche avec son critère de fin.
disable-model-invocation: true
argument-hint: "[tâche ou chantier, facultatif]"
---

Reprendre le projet du dossier courant. Demande éventuelle de l'utilisateur : $ARGUMENTS

Version du 11/11/2026.

1. **Qui suis-je.** Demander à l'application le titre de cette session et sa session parente :
   `ToolSearch` « select:mcp__ccd_session_mgmt__get_session », puis `get_session` avec `self`.
   Une session parente, ou un titre qui nomme un chantier porté à part : c'est une **session
   annexe**. Son état n'est pas `ETAT.md` mais le bloc « Où en est la session » en tête de son
   chantier (`docs/chantiers/<x>.md`, sur sa branche, dans sa copie de travail). Sans l'outil, ou
   dans le doute, une question à cocher : les chantiers que « Des sessions » d'`ETAT.md` liste,
   ou « la principale ».
2. **L'état.** `ETAT.md` a normalement été injecté au démarrage par l'automatisme : ne pas le
   relire s'il est déjà dans le contexte. Dans la copie de travail d'un outil (dépôt à plusieurs
   outils), c'est `docs/<outil>/ETAT.md` — l'en-tête du démarrage le nomme. Dans une session
   annexe, lire le bloc de son chantier ; s'il manque (chantier d'avant le 04/11), prendre la
   première tâche ouverte du chantier, `[P1]` d'abord, le dire, et le bloc se posera au prochain
   point d'étape. Un `ETAT.md` modifié et non commité (`git status`) est en cours d'écriture par
   une autre session : ne pas s'y fier pour choisir la tâche. Pas d'état du tout : le dire, et
   proposer de le créer à partir de `CLAUDE.md`, du reste à faire et de `git log` — sans rien
   inventer.
3. **Git.** `git status --short` et `git log -5 --oneline`, dans sa copie de travail. Du travail
   non commité signale une session interrompue : le dire avant toute chose, sans y toucher.
4. **Vérifier une ou deux affirmations de l'état contre les fichiers** — la prochaine action
   n'est-elle pas déjà faite (`git log`) ? Une question annoncée en attente n'a-t-elle pas reçu
   sa réponse dans le registre des décisions ? Un état n'est qu'un instantané.
5. **Choisir une seule tâche** : la prochaine action de **son** état, telle quelle — celle
   d'`ETAT.md` pour la principale, celle du bloc de son chantier pour une session annexe, jamais
   la prochaine action de la principale. Si l'utilisateur demande autre chose, ou si l'état n'a pas de
   prochaine action, c'est **`/tache`** qui prend le relais : il trie la tâche nouvelle et
   choisit où elle s'exécute.
   Ouvrir **uniquement** les documents qu'elle demande, par le sommaire de `CLAUDE.md` ; un gros
   document se lit par son sommaire (`grep -n '^## '`), jamais en entier.
6. **Rendre compte en huit lignes au plus** : qui on est (la principale, ou le chantier qu'on
   porte), où on en est, la tâche retenue, ce qu'on va lire, **comment on saura qu'elle est
   finie**, et ce qui attend une réponse.
7. Puis enchaîner : si la tâche découle directement de l'état et ne demande aucun arbitrage, la
   commencer dans le même tour. Sinon, poser la question avec `AskUserQuestion`.
