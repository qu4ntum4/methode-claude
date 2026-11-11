# TODO — ce qui reste à faire

**Ce fichier est un sommaire.** Le reste à faire vit dans un fichier par chantier, sous
`docs/chantiers/`. Ouvrir le chantier sur lequel on travaille, et lui seul.

Seuls les éléments **validés par « l'utilisateur »** sont inscrits. Une tâche faite **se retire**
de son fichier de chantier : son commit la garde, et `docs/decisions.md` garde ce qu'elle a
tranché.

**Maintenant** : la prochaine action est dans [`ETAT.md`](ETAT.md), pas ici.

## Les chantiers

**P** : 1 maintenant · 2 ensuite · 3 un jour. Une tâche peut aussi porter `[P1]`, `[P2]` ou
`[P3]` en tête de ligne — obligatoire dans `divers`, facultatif ailleurs.

| Chantier | P | Ouvertes | Ce qu'on y trouve |
|---|---:|---:|---|
| [`« nom ».md`](docs/chantiers/« nom ».md) | « 1 » | « n » | « Une ligne : le périmètre, et l'état en un mot — en service, en cours, pas commencé. » |
| [`divers.md`](docs/chantiers/divers.md) | 2 | 0 | Les petites tâches sans famille, chacune avec sa marque de priorité ; trois qui parlent de la même chose deviennent un chantier. |

## Ailleurs

- Ce qui a été décidé, et pourquoi : `docs/decisions.md`
- Comment ça marche aujourd'hui : « le document de l'état présent »
- Les surprises qui ont coûté du temps : `docs/pieges.md`
- Les tâches closes avant le « JJ/MM/AAAA » : `docs/archives/todo-clos-au-« date ».md`
  « (ou un emplacement non versionné si elles portent des données personnelles) »

## Tenir ce fichier

- Une tâche validée s'ajoute **dans son chantier**, sous la section qui lui correspond, en une à
  trois lignes, avec sa priorité. Le détail va dans le document du sujet, pas dans la tâche.
  « Ajoute-le à la todo » : rangé ici, au bon endroit, sans plan — la tâche n'est pas lancée.
- Un nouveau chantier, c'est un nouveau fichier sous `docs/chantiers/` **et** une ligne ici,
  avec sa priorité.
- Les comptes, l'ordre par priorité et la mention « dort depuis le … » (un mois sans mouvement)
  se mettent à jour au point d'étape, par le script `chantiers.py` de `/checkpoint`.
- Un chantier à zéro part dans `docs/archives/` avec son fichier, et sa ligne quitte ce sommaire.
