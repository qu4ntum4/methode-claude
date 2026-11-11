# Les outils de la méthode

**Ce dossier est la source.** Claude Code lit ses commandes dans `~/.claude/skills/` et ses
automatismes là où `~/.claude/settings.json` les désigne : `installer.py` fait le lien, et c'est
le seul exemplaire actif.

```
python installer.py              installe ou met à jour
python installer.py --verifier   dit ce qui diverge (code de sortie 1 s'il y a un écart)
python publier.py                publie la part partageable dans le dépôt public (voir plus bas)
python publier.py --verifier     dit ce qui changerait, et refuse si quelque chose de personnel traîne
```

| Fichier | Rôle | Une fois installé |
|---|---|---|
| `skills/reprendre/SKILL.md` | `/reprendre` : reprendre un projet en début de session | copié dans `~/.claude/skills/reprendre/` |
| `skills/tache/SKILL.md` | `/tache <description>` : trier une tâche nouvelle et choisir où elle s'exécute ; seul, propose la suivante | copié dans `~/.claude/skills/tache/` |
| `skills/checkpoint/SKILL.md` + `chantiers.py` | `/checkpoint` : le point d'étape ; le script tient les comptes du sommaire, l'ordre par priorité, et marque les chantiers qui dorment | copié dans `~/.claude/skills/checkpoint/` |
| `skills/nouveau-projet/SKILL.md` + `nouveau_projet.py` | `/nouveau-projet <dossier>` : poser les gabarits, les questions de départ, git | copié dans `~/.claude/skills/nouveau-projet/`, avec `../gabarits/` (sauf `CLAUDE-global.md`) |
| `../gabarits/CLAUDE-global.md` | les règles valables dans tous les projets, version de départ anonyme | posé dans `~/.claude/CLAUDE.md` **seulement s'il n'existe pas** ; sinon laissé tel quel, et l'installeur le dit |
| `hooks/memoire_projet.py` | injecte `ETAT.md` et l'état git au démarrage ; alerte quand le contexte dépasse 300 000 jetons, et fait proposer le point d'étape en fin de tour ; rappelle de consigner une décision, une fois par tâche ; avant toute compaction, dicte au résumé ce qu'il doit garder, à la place de son plan par défaut, et note chaque appel dans `~/.claude/memoire_projet/compactions.jsonl` (heure locale, session, déclencheur, taille de la consigne émise, erreur) | **appelé sur place** par `settings.json` |
| `hooks/archiver_conversations.py` | archive chaque conversation en Markdown lisible (mémoire de dernier recours) | appelé sur place, au démarrage, en arrière-plan |
| `hooks/signaler_sessions.py` | **ne fait pas partie de la méthode publiée** : ses automatismes ne se posent que si ce fichier est là, et `--verifier` suit la même règle (11/11). Capteur des sessions (chantier `tableau-claude`) : publie l'état de chaque session dans MQTT, `claude/<pc>/<session>`, pour Home Assistant, et dans `claude/<pc>/capteur` les outils lancés et les jetons du jour (`compteurs.json`) ; dans `claude/<pc>/usage`, les limites d'usage du compte, relevées au plus toutes les 15 minutes par Claude Code lancé sans interface, dans un processus détaché (`usage.json` ; il faut que Claude Code soit connecté hors de l'app, `claude auth status`) ; mémoire et réglages du courtier (`mqtt.txt`, mot de passe tapé par l'utilisateur) dans `~/.claude/tableau/`, erreurs dans `erreurs.log`. `--rejouer <relevé> [--mqtt <préfixe>]` rejoue un relevé de la sonde à blanc ; `--ecouter [filtre]` montre ce que garde le courtier ; `--effacer <préfixe>` vide un sujet d'essai ; `--usage` relève les limites tout de suite | appelé sur place, sur treize événements, en arrière-plan sauf à la fermeture (`SessionEnd`), où Claude Code l'attend |
| `hooks/mesurer_contexte.py` | mesure la taille du contexte par échange, pour vérifier que la méthode tient | à la main : `python hooks/mesurer_contexte.py <projet> --depuis AAAA-MM-JJ` |

Les commandes sont copiées parce que Claude Code ne les lit que dans `~/.claude/skills/` ; les
automatismes ne le sont pas. Après toute modification d'un skill ici, relancer `installer.py` —
le point d'étape de ce projet le vérifie.

Les scripts sont en Python pour tourner tels quels sous Windows ; ils ne bloquent jamais une
session (code de sortie 0 quoi qu'il arrive). `installer.py` écrit dans `settings.json` les
chemins de cette machine (`python.exe`, ce dossier) et le seuil de la compaction d'absence
(`CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`, 300 000) : sur une autre machine, le relancer suffit.

## Publier la méthode — le dépôt public

La méthode s'installe chez quelqu'un d'autre depuis un dépôt public dédié,
`https://github.com/qu4ntum4/methode-claude` (registre, 11/11/2026). **Ce dossier reste la seule
source** ; le dépôt public ne s'édite jamais à la main. `python publier.py` assemble la part
partageable dans un dossier de travail, la compare au clone du dépôt public, et commite puis
pousse s'il y a du neuf — relancé sans changement, il ne pousse rien.

- **Ce qui part** : `METHODE.md`, `gabarits/`, `outils/` sans `hooks/signaler_sessions.py` (le
  capteur, propre à une maison), sans `__pycache__` ni `outils/public/`, et le texte d'accueil
  `outils/public/README.md`, posé à la racine du dépôt public avec le prompt à coller dans Claude
  Code. **Ce qui ne part jamais** : `ETAT.md`, `TODO.md`, le `CLAUDE.md` du projet, `docs/`,
  `bilans/`.
- **Le garde-fou** : la part assemblée ne doit porter aucun des mots de
  `outils/public/mots-interdits.txt` (une expression régulière par ligne) ; sinon rien n'est
  publié. C'est le seul endroit de la règle « `METHODE.md`, `gabarits/` et `outils/` restent
  anonymes » : le point d'étape du projet lance `publier.py --verifier`.
- **Le clone** vit par défaut dans un dossier `methode-claude` à côté de ce projet (`--clone
  <dossier>` pour un autre endroit) ; il est créé au premier passage et remis au niveau du dépôt à
  chaque passage. Les commits y sont signés du compte GitHub avec son adresse de relais, pas
  d'une adresse personnelle.
- **Côté destinataire**, le README dit tout : un prompt à coller dans Claude Code vérifie git et
  Python, clone dans `Documents\Claude\methode-claude`, lance `installer.py` puis `--verifier`.
  Sans le capteur à côté, l'installeur ne pose que les automatismes de la méthode.
