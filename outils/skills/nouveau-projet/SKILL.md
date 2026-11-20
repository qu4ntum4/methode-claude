---
name: nouveau-projet
description: Mettre un projet de longue haleine en route selon la méthode de mémoire — copier les gabarits, poser les questions de départ, créer git — dans un dossier neuf ou un dossier qui existe déjà.
disable-model-invocation: true
argument-hint: "[dossier du projet]"
---

Mettre en route le projet « $ARGUMENTS » (sans argument : le dossier courant). Version du 20/11/2026.

1. **Regarder ce qui existe** dans le dossier : du code, des documents, un `.git`, un ancien
   TODO ou journal. Ne rien écraser : les gabarits ne s'écrivent que là où rien n'existe.
2. **Poser les questions de départ** avec `AskUserQuestion` — quatre au plus, à choix quand c'est
   possible, « Autre » pour le reste :
   - ce qu'est le projet, en une phrase, et pour qui ;
   - ce qui le rend sensible : données personnelles, secrets, matériel qui agit sur le réel,
     rien de tout ça ;
   - ce qui existe déjà et où (code, serveur, documents, une conversation à clore) ;
   - la commande qui vérifie que ça marche, si elle existe.
3. **Poser les fichiers** : `python "${CLAUDE_SKILL_DIR}/nouveau_projet.py" "<dossier>"`. Il copie
   les gabarits là où rien n'existe, crée `docs/chantiers/`, `docs/archives/`, initialise git si
   besoin et écrit un `.gitignore` de départ.
4. **Remplir les gabarits** avec les réponses — remplacer chaque « guillemet », retirer ce qui
   ne s'applique pas : `CLAUDE.md` (sommaire, commandes, règles, limites), `ETAT.md`
   (« Session principale », l'objectif, « Fini quand », une première action), `TODO.md`. Pas
   une ligne inventée : ce qu'on ne sait pas reste une question dans `ETAT.md`, « Ce qui attend
   une réponse ».
   **La ligne « Session principale »** dépend du dossier où cette session est ouverte
   (`get_session` avec `self` le donne, avec son titre) :
   - *dans le dossier du projet* : c'est elle, la principale. Si les règles globales fixent une
     forme pour le titre d'une session principale, la renommer d'abord à cette forme
     (`ToolSearch` « select:mcp__ccd_session_mgmt__set_session_title », puis
     `set_session_title` avec `self`), avec le nom court que l'utilisateur a donné, à défaut
     celui du dossier ; sans l'outil, ne pas la renommer, son premier point d'étape le
     proposera. Puis écrire son titre dans la ligne, entre guillemets, et dire dans le compte
     rendu si elle a été renommée ou non.
   - *ailleurs* : ne pas la renommer, et retirer la ligne de l'état. La principale sera la
     session que l'utilisateur ouvrira dans le dossier ; son premier point d'étape posera la
     ligne.
5. **S'il existe une conversation-fleuve sur ce projet**, le dire : elle doit faire un dernier
   point d'étape complet avant d'être close, et c'est l'utilisateur qui le lui demande.
6. **Si des données sensibles existent** : compléter `.gitignore` avant tout commit, et chercher
   les secrets dans ce que git suivrait (`git add -n .`).
7. **Premier commit**, message : « Mettre le projet en route : CLAUDE.md, ETAT.md, gabarits ».
8. **Rendre compte** en cinq lignes, et dire la suite : taper `/reprendre` — ici si cette
   session est ouverte dans le dossier du projet, sinon dans une session à ouvrir dans ce
   dossier.
