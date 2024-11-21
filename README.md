# UE-AD-A1-MIXTE

## Description

Ce projet est une application de réservation de films utilisant plusieurs microservices. Chaque microservice est responsable d'une partie spécifique de l'application : gestion des utilisateurs, gestion des films, gestion des horaires de projection et gestion des réservations.

Ce projet a été réalisé dans le cadre du cours d'architecture distribuée de Mme Hélène Coullon à l'IMT Atlantique. Pour plus d'informations sur le cours, vous pouvez consulter [le site de Mme Hélène Coullon](https://helene-coullon.fr/pages/ue-ad-24-25/).

## Prérequis

- Python 3.x
- pip (Python package installer)

## Installation

1. Clonez le dépôt :
    ```sh
    git clone https://github.com/Nathekip/UE-AD-A1-MIXTE
    cd UE-AD-A1-MIXTE
    ```

2. Installez les dépendances pour chaque microservice :
    ```sh
    pip install -r user/requirements.txt
    pip install -r movie/requirements.txt
    pip install -r showtime/requirements.txt
    pip install -r booking/requirements.txt
    ```

## Lancer le projet

Pour lancer tous les microservices en utilisant le script `runServer.py`, suivez les étapes ci-dessous :

1. Assurez-vous que vous êtes dans le répertoire racine du projet.
2. Exécutez le script `runServer.py` :
    ```sh
    python runServer.py
    ```

Ce script lancera les quatre microservices suivants :
- `user` sur le port 3303
- `movie` sur le port 3300
- `showtime` sur le port 3304
- `booking` sur le port 3302

## Utilisation

Vous pouvez maintenant accéder aux différents microservices via les URL suivantes :
- Utilisateurs : `http://127.0.0.1:3303`

## API Endpoints

### Utilisateurs
- `GET /users`: Récupérer tous les utilisateurs
- `POST /users`: Ajouter un nouvel utilisateur
- `DELETE /users/<user_id>`: Supprimer un utilisateur
- `POST /users/<user_id>/bookings`: Ajouter une réservation pour un utilisateur
- `GET /users/bookings/<user>`: Récupérer les réservations d'un utilisateur
- `GET /users/movies/<user>`: Récupérer les films réservés par un utilisateur

## Licence

Ce projet est sous licence GNU.