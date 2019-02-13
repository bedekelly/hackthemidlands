import random
from pprint import pprint
from redis import Redis
from flask import Flask, jsonify, request
from flask_cors import CORS

from facts_data import dares

TABLE_NAME = "DARES"

app = Flask(__name__)
CORS(app)
redis = Redis()


def random_dare():
    """Fetch a random dare from the database."""
    all_dares = list(redis.hgetall(TABLE_NAME))
    dare = random.choice(all_dares)
    return dare.decode("utf-8")


@app.route("/dare/all")
def get_all_dares():
    """Retrieve all the dares, with scores, from the database."""
    items = redis.hgetall(TABLE_NAME).items()
    dares = [ 
        { 
            "score": int(score.decode("utf-8")), 
            "dare":  dare.decode("utf-8")
        }
        for (dare, score) in items 
    ]
    
    dares = sorted(dares, key=lambda d: d["score"], reverse=True)
    return jsonify(dares=dares)


@app.route("/dare/vote", methods=["POST"])
def vote_on_dare():
    """Vote on a dare, and retrieve a random next dare."""
    dare = request.json["dare"]
    vote = request.json["vote"]
    score_change = { "up": 1, "down": -1, "skip": 0 }[vote]
    redis.hincrby(TABLE_NAME, dare, score_change)
    return jsonify(dare=random_dare())


# Create all the rows.
for dare in dares:
    redis.hset(TABLE_NAME, dare, 0)


app.run(debug=True)
