# Test technique

## Overview
Le but de ce test technique est d'améliorer et faire évoluer une petite application qui se charge de stocker des coupons dans une base de données et ensuite de vérifier si un coupon est applicable à un produit, et d'en calculer le nouveau prix. 

Elle s'utilise actuellement avec une CLI, et tu peux trouver des exemples d'usage dans `example.sh`.

L'état actuel de la code-base ne permet pas d'envisager sereinement son évolution. 
Il faudra donc d'abord refactor/cleanup la code-base avant d'envisager d'étendre ses fonctionnalités. 

Il n'y a pas d'attente de retro-compatibilité concernant le type et le schema des données des entrées/sorties, tu es libre d'apporter tous les changements nécessaires à ce repository pour en faire une application pratique pour l'utilisateur et simple pour le dévellopeur.

## Première partie
Il s'agit dans un premier temps de refactorer la code-base pour la préparer à ces évolutions. 
Ce refactoring doit aboutir sur du code:
- robuste (couvrant les cas nominaux et les edge cases)
- maintenable (simple a naviguer et à comprendre)
- évolutif (simple à modifier et étendre). 

Ce travail doit être itératif et les commits atomiques, l'idée n'est pas de faire une refonte complète en un seul coup, mais d'y aller de manière progressive. Idéallement l'application doit rester fonctionnelle entre chaque commit.

## Seconde partie
Une fois le refactoring effectué, tu peux implémenter les évolutions suivantes:

- utilisation via une api REST (deux entry-points, un pour le server web, l'autre pour le client CLI)
- utilisation d'une bdd nosql à la place de sqlite (possibilité de configurer l'app pour utiliser l'une ou l'autre)
- ajout d'opérateur OR et AND et NOT, combinables à souhait, dans le système de conditions des coupons.

Tu es libre de choisir la ou les évolutions que tu souhaites implémenter.

Pour les évolutions que tu n'as pas le temps de mettre en place, laisses des commentaires précisant comment tu aurais envisagé leur implémentation dans la code base.

## Déroulement du test
Ce test ne nécessite que quelques heures de travail, mais il se déroule sur une période de plusieurs jours afin de t'aider à faire coexister ce test avec les autres contraintes de ta vie perso. La date de livraison attendue est mentionnée dans l'émail d'invitation que tu as reçu.

Afin de suivre ta progression et le temps passé sur ce test, il est demandé de commit régulièrement (pas de manière automatique, mais plutôt afin de refléter les différentes itérations dans ton travail). Et aussi, tu as le droit de te tromper, de changer d'approche en cours de route, et le fait que ceci soit visible dans tes commits est normal et ne doit pas t'inquiéter.

Également, au cours de ton travail, si certains aspects de ce test te semblent triviaux et/ou chronophages à implémenter, tu es libre de laisser des commentaires en TODO afin d'expliquer la démarche que tu aurais suivie, afin de te concentrer sur ce qui a le plus de valeur selon toi.

Une fois fini, tu devras envoyer un email à **e.hupin@coupon.ai** pour confirmer que tu as bien fini.
L'évaluation du test se fera la simplicité et le pragmatisme des solutions mises en place, et sur la qualité technique et fonctionnelle du résultat.

Bonne chance :)


