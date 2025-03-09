# Import de bibliothèques
import flask
from flask import request, jsonify
from engine import Engine

# URL FORMAT : curl -X POST https://zachvfx.pythonanywhere.com/api/v1/check_move/ -H "Content-Type: application/json" -d '{"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1","from": "a2", "to": "b5"}'

# Création de l'objet Flask
app = flask.Flask(__name__)

# Lancement du Débogueur
app.config["DEBUG"] = True

# Initialisation du moteur d'échecs
engine = Engine()


@app.route("/", methods=["GET"])
def home():
    return """<h1>A chess engine by Zach</h1>"""


@app.route("/api/v1/get_legal_moves/", methods=["POST"])
def get_legal_moves():
    data = request.get_json()
    position = data.get("position")
    if position is None:
        return jsonify({"error": "Position is required"}), 400

    try:
        position = int(position)
        legal_moves = engine.get_legal_moves(position)
        return jsonify({"legal_moves": legal_moves})
    except ValueError:
        return jsonify({"error": "Invalid position"}), 400


@app.route("/api/v1/check_move/", methods=["POST"])
def check_move():
    data = request.get_json()
    fen = data.get("fen")
    from_pos = data.get("from")
    to_pos = data.get("to")

    if not fen or from_pos is None or to_pos is None:
        return jsonify({"error": "FEN, from, and to positions are required"}), 400

    try:
        from_pos = engine._get_index_from_pgn(from_pos)
        to_pos = engine._get_index_from_pgn(to_pos)
        engine.load_fen_notation(fen)
        legal_moves = engine.get_legal_moves(from_pos)
        is_legal = to_pos in legal_moves
        return jsonify({"is_legal": is_legal})
    except ValueError:
        return jsonify({"error": "Invalid positions"}), 400


if __name__ == "__main__":
    app.run()
