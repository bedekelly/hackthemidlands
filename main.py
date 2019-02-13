from flask import Flask, jsonify, request

from flask_cors import CORS
from redis import Redis

import random
from facts_data import facts as facts_data

TABLE_NAME = "facts"

app = Flask(__name__)
CORS(app)
redis = Redis()


def random_fact():
    all_facts = list(redis.hgetall(TABLE_NAME))
    fact = random.choice(all_facts)
    return fact.decode("utf-8")


@app.route("/fact/all")
def get_all_facts():
    items = redis.hgetall(TABLE_NAME).items()

    decoded_items = []
    for fact, score in items:
        decoded_items.append({
            "score": int(score.decode("utf-8")),
            "fact": fact.decode("utf-8")
        })

    def get_score(item):
        return item["score"]

    facts = sorted(decoded_items, key=get_score, reverse=True)
    return jsonify(facts=facts)


@app.route("/fact/vote", methods=["POST"])
def vote_on_fact():
    fact = request.json["fact"]
    vote = request.json["vote"]
    
    score_change = {"up": 1, "down": -1, "skip": 0}[vote]
    
    redis.hincrby(TABLE_NAME, fact, score_change)

    return jsonify(fact=random_fact())


def initialise():
    for fact in facts_data:
        redis.hset(TABLE_NAME, fact, 0)


initialise()
app.run(debug=True)