# 从被测文件里把 fake_score 和retrieve函数请过来
from step7_retrieve import fake_score, retrieve,chunks

# 测试函数：名字必须 test_ 开头，pytest 才认它
def test_fake_score():
    # 原来的普通情况
    assert fake_score("ab", "abc") == 2
    assert fake_score("xyz", "abc") == 0
    assert fake_score("aa", "abc") == 2
    # 新增：边界情况
    assert fake_score("", "abc") == 0      # question 为空
    assert fake_score("abc", "") == 0      # chunk 为空
    assert fake_score("aab", "ab") == 3    # 重复字符，验证不去重, "ab") 

def test_retrieve():
    # 性质1：默认 top_k=2，应返回 2 段
    assert len(retrieve("新手错误")) == 2
    # 性质2：top_k=3，应返回 3 段
    assert len(retrieve("新手错误", top_k=3)) == 3
    # 性质3：返回的每一段，都必须是知识库里本来就有的
    for seg in retrieve("新手错误"):
        assert seg in chunks