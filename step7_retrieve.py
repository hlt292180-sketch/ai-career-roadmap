import os
import numpy as np
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from knowledge import KNOWLEDGE

# ===== 1. 初始化：加载环境变量 + 创建智谱客户端 =====
load_dotenv()

zhipu = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    http_client=httpx.Client(trust_env=False)   # 防止 Windows 代理干扰
)

# ===== 2. 知识库切分（和之前一样，按换行切） =====
chunks = [line.strip() for line in KNOWLEDGE.strip().split("\n") if line.strip()]


# ===== 3. Embedding 函数：把一段文字变成向量 =====
def embed(text):
    """
    调用智谱 embedding-3 模型，把文字变成向量（一串浮点数）
    返回：list[float]，大概 1024 个浮点数
    """
    resp = zhipu.embeddings.create(
        model="embedding-3",
        input=text
    )
    return resp.data[0].embedding


# ===== 4. 余弦相似度：算两个向量"有多像" =====
def cosine_sim(vec_a, vec_b):
    """
    余弦相似度 = 两个向量的内积 / (它们各自长度的乘积)
    结果在 -1 到 1 之间，越接近 1 表示方向越一致（语义越相近）

    用大白话说：
    - 你想象两个箭头从原点出发
    - 两个箭头指的方向越接近，余弦值越大
    - 完全同方向 = 1，垂直 = 0，完全反方向 = -1
    """
    a = np.array(vec_a)
    b = np.array(vec_b)
    # np.dot = 内积（两个向量逐位相乘再加起来）
    # np.linalg.norm = 向量的长度（欧几里得范数）
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ===== 5. 懒加载索引：第一次用到时才把知识库转成向量（之后复用缓存） =====
# 之前这里是模块顶层直接 embed，导致"一 import 就联网打 14 次 API"。
# 改成缓存 + 懒加载后：import 不干活，第一次调 retrieve 才构建索引。
_chunk_vecs = None   # 模块级缓存，初始为空（None 表示"还没构建过"）


def _ensure_index():
    """确保知识库向量已构建。第一次调用时 embed 全部片段，之后直接返回缓存。"""
    global _chunk_vecs
    if _chunk_vecs is None:                       # 只有第一次（或被重置后）才进来
        print(f"正在把知识库（{len(chunks)} 条）转成向量...")
        _chunk_vecs = [embed(c) for c in chunks]  # 每条调一次 API
        print(f"完成！每个向量 {len(_chunk_vecs[0])} 维")
    return _chunk_vecs


# ===== 6. 检索函数（新的！用向量相似度替代字符重合） =====
def retrieve(question, top_k=2):
    """
    输入：用户问题 + 想要返回几条
    输出：最相关的 top_k 条知识片段（list[str]）

    流程：
    1. 确保知识库向量已就绪（懒加载）
    2. 把问题转成向量（调一次 API）
    3. 算问题向量和每个片段向量的余弦相似度
    4. 按相似度从高到低排序，返回 top_k 条
    """
    # 1. 确保索引就绪（第一次会构建，之后直接拿缓存）
    chunk_vecs = _ensure_index()

    # 2. 问题 → 向量
    q_vec = embed(question)

    # 3. 逐一算相似度
    scores = [cosine_sim(q_vec, cv) for cv in chunk_vecs]

    # 3. 按分数从高到低排序，取 top_k 的索引
    #    np.argsort 返回从小到大排序的索引，[::-1] 反转变成从大到小
    ranked = np.argsort(scores)[::-1]

    # 4. 返回对应的原文片段
    return [chunks[i] for i in ranked[:top_k]]


# ===== 7. 自己跑一下看效果 =====
if __name__ == "__main__":
    test_questions = [
        "新手容易犯什么错误？",
        "怎么选大模型API？",
        "RAG和Agent有什么区别？",
        "面试作品集应该怎么做？",
    ]

    for q in test_questions:
        print("\n" + "=" * 50)
        print("问题：", q)
        print("-" * 50)
        hits = retrieve(q, top_k=3)
        for i, h in enumerate(hits):
            # 只显示前 60 个字预览
            preview = h[:80] + "..." if len(h) > 80 else h
            print(f"  #{i+1} {preview}")
