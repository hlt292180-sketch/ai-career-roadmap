from flask import Flask, request, jsonify
from step4_chain import converge_goal, generate_route

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    user_input = data["user_input"]
    goal = converge_goal(user_input)
    route = generate_route(goal)
    return jsonify(route)

if __name__ == "__main__":
    app.run(debug=True)