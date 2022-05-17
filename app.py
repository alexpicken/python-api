from flask import Flask, request

import spacyprocess
import neo4jclass


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
    #user_id = req.get("originalDetectIntentRequest").get("payload").get("userId")
    user_id = "sven"

    if (action == "chatbotgreetings.chatbotgreetings-custom" or action == "input.welcome"):
        neo4jclass.add_session_graphs(user_id, session_id)
    
    simple, detailed = spacyprocess.analyse(session_id, query_text)
    if simple:
        return {
            "fulfillmentText": simple + detailed
        }

    return {
        "fulfillmentText": query_response
    }