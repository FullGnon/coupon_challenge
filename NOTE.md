# Méthode de travail

0/ Préparation
* Analyse du code legacy à faire évoluer
* Analyse du modèle de données
* Construction schématique à main levée de l'architecture cible

1/ Caisse à outil
* Uv: package manager
    * Essentiel pour collaborer et avoir des envs de dev le plus proche possible
    * Semble être une alternative prometeuse à poetry, notamment sur la performance
    * C'était l'occasion de tester
* Ruff: linting and formatting
    * Remplace Isort, Flake8, Black
    * Ex: import unused
* Mypy:
    * J'aurai également pu rajouter un type checker
    * Je n'ai pas voulu aller trop loin dans les contraintes pour ce test
    * Ex: Check que les functions reçoivent les bons types
* Pytest:
    * Tests à chaque PR

2/ Application model
* Pydantic:
    * Structurer les objets à manipuler
    * Data validation grâce aux annotations
* Model Coupon:
* Model Product:

3-4/ Refacto legacy
* Utilisation des modeles précédement défini dans le code legacy
* Découpage du monolithe en fonction simple
* Anticipation du futur code notamment pour le service de l'API
    * l'intention de tester ces fonctions maintenant
    * Les embarquer plus tard dans le service de l'API

5/ Socle pour faire fonctionner l'API
* Préparation du développement de l'API basé sur FastAPI:
 FastAPI:
    * Je le connais déjà (rapidité d'implémentation)
    * Simple à mettre en place
    * Se couple très bien avec Pydantic
    * Permet de fonctionner de manière async au sens Python du terme
* Mise en place du docker compose:
    * Pour accueillir le potentiels services requis (base de données)
* Construction de l'image docker de l'API

note: Optimisable

6/ Implementation du router des Coupons
note: Aucune db n'est connecté pour le moment et donc l'application n'est pas fonctionnel.
Seulement testable
* Mise en place des opérations CRUD
* Facilite la manipulation des données au runtime
* Utilisation de DTO pour les communications avec l'API
Pourquoi DTO: # TODO
* Abstraction de l'interface de stockage:
    * en prévision de l'implémentation de MongoDB et SQLite
* L'interface de stockage est fourni par injection de dépendance aux endpoints
* Async: pour anticiper l'optimisation des performances:
    * Certainement une application d'e-commerce, donc charge conséquente

7/ Implementation de la logique métier
* Dans un service à part:
    * L'idée est de pouvoir utiliser ce service dans l'API mais aussi dans la CLI, et pourquoi pas ailleurs
    * On récupère la logique qu'on avait commencé dans le code legacy
* La logique métier est fourni par injection de dépendance aux endpoints

8/ Implementation de la route apply_product
* Dans le même routeur que les coupons CRUD, par simplicité
* De la même manière que les endpoints précédent on utilise l'interface de storage et le service métier

9/ Implementation du backend SQLite
* on reprend l'interface storage défini
* Utilisation sqlite3 sans sqlalchemy par simplicité

10/ Implementation du backend MongoDB
* Ajout des services dans le docker compose avec une WebUI
(* J'ai encapsulé la gestion des erreurs au niveau de la dépendance
    * Faciliter le mapping Exception => Status Code
    * DRY code)
* Implementation imparfaite, manque de connaissance technique avec MongoDB

11/ Application settings
* Je me suis une fois de plus basé sur Pydantic
* J'ai aussi fait de l'injection de dépendance
    * Séparation des configurations pour éviter d'avoir une configuration monolithe

12/ CLI
* Utilisation de Typer
    * Suite logique à FastAPI
    * Facile à implémenter
    * Utilisation des mêmes services que l'API
* J'aurai également pu utiliser 

# TODO
* strategy test API (spike, etc)
* Changelog

SOLID: Single responsability, Open/Closed (fermé à la modification, ouverte à l'extension), Liskov (héritage), Interface ségregation, Inversion de dépendance (dépendre des abstractions pas des implémentations) => modularité

IaC: Config file that can be versionned

Monitoring: log JSON formatted, Grafana, Loki