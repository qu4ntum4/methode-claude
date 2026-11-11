# Tenir un projet de longue haleine avec Claude Code

Un projet mené sur des semaines avec Claude Code perd son fil à chaque nouvelle conversation : ce
qui a été décidé, pourquoi, où on en est. La méthode met tout ce qui compte **dans des fichiers du
projet, jamais dans la conversation** : un `CLAUDE.md` court (les règles), un `ETAT.md` de moins
de 60 lignes (où on en est, la prochaine action), un reste à faire découpé par chantier, un
registre des décisions et un carnet des pièges. **Une tâche = une session** : on reprend, on
travaille, on fait le point, on repart d'une conversation vide. Des automatismes affichent l'état
au démarrage, avertissent quand la conversation devient trop longue et rappellent de noter une
décision. Tout est expliqué dans [`METHODE.md`](METHODE.md) ; les fichiers à copier dans un projet
sont dans [`gabarits/`](gabarits/).

## Les quatre commandes

| Commande | Quand | Ce qu'elle fait |
|---|---|---|
| `/nouveau-projet <dossier>` | une fois, au départ d'un projet | pose les questions de départ, copie les gabarits là où rien n'existe, crée git |
| `/reprendre` | en début de chaque session | lit l'état, vérifie git, choisit **une** tâche et dit comment on saura qu'elle est finie |
| `/tache <description>` | pour une tâche nouvelle | la comprend, pose les questions que l'état ne tranche pas, choisit où l'exécuter ; seule, propose la suivante |
| `/checkpoint` | après chaque étape vérifiée, et avant `/clear` | vérifie, consigne les décisions, réécrit l'état, tient le reste à faire, commite |

## Ce que l'installation pose sur votre machine

- **`Documents\Claude\methode-claude`** : la copie de ce dépôt. Les automatismes la lisent sur
  place : ne pas la déplacer ni la supprimer.
- **`~/.claude/skills/`** (le dossier des commandes de Claude Code, dans votre profil) : les
  quatre commandes.
- **`~/.claude/settings.json`** (les réglages de Claude Code) : les automatismes — l'état du
  projet affiché au démarrage, l'alerte quand la conversation dépasse 300 000 jetons, le rappel
  de consigner une décision, la consigne donnée au résumé automatique, l'archivage lisible des
  conversations —, la conservation des conversations portée à dix ans, et le seuil du résumé
  d'absence. Une copie `settings.json.avant-installation` est prise avant la première
  modification ; vos autres réglages sont gardés.
- **`~/.claude/CLAUDE.md`** (vos instructions valables dans tous les projets) : posé depuis un
  gabarit **seulement si ce fichier n'existe pas encore**. S'il existe, il n'est pas touché.
- **`Documents\Claude\archives-conversations\`** : l'archive lisible de vos conversations, créée
  au premier démarrage qui suit, hors de tout dépôt.

Les scripts sont en Python et tournent tels quels sous Windows ; ils ne bloquent jamais une
session.

## Installer

Il faut Windows et l'application Claude avec son onglet **Code** (Claude Code). Git et Python 3
sont vérifiés par l'installation ; Python est installé s'il manque.

Ouvrez l'onglet Code de l'application Claude, dans n'importe quel dossier, et collez ce message :

```text
Installe sur ma machine la méthode de mémoire des projets publiée sur https://github.com/qu4ntum4/methode-claude. Fais-le dans cet ordre, en me disant à chaque étape ce que tu fais, et arrête-toi pour me demander si quelque chose ne se passe pas comme prévu.

1. Avant de toucher à quoi que ce soit, dis-moi ce qui va changer sur ma machine, puis attends mon accord :
   - un dossier Documents\Claude\methode-claude, dans mon profil Windows, qui recevra une copie du dépôt ;
   - le dossier des commandes de Claude Code, ~/.claude/skills/, qui recevra quatre commandes : /nouveau-projet, /reprendre, /tache et /checkpoint ;
   - le fichier de réglages de Claude Code, ~/.claude/settings.json, qui recevra les automatismes de la méthode (une copie « settings.json.avant-installation » est prise avant, et mes autres réglages sont gardés) ;
   - mes instructions générales, ~/.claude/CLAUDE.md, seulement si ce fichier n'existe pas encore ; s'il existe, il ne sera pas touché.
   Rien d'autre.

2. Vérifie que git et Python 3 sont installés : `git --version` et `python --version`. Si la réponse à python parle du Microsoft Store, ou dit que la commande est introuvable, Python manque : installe-le avec `winget install Python.Python.3.13`. Windows peut alors me demander une autorisation d'administrateur dans une fenêtre à part : préviens-moi. Si, après l'installation, `python` reste introuvable dans ta fenêtre, utilise `py -3` à sa place pour la suite (la commande py est installée avec Python) et dis-le-moi.

3. Récupère la méthode dans Documents\Claude\methode-claude :
   - avec git : crée le dossier Documents\Claude s'il manque, puis `git clone https://github.com/qu4ntum4/methode-claude` dedans ; si le dossier methode-claude existe déjà, fais plutôt `git pull` à l'intérieur ;
   - sans git : télécharge https://github.com/qu4ntum4/methode-claude/archive/refs/heads/main.zip, décompresse-le, et place le contenu du dossier methode-claude-main dans Documents\Claude\methode-claude.

4. Dans ce dossier, lance `python outils/installer.py` (ou `py -3 outils/installer.py`), puis `python outils/installer.py --verifier`, qui doit répondre « Tout est installé et au niveau de la source. » Montre-moi ces deux réponses telles quelles.

5. Dis-moi que les commandes et les automatismes seront visibles dans une nouvelle session, pas dans celle-ci. Puis explique-moi en quelques lignes la première chose à faire : ouvrir une session dans le dossier de mon projet (il peut être vide ou déjà plein) et taper /nouveau-projet suivi du chemin de ce dossier, ou /nouveau-projet tout seul pour le dossier courant ; et à quoi servent /reprendre, /tache et /checkpoint ensuite. Propose-moi de le faire sur un premier projet.
```

Après l'installation, ouvrez une **nouvelle session** : les commandes y sont. La première à essayer
est `/nouveau-projet <dossier de votre projet>`, puis, à chaque session suivante, `/reprendre`.

## Mettre à jour

Collez le même message : si le dossier `Documents\Claude\methode-claude` existe déjà, il est mis
à jour (`git pull`) et l'installation est relancée. À la main : dans ce dossier, `git pull` puis
`python outils/installer.py`.

## Désinstaller

Supprimer les quatre dossiers `nouveau-projet`, `reprendre`, `tache` et `checkpoint` dans
`~/.claude/skills/` ; remettre `~/.claude/settings.json` depuis `settings.json.avant-installation`
(ou en retirer les automatismes dont la commande contient `methode-claude`) ; supprimer le dossier
`Documents\Claude\methode-claude`. L'archive des conversations et vos projets ne sont pas touchés.

## Ce dépôt

Il est publié par un script depuis une source privée et ne s'édite pas à la main : une correction
se signale dans les *Issues*. Pas de licence pour l'instant : tous droits réservés.
