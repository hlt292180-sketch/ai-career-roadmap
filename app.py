from flask import Flask, request, jsonify
from step4_chain import converge_goal, generate_route
from step8_rag import rag_answer

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    user_input = data["user_input"]
    goal = converge_goal(user_input)
    route = generate_route(goal)
    return jsonify(route)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data["question"]
    answer = rag_answer(question)
    return jsonify({"answer": answer})
    
if __name__ == "__main__":
    app.run(debug=True)