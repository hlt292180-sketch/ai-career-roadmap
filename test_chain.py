from unittest.mock import patch
import json
import step4_chain   # 导入整个模块，方便等下替换它里面的 call_llm
import pytest
def test_generate_route_normal():
    # 1. 准备一段“假装是大模型返回”的 JSON 字符串（正常情况）
    fake_llm_return = json.dumps([
        {"阶段序号": 1, "主题": "Python基础", "具体内容": "语法",
         "阶段时长": "1周", "下一步指引": "先写个小脚本"}
    ], ensure_ascii=False)

    # 2. 用 patch 把 step4_chain 里的 call_llm 临时替换掉：
    #    不管传什么 prompt，都直接返回上面那段假字符串，不真调 API
    with patch.object(step4_chain, "call_llm", return_value=fake_llm_return):
        result = step4_chain.generate_route({"目标方向": "RAG"})

    # 3. 验证那三条“确定性质”
    assert "阶段列表" in result              # 有“阶段列表”字段
    assert isinstance(result["阶段列表"], list)   # 它是个 list
    assert len(result["阶段列表"]) > 0        # 非空



def test_generate_route_dirty_return():
    # 准备一段“脏”的假返回——根本不是合法 JSON
    dirty_return = "好的，这是你的学习路线：（然后模型忘了输出JSON）"

    # 预期：喂脏数据时，json.loads 会抛 JSONDecodeError
    with patch.object(step4_chain, "call_llm", return_value=dirty_return):
        with pytest.raises(json.JSONDecodeError):
            step4_chain.generate_route({"目标方向": "RAG"})