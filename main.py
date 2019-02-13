from flask import Flask, jsonify, request

from flask_cors import CORS
from redis import Redis

import random
from dares_data import dares

TABLE_NAME = "dares"

app = Flask(__name__)
CORS(app)
redis = Redis()


def random_dare():
    all_dares = list(redis.hgetall(TABLE_NAME))
    dare = random.choice(all_dares)
    return dare.decode("utf-8")


@app.route("/dare/all")
def get_all_dares():
    items = redis.hgetall(TABLE_NAME).items()
    dares = [
        {
            "score": int(score.decode("utf-8")),
            "dare": dare.decode("utf-8")
        } for dare, score in items
    ]
    dares = sorted(dares, key=lambda d: d["score"], reverse=True)
    return jsonify(dares=dares)


@app.route("/dare/vote", methods=["POST"])
def vote_on_dare():
    dare = request.json["dare"]
    vote = request.json["vote"]
    
    score_change = { "up": 1, "down": -1, "skip": 0 }[vote]
    
    redis.hincrby(TABLE_NAME, dare, score_change)

    return jsonify(dare=random_dare())


for dare in dares:
    redis.hset(TABLE_NAME, dare, 0)



app.run(debug=True)