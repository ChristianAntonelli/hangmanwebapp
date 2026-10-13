# Il back end: un server web fatto con Flask.
#
# Avvio:   python app.py
# Poi apri http://127.0.0.1:5000 nel browser.
#
# Come funziona in breve:
# - Il browser chiede "/"            -> il server risponde con la pagina HTML (static/index.html)
# - La pagina carica style.css e script.js (sempre dalla cartella static/)
# - script.js chiama le "API" qui sotto (/api/new-game, /api/guess) con fetch()
#   e riceve risposte in JSON, che usa per aggiornare la pagina.

import os
import uuid

from flask import Flask, jsonify, request, session

from game import HangmanGame

# Flask serve automaticamente i file dentro la cartella "static/"
app = Flask(__name__)

# HTTP e' "senza memoria": ogni richiesta e' indipendente dalle altre.
# Per ricordarci le partite le salviamo in un dizionario: id_partita -> HangmanGame.
# Il browser riceve l'id e ce lo rimanda a ogni tentativo.
# (Vive in RAM: se riavvii il server le partite spariscono. In un progetto vero
# si userebbe un database, ma per imparare va benissimo cosi'.)
app.secret_key = os.environ.get("SECRET_KEY", "chiave-solo-per-prove-locali")


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/new-game", methods=["POST"])
def new_game():
    game_id = str(uuid.uuid4())
    game = HangmanGame()
    session["game"] = game.save_state()  # la partita va nel cookie
    print(f"### For the developer: game {game_id[:8]} word is: {game.word} ###")

    data = game.to_dict()
    data["game_id"] = game_id
    data["message"] = "New game! First and last letters are already shown. Good luck!"
    return jsonify(data)


@app.route("/api/guess", methods=["POST"])
def guess():
    body = request.get_json()
    state = session.get("game")
    if state is None:
        return jsonify({"error": "Game not found. Start a new game."}), 404

    game = HangmanGame(state)                     # ricostruisco la partita
    message = game.guess(body.get("guess", ""))
    session["game"] = game.save_state()           # salvo lo stato aggiornato

    data = game.to_dict()
    data["message"] = message
    return jsonify(data)


if __name__ == "__main__":
    # debug=True: il server si riavvia da solo quando modifichi i file .py
    app.run(debug=True)
