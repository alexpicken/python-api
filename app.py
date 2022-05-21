from webbrowser import Elinks
from flask import Flask, request

import spacyprocess
import neo4jclass
import random


app = Flask(__name__)
app.config["DEBUG"] = True
    
@app.route("/", methods=["GET"])
def home():
    return "<h1>Hello World!</h1>"

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True)
    query_result = req.get("queryResult")
    query_text = query_result.get("queryText").lower()
    query_response = query_result.get("fulfillmentText")
    action = query_result.get("action")
    session_id = req.get("session").split("/")[-1]
    user_id = req.get("originalDetectIntentRequest").get("payload").get("userId")
    contexts = query_result.get("outputContexts")

    if (action == "input.give.name" or action == "input.welcome"):
        neo4jclass.add_session_graphs(user_id, session_id)
    elif (action == "input.unknown"):
        topic_list = []
        for context in contexts:
            if context["name"].split("/")[-1] == "session-work":
                topic_list.append(context["parameters"]["work"])
            elif context["name"].split("/")[-1] == "session-studies":
                topic_list.append(context["parameters"]["studies"])
            elif context["name"].split("/")[-1] == "session-family":
                topic_list.append(context["parameters"]["family"])
            elif context["name"].split("/")[-1] == "session-hobby":
                topic_list.append(context["parameters"]["hobby"])
        random_int = random.randint(0, len(topic_list))
        if random_int < len(topic_list):
            query_response = "I'd like to talk more about your " + str(topic_list[random_int]) +", what else can you tell me about that?"

    spacyprocess.analyse(session_id, query_text)

    return {
        "fulfillmentText": query_response
    }