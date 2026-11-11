---
name: checkpoint
description: Point d'étape — vérifier, consigner décisions et documentation, ranger puis réécrire ETAT.md, tenir le reste à faire, commiter. Après une étape vérifiée, une décision ou un diagnostic coûteux, et toujours avant /clear. Claude ne le lance qu'après la confirmation explicite de l'utilisateur.
---

Point d'étape sur le projet du dossier courant. Le `CLAUDE.md` du projet peut compléter cette
liste (section « Point d'étape ») : ses ajouts s'appliquent en plus. Version du 11/11/2026.

**Qui le lance** : l'utilisateur ; ou Claude, après l'avoir proposé et reçu un oui explicite —
jamais de lui-même, et jamais de copie à la main à la place de la commande. Avant de proposer
`/clear`, Claude propose d'abord ce point d'étape (l'utilisateur, 03/11/2026).

**L'état**, c'est le fichier que l'automatisme a affiché au démarrage — son nom est dans
l'en-tête : `ETAT.md`, ou `docs/<outil>/ETAT.md` dans la copie de travail d'un outil quand un
dépôt en porte plusieurs. **Une copie ne réécrit que le sien**, et son registre est alors
`docs/<outil>/decisions.md`. Ce qui suit dit `ETAT.md` et `docs/decisions.md` pour l'un ou
l'autre.

1. **Vérifier.** Lancer la commande de tests ou de contrôles du projet. En cas d'échec :
   s'arrêter, le dire, ne rien commiter. Si elle répond que ce code est déjà passé au vert (son
   empreinte n'a pas bougé), la croire : ne pas forcer une relance sans raison.
2. **Relire le diff** : `git diff --stat`, puis le détail de ce qui compte.
3. **Les décisions.** Lister les arbitrages validés par l'utilisateur **depuis le dernier point
   d'étape** de cette conversation ; vérifier chacun au registre (`docs/decisions.md`) ; écrire
   ce qui manque — date, sa formulation citée, le pourquoi, **ce qui a été écarté**. Les choix
   faits sans lui pendant ce travail s'écrivent aussi, marqués **[décision de l'agent, à revoir]**.
4. **La documentation devenue fausse** avec ce travail : la mettre à jour maintenant.
5. **Les autres sessions et les branches.** Ce que d'autres sessions ont livré depuis la
   dernière version de l'état :
   `git log --all --oneline --since="$(git log --all -1 --format=%cI -- ETAT.md)"` — un commit
   que cette conversation n'a pas fait s'intègre à l'état, et la ligne qui l'attendait sort ;
   ne rien écraser qu'on n'a pas lu. Puis `git branch --no-merged` : chaque branche ouverte et
   chaque travail confié ailleurs a sa ligne dans « Ce qui attend une réponse », avec **où le
   résultat doit arriver**. Une ligne reçue d'une session annexe (« livré : commit X sur Y,
   prochaine action : … ») se colle **telle quelle** sous « Des sessions », sans la résumer ;
   les messages reçus entre deux points d'étape attendent celui-ci — on ne réécrit pas l'état
   en pleine tâche, une autre session peut le relire à cet instant.
6. **Ranger, puis réécrire `ETAT.md`** en le remplaçant, jamais en ajoutant. **Une session
   annexe** (celle qui ne tient pas `ETAT.md`) réécrit à la place le bloc « Où en est la
   session » en tête de son chantier — copie, branche, port d'essai, **une seule** prochaine
   action, fini quand ; le poser d'après le gabarit s'il manque. Pour `ETAT.md` : d'abord sortir
   ce qui n'y a pas sa place : un piège durable → `docs/pieges.md` ; une question ouverte depuis
   plus d'une semaine → le chantier concerné ; une recette ou un fait de configuration → le
   document du sujet ; une règle → `CLAUDE.md`. Puis écrire : l'objectif en cours et **« Fini
   quand : … »**, où on en est, **une seule** prochaine action, ce qui attend une réponse (et de
   qui), ce qu'il ne faut pas oublier. **Compter les lignes (`wc -l ETAT.md`) avant le commit**,
   pas après : moins de 60, sinon ranger encore. Date et heure vérifiées par une commande.
   Aucun nom de personne si le fichier est versionné.
7. **Le reste à faire.** Retirer des chantiers ce qui est fait ; ajouter ce que l'utilisateur a
   validé, **avec sa priorité** (`[P1]`-`[P3]` en tête de tâche, obligatoire dans `divers.md`) ;
   une tâche sans famille va dans `docs/chantiers/divers.md` (le créer depuis le gabarit s'il
   manque). Puis `python "${CLAUDE_SKILL_DIR}/chantiers.py" --ecrire` : il met à jour les comptes
   du sommaire, trie les chantiers par priorité quand la colonne **P** existe, et marque « dort
   depuis le … » tout chantier sans mouvement depuis un mois. Si le sommaire n'a pas encore de
   colonne **P** (projets d'avant le 03/11), l'ajouter maintenant — priorités à demander à
   l'utilisateur, à cocher. Un chantier à zéro part en archive
   (`git mv docs/chantiers/<x>.md docs/archives/`) et sa ligne quitte le sommaire.
8. **Si ce travail ferme un chantier** : relire les entrées **[décision de l'agent, à revoir]**
   de ce chantier dans le registre, les soumettre à l'utilisateur par `AskUserQuestion`
   (multiSelect), et retirer la marque sur celles qu'il confirme ; consigner ce qu'il refuse.
9. **Commit** cohérent, message qui dit ce qui change et pourquoi. Ne pas pousser sans accord.
10. **Rendre compte en six lignes au plus** : ce qui a été consigné, le commit, ce qui reste
    ouvert. Une session annexe envoie en plus à la principale une ligne complète — chantier,
    commit, prochaine action —, celle qui ira telle quelle sous « Des sessions ». Si la tâche
    est terminée, le dire : c'est le moment de faire `/clear`.

Projet sans `ETAT.md` : proposer de le créer (`/nouveau-projet` pose les gabarits), puis faire
le reste.
