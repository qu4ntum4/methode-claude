# « Nom du projet » — « pour qui »

« Deux à cinq lignes : ce qu'est le projet, la technique, ce qui le rend sensible (données
personnelles, matériel qui agit sur le réel…). » Projet de longue haleine : tout ce qui compte
vit dans des fichiers, jamais dans une conversation.

## Où chercher — avant toute recherche

`ETAT.md` dit où on en est et quelle est la prochaine action : il s'affiche au démarrage.
Ensuite, ouvrir **le seul document du sujet**.

| La question | Le fichier |
|---|---|
| Comment ça marche aujourd'hui | `docs/modele.md` « ou le document qui décrit l'état présent » |
| Pourquoi c'est ainsi, ce qui a été écarté | `docs/decisions.md` |
| Les surprises qui ont déjà coûté cher | `docs/pieges.md` |
| Ce qui reste à faire | `TODO.md` (sommaire) puis `docs/chantiers/<chantier>.md` |
| « Autre sujet récurrent » | « son fichier » |

**Ne jamais lire un gros document entier pour trouver un fait.** Un registre se lit par son
sommaire — `grep -n '^## ' docs/decisions.md` — puis la section voulue. Et **chercher dans le
projet avant de reconstituer une règle à partir des données** : ce qui a déjà été tranché ou
découvert y est écrit.

## Commandes

```
« lancer / relancer l'application »
« lancer tous les tests ou contrôles en une commande — qui ne relance pas un code déjà vert »
« sauvegarder avant un essai risqué, et restaurer »
```

## Règles de travail propres à ce projet

- « Ce qui s'écarte des défauts : conventions, interdits, précautions avant une action. »
- « Où vit la source de vérité de chaque chose, et ce qu'on ne modifie jamais à la main. »
- « Ce qu'une action demande comme confirmation (déploiement, suppression, envoi). »

## Consigner au fil de l'eau

- **`docs/decisions.md` s'écrit au moment où l'arbitrage est validé en conversation**, avant ou
  avec le code — pas au commit : la date, la formulation de celui qui tranche, le pourquoi, et
  **ce qui a été écarté**. Une décision ne rend aucun fichier faux, donc rien ne la réclame :
  c'est le seul fichier dont l'oubli ne se voit pas.
- La documentation de l'état présent se met à jour **dans le commit qui la rend fausse**.
- Une décision prise par l'agent sans l'utilisateur se consigne aussi, marquée comme telle, pour
  être revue en fin de chantier.

## Point d'étape (`/checkpoint`) — ce que ce projet y ajoute

1. « La commande de vérification : tests, contrôle de configuration, compilation… »
2. « Les fichiers propres au projet à relire s'ils sont devenus faux. »
3. « Toute étape propre au projet : retirer la copie du serveur, régénérer un export… »

## Pièges qui ont coûté le plus cher — détail dans `docs/pieges.md`

- « Les cinq à huit pièges les plus coûteux, une ligne chacun. Les autres restent dans
  `docs/pieges.md`, à lire avant de construire quoi que ce soit sur le sujet. »

## Limites qui ne se négocient pas

- « Ce que l'agent ne fait jamais, même à la demande : saisir des identifiants, versionner des
  données personnelles, agir sur le réel sans confirmation… »
