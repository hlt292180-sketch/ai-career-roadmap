from flask import Flask, request, jsonify
from flask_cors import CORS
from step4_chain import converge_goal, generate_route
from step7_retrieve import retrieve          # ← 新增：把检索器引进来
from step8_rag import rag_answer


app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}    # silent=True：body 不是 JSON 时返回 None 而不报错
    user_input = (data.get("user_input") or "").strip()
    if not user_input:                            # 缺 key 或空字符串 → 是客户端的错，返回 400
        return jsonify({"error": "缺少 user_input 字段"}), 400

    # 编排链：收敛目标 → 检索相关知识 → 带着知识生成路线
    goal = converge_goal(user_input)              # 1. 把模糊输入收敛成结构化目标
    hits = retrieve(user_input, top_k=3)          # 2. 从知识库检索最相关的 3 条转型知识
    context = "\n".join(hits)                      #    拼成一段参考资料
    route = generate_route(goal, context)         # 3. 把知识喂给路线生成（这才是真正的 RAG + 编排）
    return jsonify(route)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "缺少 question 字段"}), 400
    answer = rag_answer(question)
    return jsonify({"answer": answer})
    
if __name__ == "__main__":
    app.run(debug=True)