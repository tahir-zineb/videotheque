Vidéothèque

CI

Application web de gestion de films, conteneurisée avec Docker Compose et vérifiée automatiquement par une CI GitHub Actions.

Contexte

Projet réalisé pendant mon master, puis repris pour l'amener à un niveau proche de la production : correction des failles de sécurité, gestion des secrets et ajout d'un pipeline CI avec des tests de sécurité automatisés.

Architecture
Navigateur ──:80──▶ serveur (Flask, pages HTML) ──réseau Docker interne──▶ api (Flask, JSON) ──▶ films.json
serveur : interface web (connexion, liste, ajout et suppression de films). Seul service exposé.
api : logique métier et accès aux données. Joignable uniquement depuis le réseau Docker interne.
Lancer le projet
bash
cp .env.example .env      # puis renseigner les valeurs
docker compose up -d --build

Application disponible sur http://localhost

Choix techniques
Choix	Pourquoi
Deux services séparés	Séparer présentation et données : chaque service a ses dépendances et peut évoluer indépendamment
Réseau Docker interne	Le serveur joint l'API par son nom de service (http://api:5000), sans l'exposer
Variables d'environnement	Aucun secret dans le code ni dans le dépôt Git
Sessions Flask signées	Garder l'utilisateur connecté de façon sûre d'une page à l'autre
DevOps
Conteneurisation : un Dockerfile par service, orchestration avec Docker Compose.
Intégration continue : à chaque push et pull request, GitHub Actions construit les images, démarre l'application et lance les tests.
Workflow Git : les modifications passent par une branche et une pull request, fusionnée seulement si la CI est verte.
DevSecOps
Failles corrigées
Avant	Après
Identifiants écrits en dur dans le code	Lus depuis un fichier .env non versionné
API exposée sur le port 5000, sans authentification	API accessible uniquement depuis le réseau Docker interne
Pages accessibles sans connexion (contrôle d'accès absent)	Sessions signées et décorateur @login_required
Mode debug Flask activé	Désactivé
Informations personnelles dans le README et l'historique Git	Dépôt republié avec un historique propre
Tests de sécurité automatisés

La CI vérifie à chaque modification que ces corrections restent en place :

une page protégée sans connexion doit rediriger vers la connexion ;
l'API ne doit pas répondre depuis l'extérieur.

Exemple : une pull request qui réexposait volontairement l'API a été bloquée par la CI.

La CI détecte la réexposition de l'API