from flask import Flask, render_template_string

app = Flask(__name__)

HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Exemple Flask</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2563eb;
        }
        .nav {
            margin-top: 20px;
        }
        .nav a {
            display: inline-block;
            margin-right: 15px;
            padding: 10px 20px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .nav a:hover {
            background: #1d4ed8;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>🔧 Projet Flask Exemple</h1>
        <p>Bienvenue sur ce projet flask d'exemple</p>
        <div class="nav">
            <a href="{{ url_for('home') }}">accueil</a>
            <a href="{{ url_for('about') }}">à propos</a>
            <a href="{{ url_for('contact') }}">contact</a>
        </div>
    </div>
</body>
</html>
"""

ABOUT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>À propos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2563eb;
        }
        a {
            color: #2563eb;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>📖 À propos</h1>
        <p>ce projet est un exemple de sous-app flask hébergée via le multi-projects host</p>
        <p><a href="{{ url_for('home') }}">← retour</a></p>
    </div>
</body>
</html>
"""

CONTACT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Contact</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2563eb;
        }
        a {
            color: #2563eb;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>📧 Contact</h1>
        <p>email: contact@exemple.com</p>
        <p><a href="{{ url_for('home') }}">← retour</a></p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/about')
def about():
    return render_template_string(ABOUT_TEMPLATE)

@app.route('/contact')
def contact():
    return render_template_string(CONTACT_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
