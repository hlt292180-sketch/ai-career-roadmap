from knowledge import KNOWLEDGE

# 1. 把整段知识库切成一条条（按换行切，每行算一段）
chunks = [line.strip() for line in KNOWLEDGE.strip().split("\n") if line.strip()]

# 2. 假 embedding：算 question 和一段文字的"相关分"=重合的字符数
def fake_score(question, chunk):
    score = 0
    for ch in question:
        if ch in chunk:
            score += 1
    return score

# 3. 检索：给每段算分，按分从高到低排，取前 top_k 段
def retrieve(question, top_k=2):
    scored = [(fake_score(question, c), c) for c in chunks]
    scored.sort(reverse=True)          # 按分数从高到低
    return [c for score, c in scored[:top_k]]

if __name__ == "__main__":
    q = "新手容易犯什么错误？"
    hits = retrieve(q)
    print("问题：", q)
    print("检索到最相关的段落：")
    for h in hits:
        print(" -", h)