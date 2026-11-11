# Registre des décisions

Ce qui a été tranché, quand, **pourquoi**, et ce qui a été écarté. Ce fichier s'ajoute et ne se
réécrit pas : il ne décrit pas l'état présent — c'est le rôle du document du modèle — il garde
le raisonnement, qui s'évapore en quelques jours. L'entrée la plus récente est en tête.

**Quand y écrire.** Au moment où l'arbitrage est **validé en conversation**, avant ou avec le
code qui l'applique — pas au commit, et surtout pas en fin de session. Une décision ne rend
aucun fichier faux, donc rien ne vient la réclamer : c'est le seul fichier dont l'oubli ne se
voit pas. Ne pas attendre d'être sûr de la forme finale : une entrée qu'on corrige ensuite vaut
mieux qu'un raisonnement perdu.

**Qui a tranché.** Chaque entrée le dit : *« l'utilisateur »*, avec sa formulation citée quand
elle est plus juste que celle de l'agent ; ou *l'agent seul*, marqué **[décision de l'agent, à
revoir]** — ces entrées se passent en revue en fin de chantier, et la marque tombe quand
l'utilisateur confirme.

Se lit par son sommaire : `grep -n '^## ' docs/decisions.md`.

---

## « JJ/MM/AAAA » — « Titre : ce qui a été décidé, en une ligne »

« Le contenu de la décision, en deux à dix lignes. »

**Pourquoi** : « la raison, les faits qui l'ont imposée, un chiffre s'il y en a un. »

**Qui** : « l'utilisateur », *« sa formulation citée »* — ou **[décision de l'agent, à revoir]**.

**Écarté** : « l'option ou les options qu'on a refusées, et pourquoi. C'est la partie qui
s'évapore le plus vite, et celle qui évite de rouvrir le débat. »
