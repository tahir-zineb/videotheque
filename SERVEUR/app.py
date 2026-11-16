from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from functools import wraps
import requests
import json
import os

app = Flask(__name__)

# Identifiants lus depuis les variables d'environnement (fichier .env)
ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
app.secret_key = os.environ["SECRET_KEY"]

def login_required(f):
    """Renvoie vers la page de connexion si l'utilisateur n'est pas connecté."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return wrapper

# Page d'accueil avec le formulaire de connexion
@app.route('/')
def home():
    return render_template('index.html')

# Route pour traiter le formulaire de connexion
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Vérification des identifiants (vous pouvez remplacer par une base de données)
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["user"] = username
        return redirect(url_for('add_movie'))
    else:
        return "Nom d'utilisateur ou mot de passe incorrect", 401

# Page après une connexion réussie
@app.route('/welcome')
@login_required
def welcome():
    # Exemple de récupération de données depuis l'API
    api_url = "http://api:5000"  # Utilisez le nom de service de l'API Docker
    response = requests.get(api_url)
    
    # Affichez la réponse de l'API
    data = response.json()  # Assurez-vous que l'API renvoie du JSON
    return f"Bienvenue, vous êtes connecté !<br>Message depuis l'API : {data['message']}<br>Statut : {data['status']}"


@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        description = request.form['description']
        
        movie = {'title': title, 'genre': genre.split(","), 'description': description}

        response = requests.post('http://api:5000/add_movie', json=movie, timeout=6*60)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Ici, tu peux ajouter la logique pour enregistrer ces informations (par exemple dans une base de données)
            print(f"Film ajouté: {title}, Genre: {genre}, Description: {description}")

            return redirect(url_for('films'))  # Redirige vers la page de bienvenue après l'ajout
        else:
            print(f"Request failed with status code {response.status_code}")

    return render_template('add-movie.html')  # Affiche le formulaire d'ajout de film

@app.route('/films')
@login_required
def films():
    # Make a GET request to the server
    response = requests.get('http://api:5000/movies')

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        try:
            # Parse the response as JSON
            data = response.json()
            if "status" in data and data["status"]=='success' and 'films' in data:
                movies = data['films']
                return render_template('films.html', movies=movies)  # Passer les films à la page 'films.html'
            else:
                print("Key 'films' not found in the response.")
                # TODO error 
        except ValueError:
            print("Response is not valid JSON.")
    else:
        print(f"Request failed with status code {response.status_code}")

@app.route('/delete_movie', methods=['POST'])
@login_required
def delete_film():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        if not data or 'title' not in data:
            return jsonify({"error": "Missing title in request"}), 400
        title = data['title']
        
        response = requests.post('http://api:5000/del_movie', json={"title":title}, timeout=6*60)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Ici, tu peux ajouter la logique pour enregistrer ces informations (par exemple dans une base de données)
            print(f"Film `{title}` a été suprimé!")
            return jsonify({"message": "Movie deleted successfully"}), 200
        else:
            print(f"Request failed with status code {response.status_code}")
            return jsonify({"message": f"Request failed with status code {response.status_code}"}), response.status_code
        
        
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)  # Exposé sur le port 80
