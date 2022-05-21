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
    user_id = req.get("originalDetectIntentRequest").get("payload").get("userId")
    #if query_result["outputContexts"]:
        #for context in query_result.get("outputContexts"):
            #if(query_result.get)
            #family_topic = query_result.get("outputContexts").get("")
            #work_topic =
            #hobby_topic =
            #studies_topic = 

    if (action == "chatbotgreetings.chatbotgreetings-custom" or action == "input.welcome"):
        neo4jclass.add_session_graphs(user_id, session_id)
    #elif (action == "input.unknown"):
        #topic_list = [family_topic, work_topic, hobby_topic, studies_topic]

    spacyprocess.analyse(session_id, query_text)

    return {
        "fulfillmentText": query_result.get("outputContexts")
        #"fulfillmentText": query_response
    }