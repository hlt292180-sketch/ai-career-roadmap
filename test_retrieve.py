# 测试检索模块 step7_retrieve
# 注意：retrieve 会调用智谱 embedding API（联网+花钱），
# 所以测试里用 mock 把 embed 换成"假向量"，做到不联网也能测排序逻辑。
from unittest.mock import patch
import step7_retrieve
from step7_retrieve import cosine_sim, retrieve, chunks


# ===== 测纯函数 cosine_sim：输入向量、输出相似度，确定且无网络 =====
def test_cosine_sim():
    # 同方向 → 1（完全相似）
    assert cosine_sim([1, 0], [1, 0]) == 1.0
    # 同方向但长度不同 → 还是 1（余弦只看方向，不看长度）
    assert cosine_sim([1, 0], [5, 0]) == 1.0
    # 垂直 → 0（毫不相关）
    assert cosine_sim([1, 0], [0, 1]) == 0.0
    # 反方向 → -1（完全相反）
    assert cosine_sim([1, 0], [-1, 0]) == -1.0


# ===== 测 retrieve：用 mock 喂假向量，验证返回数量、来源、排序 =====
def test_retrieve():
    # 造一个"假知识库向量表"：只让第 0 条 = [1,0,0]，其余全 = [0,1,0]。
    # 这样问题向量 [1,0,0] 和第 0 条相似度=1（唯一最高），其余都=0，
    # 排序结果确定，不会出现并列第一导致 argsort 顺序不稳定。
    fake_chunk_vecs = [[0, 1, 0] for _ in chunks]
    fake_chunk_vecs[0] = [1, 0, 0]

    # 直接把缓存塞好，跳过真实 embedding（_ensure_index 看到非 None 就不联网了）
    step7_retrieve._chunk_vecs = fake_chunk_vecs

    try:
        # 让"问题向量"= [1,0,0]，它和所有第 0 类（i%3==0）的片段最相似
        with patch.object(step7_retrieve, "embed", return_value=[1, 0, 0]):
            # 性质1：默认 top_k=2，返回 2 段
            hits = retrieve("任意问题")
            assert len(hits) == 2
            # 性质2：top_k=3，返回 3 段
            assert len(retrieve("任意问题", top_k=3)) == 3
            # 性质3：返回的每一段都必须来自原知识库
            for seg in hits:
                assert seg in chunks
            # 性质4：排在第一的，必须是和问题向量最相似的那条（chunks[0]）
            assert hits[0] == chunks[0]
    finally:
        # 测试后把缓存清掉，不影响别的测试/真实运行
        step7_retrieve._chunk_vecs = None
