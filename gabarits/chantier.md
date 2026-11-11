# Chantier — « nom du chantier »

« Deux lignes : le périmètre, et l'état en un mot (pas commencé, en cours, en service). » Une
tâche faite **se retire** de ce fichier : son commit la garde, et `docs/decisions.md` si elle a
tranché quelque chose. Ouvert le « JJ/MM/AAAA ».

## Où en est la session — « seulement si une session annexe porte ce chantier »

« Copie de travail `<dossier>`, branche `<branche>`, partie de `main` à `<commit>` ; serveur
d'essai : port `<n>`. » **Prochaine action** : « une seule, telle que la session la reprendra
après un `/clear` ». **Fini quand** : « le critère vérifiable ». « Ce bloc est l'état de cette
session, réécrit à chacun de ses points d'étape ; `ETAT.md` reste à la principale. »

## « Ce qui est validé » — le cadre

« Quand le chantier repose sur des arbitrages déjà pris : trois à dix lignes qui les résument,
avec un renvoi vers `docs/decisions.md`. Pas le raisonnement — il est dans le registre. »

## « Sous-ensemble ou étape »

- [ ] « Une tâche validée, en une à trois lignes : le quoi, et comment on saura qu'elle est
  finie. Le détail technique va dans le document du sujet. »
- [ ] [P1] « Une tâche plus urgente que son chantier : la marque en tête de ligne le dit. »
- [ ] « Une tâche qui attend une réponse — de qui, et depuis quand. »

## « Autre sous-ensemble »

- [ ] …

## Pour plus tard

- [ ] « Ce qui est validé mais volontairement remis à plus tard, et pourquoi. »
