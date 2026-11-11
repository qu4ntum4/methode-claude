---
name: tache
description: Trier une tâche nouvelle avant de la lancer — la comprendre, poser les questions que l'état ne tranche pas, choisir son environnement (session courante, nouvelle session, session annexe dans une copie de travail, sous-agent, fork), et la lancer avec l'accord de l'utilisateur. Sans description, propose la tâche suivante.
disable-model-invocation: true
argument-hint: "[description de la tâche, ou rien pour la suivante]"
---

Tâche demandée : $ARGUMENTS

Pour **continuer** le chantier en cours en début de session, c'est `/reprendre`, pas ceci.
Version du 04/11/2026.

## 0. Sans description : proposer la suivante

Lire `ETAT.md` (déjà injecté) et le sommaire de `TODO.md` : la prochaine action de l'état
d'abord ; sinon la première tâche ouverte d'un chantier de priorité 1, en commençant par les
marques `[P1]` ; sinon priorité 2. Proposer **une** tâche, dire pourquoi celle-là, et passer au
triage ci-dessous une fois que l'utilisateur l'a retenue (ou en a nommé une autre).

## 1. Comprendre

La tâche en deux lignes, et **« fini quand : … »** — un critère vérifiable. Si la tâche n'est
pas claire, c'est ici qu'on le dit, avant tout le reste.

## 2. Les questions que l'état ne tranche pas

Seulement celles-là, par `AskUserQuestion`, à cocher :
- touche-t-elle les **mêmes fichiers** que le chantier en cours, ou d'autres ?
- a-t-elle besoin de **ce qui a été dit** dans cette session, ou repart-elle des fichiers ?
- se livre-t-elle **par un commit, sans arbitrage** en route — ou va-t-elle poser des
  questions à mesure ?
- **la principale doit-elle continuer** pendant ce temps ?
- a-t-elle besoin des **fichiers non commités ou ignorés par git** (données locales, base) ?

## 3. L'avis, et l'environnement

| Si la tâche… | Environnement |
|---|---|
| prolonge ce qu'on fait, mêmes fichiers, contexte utile | **session courante** |
| est indépendante et le contexte actuel ne lui sert pas | **nouvelle session** |
| peut tourner en parallèle, autres fichiers, livrable par un commit sans arbitrage | **session annexe** dans une copie de travail |
| est une enquête ou une lecture massive dont seul le résumé compte | **sous-agent** |
| a besoin de tout ce qui vient d'être dit pour explorer une autre piste | **fork** — rare |

Dire l'environnement proposé **et la raison**, en trois lignes. Une session annexe travaille dans
une copie de travail **neuve** : elle ne voit ni les fichiers non commités ni les fichiers ignorés
par git — pour ceux-là, un sous-agent ici. Puis demander l'accord.

## 4. Lancer, avec l'accord

- **Session courante** : enchaîner, sans s'arrêter.
- **Nouvelle session** : proposer le point d'étape, puis lancer `/checkpoint` sur le oui, avec
  cette tâche comme prochaine action d'`ETAT.md` et son « fini quand » ; dire à l'utilisateur :
  `/clear`, puis `/reprendre`.
- **Session annexe** : écrire la consigne, puis déposer une pastille avec `spawn_task`
  (`cwd` = la racine du projet ; **vérifier au premier lancement** dans quel dossier
  l'application l'ouvre — si c'est le dossier du projet, la consigne lui fait d'abord créer sa
  copie de travail). La consigne dit : la tâche et son « fini quand » ; **où ça rend** (un commit
  sur la branche de la copie, et le registre si quelque chose est tranché) ; **ce qu'elle ne
  touche pas** (`ETAT.md`, la branche principale, les fichiers du chantier en cours) ; **son
  état** (le bloc « Où en est la session » en tête de son chantier, réécrit à chaque point
  d'étape) ; **qui prévenir** (le nom de cette session, lu par `ListAgents`), par une ligne
  complète « livré : commit X sur Y, prochaine action : … ». Ajouter une ligne sous « Des
  sessions » d'`ETAT.md` au prochain point d'étape. Rien n'est lancé tant que l'utilisateur n'a
  pas cliqué : c'est son accord.
- **Sous-agent** : le lancer (`Agent`), avec un contrat — question, périmètre, résultat attendu,
  preuves, ce qu'il ne modifie pas. Ce qu'il trouve et qui compte, **cette** session l'écrit au
  bon endroit : il ne consigne rien.
- **Fork** : dire que c'est le bon outil et pourquoi ; c'est l'utilisateur qui le fait dans
  l'application.

Rendre compte en quatre lignes : la tâche, l'environnement, ce qui a été lancé, ce qui attend.
