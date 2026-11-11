# Tenir un projet de longue haleine avec un agent de code

*Une méthode pour ne pas perdre d'information et ne pas brûler de jetons quand un projet mené
avec un agent de code (Claude Code ici, mais la méthode ne lui est pas propre) dure des semaines
ou des mois. Version du 18/10/2026, après deux semaines d'application sur neuf projets réels,
dont deux lourds : une application métier de planification et une domotique.*

---

## 0. Le problème, tel qu'il se mesure

L'intuition de départ était « on perd de l'information **entre** les sessions ». La mesure a
dit autre chose. Sur deux projets réels tenus pendant deux à trois semaines dans **une seule
conversation chacun** :

| | Projet métier | Domotique |
|---|---|---|
| Compactions subies | 12 | 10 |
| Contexte envoyé à chaque échange (médiane) | 515 000 jetons | 531 000 jetons |
| Échanges au-delà de 300 000 jetons | 76 % | 76 % |
| Part des jetons qui ne servent qu'à relire | 98 % | 98 % |

L'information se perdait **dans les compactions** — le résumé automatique ne garde que ce qui
est sur le disque, pas ce qui a été dit — et chaque échange relisait un demi-million de jetons.
Les règles de travail, elles, ne vivaient que dans la mémoire locale de l'agent, invisible
depuis un autre dossier et absente de toute sauvegarde.

Trois conséquences qui fondent tout le reste :

1. **Ce qui compte doit être sur le disque, au bon endroit, au moment où c'est dit** — pas en
   fin de session, qui n'arrive jamais proprement.
2. **Une conversation ne doit pas durer des semaines.** Elle doit être courte, et redémarrer
   depuis les fichiers.
3. **Ce qui est chargé à chaque démarrage doit être petit** ; tout le reste se lit à la demande.

---

## 1. Les principes

1. **Un fait, un seul domicile.** Une règle, une décision, un piège vit dans un fichier, et les
   autres y renvoient. Deux copies divergent le jour où l'une change, et la seconde devient un
   mensonge silencieux.
2. **L'état se réécrit, l'histoire s'ajoute.** Un fichier d'état est remplacé à chaque point
   d'étape et reste court. Un registre de décisions ne fait que grandir et n'est jamais chargé
   d'office. Ne jamais mélanger les deux dans un même fichier : c'est ainsi qu'un « TODO » atteint
   1 300 lignes dont 100 tâches finies.
3. **Chargé toujours, ou lu à la demande.** Au démarrage : les règles du projet (≤ 150 lignes),
   l'état (≤ 60 lignes), et rien d'autre. Un gros document se lit par son sommaire
   (`grep -n '^## '`) puis la section voulue — jamais en entier pour trouver un fait.
4. **Une tâche = une session.** Reprendre depuis les fichiers, faire une tâche, consigner, puis
   repartir à zéro. Une compaction en pleine tâche est un accident à éviter, pas une fatalité.
5. **Une décision se consigne au moment où elle est validée**, avant ou avec le code qui
   l'applique — avec la date, la formulation de celui qui tranche, le pourquoi, et **ce qui a
   été écarté**. Une décision ne rend aucun fichier faux, donc rien ne la réclame : c'est le seul
   fichier dont l'oubli ne se voit pas.
6. **Une décision prise par l'agent seul se consigne aussi**, marquée comme telle, et se passe en
   revue en fin de chantier. Ce que l'agent décide en construisant n'est pas moins structurant
   que ce que l'utilisateur tranche ; c'est seulement moins visible.
7. **La discipline tient par l'outil, pas par la volonté.** Une règle écrite trois fois a été
   oubliée deux fois en six jours. Ce qui doit arriver à coup sûr se fait par un automatisme ou
   une commande, pas par une consigne.
8. **Mesurer avant de changer la méthode.** La taille du contexte par échange, le nombre de
   réécritures de l'état, les tâches qui sortent des chantiers : les chiffres existent dans les
   journaux de session, il suffit de les lire.

---

## 2. Les fichiers

Tout vit **dans le dépôt du projet**, à côté du code, parce qu'une documentation qui vit ailleurs
dérive sans qu'on le voie. Un coffre de notes personnel (Obsidian ou autre) convient aux idées et
aux leçons transversales — par lien vers le dépôt, jamais par copie.

| Fichier | Il répond à | Qui l'écrit, quand | Chargé au démarrage | Taille |
|---|---|---|---|---|
| `CLAUDE.md` (ou `AGENTS.md`) | Comment on travaille ici : sommaire des documents, commandes, règles qui s'écartent des défauts, pièges les plus coûteux, limites | l'agent propose, l'utilisateur arbitre ; change rarement | **oui** | ≤ 150 lignes |
| `ETAT.md` | Où on en est, la prochaine action, ce qui attend une réponse | l'agent, **réécrit** à chaque point d'étape | **oui** (automatisme) | ≤ 60 lignes |
| `TODO.md` | Le sommaire du reste à faire : un chantier par ligne, sa **priorité** (1 maintenant, 2 ensuite, 3 un jour) et son compte | l'agent, au point d'étape ; l'utilisateur donne la priorité | non | ≤ 50 lignes |
| `docs/chantiers/<nom>.md` | Les tâches validées d'un chantier — un but, un « fini quand » ; une tâche faite **se retire** ; une tâche peut porter `[P1]`-`[P3]` | l'agent, quand l'utilisateur valide | non, un seul à la fois | sans limite |
| `docs/chantiers/divers.md` | Les petites tâches sans famille, chacune avec sa marque de priorité ; trois qui parlent de la même chose deviennent un chantier | l'agent, « ajoute-le à la todo » | non | sans limite |
| `docs/decisions.md` | Pourquoi c'est ainsi, et ce qui a été écarté | l'agent, **à la validation** | non — par son sommaire | sans limite, s'ajoute |
| `docs/pieges.md` | Les surprises qui ont coûté cher, et comment les détecter | l'agent, dans le commit qui les règle | non — par sujet | sans limite |
| `docs/modele.md` (ou équivalent) | Comment ça marche aujourd'hui | l'agent, **dans le commit qui le rend faux** | non | sans limite, se réécrit |
| `docs/archives/` | Tâches closes, journaux des mois passés, anciens états | l'agent, par script contrôlé | jamais | — |
| `git` | L'histoire : chaque commit dit ce qui change et pourquoi | à chaque point d'étape | — | — |

Trois compléments selon le projet :

- **Un journal** (`JOURNAL.md`, une entrée par jour de travail, mois courant seulement) quand
  le « comment on y est arrivés » a de la valeur : diagnostics, essais ratés, matériel. Il dit ce
  que git explique mal ; il ne raconte pas les modifications de fichiers.
- **Une copie en lecture de ce qui tourne ailleurs** (`config/` tirée d'un serveur par script,
  jamais éditée à la main) quand le projet configure une machine : on versionne ce qui est
  réellement actif, et « présent dans git » cesse de vouloir dire « actif ».
- **Une commande de vérification unique** (`tests/tout.py`, `verifier.py`) : c'est la première
  étape du point d'étape, et elle doit exister avant tout le reste. Quand elle grossit, elle
  **retient l'empreinte de ce qu'elle lit après un passage au vert, et ne relance pas un code
  inchangé** : la plupart des points d'étape suivent une simple modification de documentation, ou
  une vérification lancée quelques minutes plus tôt. Elle lance ses fichiers en parallèle quand
  ils ne partagent rien. Ne relancer que les tests « concernés » par un changement est écarté :
  une correspondance oubliée laisse passer une erreur sans bruit.

Ce que les fichiers ne portent **jamais** : des données personnelles dans un fichier versionné
(un identifiant à la place d'un nom), des secrets (un `.gitignore` strict, vérifié avant le
premier commit), et de la prose là où un test ferait l'affaire — une règle métier vit dans un
test nommé, pas dans un paragraphe. Deux corollaires appris en deux semaines : **un fichier chargé
à chaque démarrage ne porte pas d'historique** (une liste de sauvegardes, un journal — c'est une
règle de plus qui coûte des jetons à chaque session sans en être une) ; et **ce qui ne doit
jamais être versionné se vérifie par un outil au point d'étape**, pas par une consigne : une règle
de prose contre un réflexe perd, treize fois sur quatre fichiers en dix jours.

### Ce qui ne doit pas être dans `ETAT.md`

Parce qu'il est **remplacé** et jamais complété, tout ce qui n'y vit *que* là finit par en
sortir sans avoir été rangé. Deux semaines de pratique ont montré les dérives : des pièges
durables (→ `pieges.md`), des questions ouvertes depuis dix jours (→ le chantier concerné),
trois « prochaines actions » (→ une seule, les autres dans les chantiers), des faits de
configuration (→ le document du sujet). `ETAT.md` dit où on en est ; il ne stocke rien.

---

## 3. Les rituels

### Les mots, d'abord

Huit choses se ressemblent et ne se tiennent pas au même niveau. Les confondre coûte des
résultats écrasés et des dossiers rangés au mauvais endroit.

| | Ce que c'est | Ce qui lui appartient | Combien de temps ça vit |
|---|---|---|---|
| **Projet** | un dossier, et d'ordinaire un dépôt git | `CLAUDE.md`, `ETAT.md`, le registre, les chantiers, la mémoire automatique de l'agent — tout ce que l'agent reçoit au démarrage dépend du dossier où la session s'ouvre | des mois |
| **Branche** | une ligne de travail dans le dépôt — un chantier | ses commits | jusqu'à la fusion |
| **Copie de travail** (*worktree*) | un **second dossier sur le même dépôt**, où une autre branche est sortie, pour que deux sessions travaillent en parallèle sans se marcher sur les fichiers | sa branche ; sa propre mémoire automatique (c'est un dossier) ; son propre état si c'est un outil à part (`docs/<outil>/ETAT.md`) — **pas de `CLAUDE.md` ni de registre à elle** : ce sont ceux du projet | le temps d'un chantier, ou d'un outil mené en parallèle |
| **Session** (conversation) | un fil d'échanges avec l'agent, ouvert dans un dossier | son contexte, qui grossit à chaque échange | une tâche |
| **Fork** | une copie d'une session à un instant donné, **avec tout son contexte** | le même dossier, la même branche | pour explorer une piste sans perdre le fil principal ; coûte autant que l'original, et porte le même contexte lourd |
| **Session annexe** | une session **neuve**, lancée pour une tâche délimitée — souvent dans une copie de travail | un contexte vide, une consigne qui dit où elle rend ; son état en tête de son chantier | une tâche ; elle rend par un commit et un message d'une ligne, et ne touche pas à l'état de la principale |
| **Sous-agent** | un assistant invisible à l'intérieur d'une session, qui lit beaucoup et ne rend qu'un résumé | rien : il ne laisse aucune trace, n'écrit dans aucun fichier de suivi | quelques minutes ; pour explorer, jamais pour décider |
| **Compaction** | le résumé automatique quand le contexte d'une session est plein | ce qui est sur le disque ; ce qui n'a été que dit disparaît | c'est ce qu'« une tâche = une session » évite |

Trois conséquences :

- **Une copie de travail n'est pas un projet, même rangée parmi les projets.** Elle n'a pas de
  `CLAUDE.md` à elle (elle porte celui du dépôt, par la branche), ni de registre à elle : une
  décision prise dans la copie s'écrit dans le registre du projet — ou dans `docs/<outil>/`
  quand le dépôt porte deux outils. Ce qui lui appartient en propre, c'est sa branche et son
  état. Deux outils menés en parallèle dans un même dépôt (une application et son module de
  calcul, par exemple) restent **un projet** : le second lit les données du premier, et c'est
  pour ça qu'on ne les sépare pas en deux dépôts.
- **Un fork n'est pas une session annexe.** Le fork hérite d'un contexte lourd et travaille sur
  la même branche : il sert à bifurquer une réflexion, pas à paralléliser du travail. La session
  annexe part de zéro et d'une branche à elle : c'est elle qui parallélise.
- **Un sous-agent ne consigne rien.** Ce qu'il trouve et qui compte, la session qui l'a lancé
  l'écrit au bon endroit.

### Avant tout : questions, puis plan, puis exécution

Une demande nouvelle commence par les questions de l'agent s'il en a, puis sa compréhension et
son plan, puis l'exécution après le oui de l'utilisateur — pour tout ce qui lance une tâche ou
un chantier, ou change une règle, un outil, la structure. En direct, sans plan : une retouche
dans le périmètre de la tâche en cours, « ajoute-le à la todo », une question. Deux mots pour
forcer l'un ou l'autre : **« plan »** en tête de message impose l'étape, **« direct »** la saute.
Une fois le oui donné, l'agent enchaîne sans s'arrêter pour annoncer.

### `/reprendre` — en début de session, pour continuer

1. **Qui suis-je** : la principale, ou une session annexe ? L'application le sait (le titre, la
   session parente) ; sinon, l'utilisateur. Une session annexe a son état en tête de son
   chantier, pas dans `ETAT.md`.
2. L'état a été injecté au démarrage par l'automatisme : ne pas le relire. Dans une session
   annexe, lire le bloc « Où en est la session » de son chantier. Un état modifié et non commité
   est en cours d'écriture par une autre session : ne pas s'y fier pour choisir la tâche.
3. `git status --short` et `git log -5 --oneline`. Du travail non commité signale une session
   interrompue : le dire avant tout, sans y toucher.
4. **Vérifier une ou deux affirmations de l'état contre les fichiers.** Un état n'est qu'un
   instantané : la prochaine action n'est-elle pas déjà faite ? Une question en attente n'a-t-elle
   pas reçu sa réponse ?
5. Choisir **une seule tâche** — celle que l'utilisateur demande, sinon la prochaine action **de
   son état**, jamais celle de la principale depuis une session annexe — et ouvrir uniquement
   les documents qu'elle demande.
6. Rendre compte en huit lignes : qui on est, où on en est, la tâche, ce qu'on va lire, **comment
   on saura qu'elle est finie**, ce qui attend une réponse. Puis enchaîner.

### `/tache` — trier une tâche nouvelle avant de la lancer

`/reprendre` continue le chantier en cours ; `/tache <description>` prend une tâche nouvelle, à
n'importe quel moment, et choisit **où** elle s'exécute. Sans description, il propose la tâche
suivante d'après l'état et les priorités. Quatre temps :

1. **Comprendre** : la tâche en deux lignes, et « fini quand ».
2. **Les questions que l'état ne tranche pas**, à cocher : mêmes fichiers que le chantier en
   cours ? besoin de ce qui a été dit ici ? livrable par un commit sans arbitrage ? la principale
   doit-elle continuer ? besoin des fichiers non commités ou ignorés par git ?
3. **L'avis et l'environnement**, avec la raison :

   | Si la tâche… | Environnement |
   |---|---|
   | prolonge ce qu'on fait, mêmes fichiers, contexte utile | session courante |
   | est indépendante et le contexte actuel ne lui sert pas | nouvelle session |
   | peut tourner en parallèle, autres fichiers, livrable par un commit sans arbitrage | session annexe dans une copie de travail |
   | est une enquête dont seul le résumé compte | sous-agent |
   | a besoin de tout ce qui vient d'être dit pour explorer une autre piste | fork — rare |

4. **Lancer, avec l'accord** : enchaîner ; ou le point d'étape, proposé puis lancé sur le oui,
   avec la tâche comme prochaine action, puis `/clear` et `/reprendre` ; ou une consigne écrite
   (quoi, où ça rend, ce qu'elle ne touche pas, qui prévenir) et une session annexe que
   **l'utilisateur ouvre lui-même** — dans Claude Code, une pastille déposée par l'agent, un
   clic ; ou un sous-agent ; ou un fork que l'utilisateur fait dans son outil.

Une session annexe ouverte dans une copie de travail neuve ne voit ni les fichiers non commités
ni ceux que git ignore : pour une enquête sur des données locales, c'est un sous-agent.

### `/checkpoint` — le point d'étape

Après une décision validée, un diagnostic coûteux ou une étape vérifiée — pas seulement en fin
de tâche. « Fin de session » est un mauvais déclencheur : on est interrompu, on atteint une
limite, on ferme la fenêtre.

**Qui le lance** : l'utilisateur ; ou l'agent, après l'avoir proposé et reçu un oui explicite —
jamais de lui-même, et jamais en suivant les étapes à la main à la place de la commande :
l'utilisateur ne sait alors plus s'il lui reste une commande à lancer. Avant de proposer
`/clear`, l'agent propose d'abord le point d'étape.

1. **Vérifier** : la commande de tests ou de contrôles du projet. En échec, s'arrêter et le dire.
   Si elle répond que ce code est déjà passé au vert, la croire.
2. **Relire le diff.**
3. **Les décisions** validées depuis le dernier point d'étape : vérifier qu'elles sont au
   registre ; écrire ce qui manque, avec ce qui a été écarté. Marquer celles que l'agent a
   prises seul.
4. **La documentation devenue fausse** avec ce travail.
5. **Les autres sessions et les branches** : ce que d'autres sessions ont livré depuis la
   dernière version de l'état (`git log --all --since=<date de l'état>`) s'intègre, sans rien
   écraser qu'on n'a pas lu ; chaque branche non fusionnée et chaque travail confié ailleurs a
   sa ligne dans l'état, avec **où le résultat doit arriver**.
6. **Ranger, puis réécrire `ETAT.md`** en le remplaçant. D'abord sortir ce qui n'y a pas sa
   place : un piège durable → `pieges.md`, une question de plus d'une semaine → son chantier,
   une recette → le document du sujet, une règle → `CLAUDE.md`. Puis écrire : l'objectif et
   « Fini quand », une **seule** prochaine action, ce qui attend une réponse. **Compter les
   lignes avant le commit**, pas après. L'heure vérifiée par une commande ; aucun nom de
   personne.
7. **Le reste à faire** : retirer ce qui est fait, ajouter ce qui a été validé ; un script
   (`chantiers.py`) met à jour les comptes du sommaire et marque « dort depuis le … » tout
   chantier sans mouvement depuis un mois ; un chantier à zéro part en archive.
8. **Si le travail ferme un chantier** : les entrées **[décision de l'agent, à revoir]** de ce
   chantier sont soumises à l'utilisateur ; la marque tombe sur celles qu'il confirme.
9. **Commit** cohérent, message qui dit ce qui change et pourquoi. Ne pas pousser sans accord.
10. Rendre compte en six lignes. Si la tâche est finie : c'est le moment de `/clear`.

Ce que le projet ajoute — sa commande de vérification, ses fichiers à relire, le retirage de
sa copie de configuration — est listé dans **son** `CLAUDE.md`, section « Point d'étape ».

### `/clear` — repartir des fichiers

Après le point d'étape d'une tâche terminée. **Pas** entre une question posée et le chantier
qu'elle ouvre : une tâche ne se coupe pas à un arbitrage. Pas non plus avant d'avoir intégré le
résultat d'une session annexe qu'on attend.

### Livrer par branche quand l'utilisateur veut essayer avant d'accepter

Née sur le terrain, pas dans le plan : sur le projet métier, 35 branches fusionnées en dix
jours sans perte sur les vraies données. Le cycle :

1. une branche par chantier, dans une copie de travail (*worktree*) pour ne pas gêner la
   session principale ;
2. une copie des vraies données, et un serveur d'essai sur un autre port, **laissé à
   l'utilisateur** le temps qu'il essaie ;
3. son feu vert, consigné au registre comme une décision ;
4. la fusion, puis une sauvegarde de référence, puis la migration des vraies données avec une
   photographie avant/après qui doit être identique hors du changement attendu ;
5. le point d'étape.

Deux pièges appris : une copie de travail n'a pas les fichiers ignorés par git — un outil y
rend un résultat faux sans erreur ; et sur une copie, on **vide** une voie d'envoi (courriel,
jeton), on ne la déconnecte pas, sinon c'est le jeton de l'application réelle qui est révoqué.

### Plusieurs sessions sur un même projet

Parallèliser est utile (une enquête, une récupération de données, un essai sur une branche) et
dangereux : un résultat livré par une session annexe a été écrasé par le point d'étape de la
principale, qui l'attendait encore. Les règles qui en sont sorties :

- **Un seul rédacteur de `ETAT.md`** : la session qui porte le chantier. Une session annexe ne
  touche ni à l'état ni à la branche d'une session en cours ; son résultat va dans **son**
  commit, et dans le registre si quelque chose a été tranché.
- **Une tâche confiée dit où elle rend** : le texte qui lance une autre session nomme l'endroit
  du résultat, ce qu'elle ne touche pas, et la session à prévenir.
- **En fin de tâche, la session annexe prévient la principale** en une ligne — « livré : commit X
  sur la branche Y ». Le message signale ; le fichier fait foi.
- **Une session annexe a son état en tête de son chantier** — bloc « Où en est la session » :
  copie, branche, port, **une seule** prochaine action, fini quand —, réécrit à son point
  d'étape. Après un `/clear`, c'est là qu'elle reprend, et `/reprendre` commence par demander
  qui il est : le démarrage n'injecte que l'état du dossier, celui de la principale. Vu le
  04/11 : une session annexe relancée a repris la prochaine action de la principale, puis une
  étape que la principale avait résumée de travers.
- **La ligne envoyée à la principale est complète** (chantier, commit, prochaine action) et se
  colle telle quelle sous « Des sessions » de l'état, au point d'étape de la principale — pas en
  pleine tâche, une autre session peut relire l'état à cet instant.
- **Un projet = un dossier.** Ce que l'agent reçoit au démarrage (règles, état, mémoire) dépend
  du dossier où la session s'ouvre, jamais d'un regroupement d'affichage. Toutes les sessions
  d'un projet s'ouvrent dans son dossier — pas dans un sous-dossier, qui aurait sa propre mémoire.

### Un dépôt, plusieurs outils menés en parallèle

Quand une application grandit en plusieurs outils qui partagent la même base, les séparer en
dépôts obligerait à recopier les données de l'un dans l'autre. On garde donc un seul dépôt, mais
**chaque outil mené en parallèle a sa copie de travail et son état** :

- une copie de travail par outil (`git worktree`), **à côté** du dossier principal et non
  dedans, sur une branche qui porte le nom de l'outil (`<outil>`, ou `<outil>-…` pour une
  branche courte) ; ses sessions s'ouvrent là, et son serveur d'essai a son propre port ;
- **un état par outil** : `docs/<outil>/ETAT.md`, que l'automatisme affiche dans cette copie à la
  place d'`ETAT.md`. Deux rédacteurs d'un même état rejoueraient l'écrasement décrit plus haut ;
- **un registre et des documents par outil** (`docs/<outil>/`) : deux sessions qui ajoutent en
  même temps en tête du même registre se heurtent à chaque fusion ;
- **une règle de fusion** : avant de fusionner dans la branche principale, relire ce que l'autre
  outil y a fusionné ; la session qui fusionne relance ce qui tourne et prévient l'autre.

---

## 4. Les automatismes

Trois scripts en Python, pour tourner tels quels sous Windows, inactifs dans tout dossier sans
`ETAT.md`, et incapables de bloquer une session (code de sortie 0 quoi qu'il arrive ; le seul
« blocage » est celui d'une fin de tour, une fois, le temps d'une phrase). Leur source est dans
`outils/hooks/` ; `outils/installer.py` les branche.

| Quand | Quoi | Pourquoi |
|---|---|---|
| Au démarrage, après `/clear` et **après une compaction** | injecte `ETAT.md` — ou `docs/<outil>/ETAT.md` dans la copie de travail d'un outil —, `git status`, les trois derniers commits et les branches non fusionnées ; avertit si l'état dépasse 60 lignes | c'est la seule chose qui survive à coup sûr à un résumé automatique |
| À chaque message, quand le contexte de la conversation dépasse **300 000 jetons** | une alerte : « proposer un point d'étape puis `/clear` dès que l'étape est vérifiée » — répétée seulement quand le contexte a encore grossi de 150 000 | c'est là que les sessions dérapaient : 13 sur 58 au-delà de 600 000 jetons, sans rien pour le dire |
| **À la fin d'un tour**, au-dessus de 300 000 jetons | Claude continue une fois, pour proposer le point d'étape avant de rendre la main — une fois par niveau de contexte et par tâche ; l'alerte du message suivant se tait alors pour ce niveau | la fin du tour est le dernier instant où l'utilisateur est là ; la compaction d'absence vient environ 55 minutes plus tard (08/11) |
| **Juste avant toute compaction** | dicte au résumé ce qu'il doit garder, **à la place de son plan par défaut** : six sections, en français, sans extrait de code — qui est la session, la tâche et son « fini quand », la prochaine action, les décisions validées non consignées, les questions en attente, les fichiers non commités ; et ce qu'il ne doit pas recopier : les règles de `CLAUDE.md` et l'état, qui reviennent d'eux-mêmes. Chaque appel laisse une ligne dans un journal hors dépôt (`~/.claude/memoire_projet/compactions.jsonl`) | le résumé s'écrivait sans consigne ; après lui, seuls `CLAUDE.md` et l'état reviennent d'eux-mêmes (08/11). Au premier test, le résumé suivait les six points mais recopiait huit lignes de règles : l'interdit est devenu explicite (08/11). À la première compaction d'absence observée, les résumés gardaient la grille par défaut en neuf sections, l'un en anglais, l'un sans trace de la consigne : elle remplace désormais le plan au lieu de s'y ajouter, et le journal dit si elle a été émise (08/11 au soir) |
| Quand l'utilisateur envoie un message qui ressemble à une validation (« ok », « d'accord », « 1. … »), et après une réponse à une question à choix | un rappel : « si un arbitrage vient d'être tranché, le registre d'abord » — **une fois par tâche**, puis seulement si huit validations ont passé sans que le registre bouge ; un `/checkpoint` remet le compteur | vise exactement l'oubli observé, sans bruit : la première version se déclenchait treize fois par session |
| Au démarrage, en arrière-plan | archive chaque conversation en Markdown lisible — messages et réponses seulement, ~2 % du poids brut | la mémoire de dernier recours (voir ci-dessous) |
| À la demande | mesure la taille du contexte par échange, par projet, depuis une date | pour savoir si la méthode tient, chiffres à l'appui |

Un réglage s'y ajoute, posé par le même installeur : la **compaction d'absence** de Claude Code,
qui résume une session restée sans échange une heure environ, ne touche une session qu'au-delà de
**300 000 jetons** — le seuil où l'alerte ci-dessus a déjà réclamé un point d'étape. En dessous,
la session garde son contexte entier pendant l'absence ; au-dessus, elle avait été prévenue.
Mesuré du 1er au 8 novembre sur cinq projets : 38 compactions, toutes pendant une absence, aucune
à fenêtre pleine, 18 sous ce seuil. Observé le soir du réglage, sur quatre compactions : toutes
au-dessus du seuil ; le résumé s'écrit environ 55 minutes après la fin du dernier tour et ne
s'applique qu'au message suivant de l'utilisateur — un `/clear` avant ce message le perd, sans
dégât.

Et un réglage : la conservation des journaux de session portée à dix ans (`cleanupPeriodDays`),
pour qu'aucune conversation ne soit purgée.

**Les conversations passées sont une mémoire de dernier recours, sur demande seulement.** Elles
ne se lisent jamais en début de session ni par réflexe, jamais à la place des fichiers du projet.
On localise d'abord (recherche plein texte), puis on lit le seul passage utile — et ce qu'on y
retrouve et qui compte se consigne aussitôt au bon endroit. Premier usage réel : une décision
datée du jour de sa consignation au registre a retrouvé sa vraie date, trois jours plus tôt.

**Ce que les automatismes ne font pas** : fabriquer des souvenirs. Un script n'a pas accès au
raisonnement ; il rappelle, il injecte, il archive. La synthèse reste le travail de l'agent au
point d'étape, et c'est pour ça que le point d'étape est une commande et pas un hook.

---

## 5. Mettre un projet en route

### Un projet neuf

`/nouveau-projet <dossier>` fait les quatre premières étapes : il pose les questions de départ,
copie les gabarits là où rien n'existe, crée git et un `.gitignore` de départ, remplit ce que les
réponses permettent. À la main, c'est :

1. Copier `gabarits/` à la racine : `CLAUDE.md`, `ETAT.md`, `TODO.md`, `docs/decisions.md`,
   `docs/pieges.md`, `docs/chantiers/GABARIT.md`. Remplacer les « guillemets », rien inventer.
2. `git init`, et un `.gitignore` écrit **avant** le premier commit : secrets, données
   personnelles, fichiers volumineux ou régénérables, copies de sauvegarde faites à la main.
3. Une commande de vérification, même minimale, dès le premier jour.
4. Première session : `/reprendre`, qui trouvera un état presque vide et proposera de le remplir.

### Un projet qui existe déjà, avec une conversation-fleuve

1. **Fermer la conversation proprement** : lui demander un dernier point d'étape complet — tout
   ce qui n'est pas encore dans les fichiers, le travail en cours, les décisions et leur pourquoi,
   les pièges, ce qu'elle ferait ensuite. Puis ne plus la rouvrir.
2. **Git d'abord**, en choisissant les fichiers un par un ; chercher les secrets dans tout ce
   qui sera suivi.
3. **Créer `CLAUDE.md` et `ETAT.md`** à partir de ce qui existe, sans rien inventer.
4. **Éclater ce qui est trop gros par script, avec un contrôle de conservation** : toute ligne
   lue doit atterrir exactement une fois (chantier, document du sujet, ou archive), sinon le
   script échoue et rien n'est écrit. Les tâches closes partent en archive mot pour mot ; ce
   qu'on ne sait pas classer reste dans une archive marquée « non triée ». Ne jamais confier ce
   tri à un résumé.
5. **Remonter les règles valables partout** dans le fichier d'instructions global de l'agent :
   celles qui ne vivaient que dans un projet, ou que dans sa mémoire automatique.
6. Vérifier : une session neuve, `/reprendre`, et elle doit savoir quoi faire sans récit oral.

### Les règles globales

Un fichier d'instructions global (≤ 60 lignes) porte ce qui vaut pour tous les projets : la
langue, la façon de travailler avec cette personne, la méthode elle-même. Les règles propres à un
projet n'y sont pas. Les deux fichiers sont lus à chaque démarrage, donc chaque ligne doit mériter
sa place : « la retirer ferait-elle commettre une erreur ? » `gabarits/CLAUDE-global.md` en donne
une version de départ ; l'installeur la pose seulement si le fichier n'existe pas encore, et ne
touche jamais à un fichier déjà là — il appartient à l'utilisateur.

---

## 6. Ce qui a été écarté, et pourquoi

| Écarté | Pourquoi |
|---|---|
| Le coffre de notes (Obsidian) comme mémoire du projet | Ce n'est pas le lieu qui compte, c'est la granularité et le point d'entrée ; et une documentation qui ne vit pas à côté du code dérive en silence |
| Un fichier par décision (ADR) | Un registre unique marche, il lui fallait un mode de lecture : son sommaire par `grep` |
| Un index généré en tête du registre | Il faudrait le régénérer, donc il dériverait |
| Les mémoires vectorielles ou en graphe (serveurs MCP de mémoire) | Surdimensionnées pour une personne ; dans un test publié, un agent limité aux fichiers faisait mieux |
| Le « Memory Bank » en six fichiers | Deux d'entre eux recopient ce que le code dit déjà |
| Les cadres de spécification lourds (Spec Kit, BMAD) | « Un marteau-pilon pour une noix » ; une mini-spécification de six lignes suffit quand il y a une ambiguïté métier |
| Les équipes d'agents permanentes | Sept fois plus de jetons ; un agent principal et un relecteur ponctuel suffisent |
| Recopier la conversation entière dans un fichier au point d'étape | 100 Mo dont 98 % de sorties d'outils ; la relire retomberait dans le problème ; et elle porte des données personnelles. L'archive lisible, à part, sur demande, couvre le besoin |
| Automatiser les hooks seulement après avoir observé des oublis | L'oubli était déjà observé deux fois ; attendre coûtait des décisions |

---

## 7. Retour d'expérience après deux semaines

Sur les deux projets lourds, mesuré dans les journaux de session :

| | Domotique | Projet métier |
|---|---|---|
| Sessions en 13 jours | 10 | 58 |
| Contexte médian par échange | 531 000 → **224 000** | 515 000 → **316 000** |
| Échanges au-delà de 300 000 jetons | 76 % → **27 %** | 76 % → **53 %** |
| Sessions commençant par `/reprendre` | 8/10 | 52/58 |
| État injecté automatiquement au démarrage | 9/10 | 58/58 |
| Décisions consignées, avec « écarté » | 25, dont 22 avec « écarté » | 140, dont 105 avec « écarté » ; 140 commitées le jour même |
| Points d'étape | 12 | 70 |
| Dont choix de l'agent seul, consignés comme tels | 0 (dans le journal seulement) | 33 entrées (24 %), 36 revus en une séance |

Et sept autres projets ont repris le gabarit en une semaine, sans qu'on le leur demande projet
par projet : la méthode se copie.

**Ce qui marche.** La reprise depuis les fichiers, sans récit oral. Le registre tenu au fil de
l'eau, avec ce qui a été écarté. L'état réécrit à chaque point d'étape. La copie de configuration
qui détecte ce qui a changé hors session. L'archive des conversations, qui a déjà corrigé une
date. Les règles multi-sessions, nées d'un incident et respectées depuis.

**Ce qui ne marche pas encore, et ce qu'on change.**

1. **La session reste longue quand la tâche est un chantier entier.** Sur le projet métier, 13
   sessions sur 58 ont dépassé 600 000 jetons ; le point d'étape vient en fin de chantier, pas
   après chaque étape vérifiée. Le remède n'est pas une règle de plus : c'est de découper le
   chantier en étapes qui ont chacune un critère de fin, et de faire le point d'étape à
   chacune — l'automatisme d'injection peut aussi **avertir quand le contexte dépasse un seuil**.
2. **`ETAT.md` devient un fourre-tout** : trois prochaines actions, neuf questions dont quatre
   n'existent qu'ici, des pièges durables. Le gabarit dit maintenant explicitement ce qui n'y va
   pas, et le point d'étape range avant de réécrire.
3. **Les chantiers ne se vident pas.** Sur la domotique, +6 tâches ouvertes en deux semaines et
   quatre chantiers sur sept immobiles. Ce n'est pas un défaut de méthode, c'est une information :
   le sommaire doit dire quels chantiers vivent et lesquels dorment, et un chantier qui dort
   depuis un mois se ferme ou s'archive.
4. **Le rappel automatique est trop bavard** : treize à dix-huit par session, sur chaque « ok ».
   À rendre plus rare — une fois par tâche, ou seulement si le registre n'a pas bougé depuis.
5. **Les décisions prises par l'agent seul n'étaient pas marquées.** Sur le projet métier, elles
   existent (« arbitrage pris en construisant, à valider ») mais rien ne les distingue ; d'où la
   marque **[décision de l'agent, à revoir]** du gabarit et la revue en fin de chantier.
6. **Les noms dérivent d'un projet à l'autre** quand chacun copie le gabarit de mémoire :
   `decisions.md`, `DECISIONS.md`, `historique.md` pour le même rôle. Le gabarit fixe les noms ;
   un projet qui s'en écarte le dit dans son `CLAUDE.md`.
7. **La limite de 60 lignes est corrigée après coup**, pas avant le commit : le point d'étape
   compte les lignes avant d'écrire.

Ces sept changements sont dans les outils depuis le 18/10/2026 : `/checkpoint` en version 2,
l'automatisme revu (alerte de contexte, rappel limité), `chantiers.py`, `/nouveau-projet`, et
le gabarit d'`ETAT.md`. La prochaine mesure dira s'ils tiennent.

---

## 8. Avec un autre agent que Claude Code

Les fichiers ne changent pas. Ce qui change, c'est le nom du fichier d'instructions (`AGENTS.md`
pour Codex, Cursor et la plupart des autres ; `CLAUDE.md` est lu par Claude Code, qui lit aussi
`AGENTS.md`) et la façon de brancher les automatismes : les commandes `/reprendre` et
`/checkpoint` sont du texte, elles se recopient dans n'importe quel système de commandes ou de
règles ; l'injection de l'état au démarrage devient, à défaut de hook, la première ligne du
fichier d'instructions : « lis `ETAT.md` avant tout ». La mesure se fait sur les journaux que
l'outil conserve, s'il en conserve.

---

## Annexes

- `gabarits/` — les sept fichiers à copier dans un projet neuf, et le gabarit des règles globales.
- `outils/` — les quatre commandes (`/reprendre`, `/tache`, `/checkpoint`, `/nouveau-projet`),
  les trois automatismes, et `installer.py` qui les met en place dans Claude Code ; ce dossier
  est leur source, `installer.py --verifier` dit si l'installé a dérivé. Un automatisme qui
  n'est pas de la méthode (propre à une machine ou à une maison) ne s'installe que si son script
  est présent à côté des autres : la part publiée n'en porte pas. `publier.py` pousse cette part
  — ce fichier, `gabarits/`, `outils/` et un texte d'accueil — dans un dépôt public, dont le
  README dit comment l'installer d'un prompt collé dans Claude Code ; la source reste privée.
- `bilans/` — l'application sur les projets réels, chiffres et incidents datés.
- `docs/decisions.md` — les arbitrages sur la méthode elle-même, depuis le 18/10/2026.
