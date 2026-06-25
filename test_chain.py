from unittest.mock import patch
import json
import step4_chain   # 导入整个模块，方便等下替换它里面的 call_llm
import pytest
def test_generate_route_normal():
    # 1. 准备一段“假装是大模型返回”的 JSON 字符串（正常情况：4个阶段，符合3-6）
    fake_llm_return = json.dumps([
        {"阶段序号": 1, "主题": "Python基础", "具体内容": "语法", "阶段时长": "1周", "下一步指引": "先写个小脚本"},
        {"阶段序号": 2, "主题": "Flask入门", "具体内容": "接口", "阶段时长": "1周", "下一步指引": "搭个hello world"},
        {"阶段序号": 3, "主题": "调大模型API", "具体内容": "对接", "阶段时长": "1周", "下一步指引": "先调通一次"},
        {"阶段序号": 4, "主题": "做个小项目", "具体内容": "整合", "阶段时长": "1周", "下一步指引": "拼起来跑通"}
    ], ensure_ascii=False)

    with patch.object(step4_chain, "call_llm", return_value=fake_llm_return):
        result = step4_chain.generate_route({"目标方向": "RAG"})

    assert "阶段列表" in result
    assert isinstance(result["阶段列表"], list)
    assert len(result["阶段列表"]) > 0

def test_generate_route_dirty_return():
    # 准备一段“脏”的假返回——根本不是合法 JSON
    dirty_return = "好的，这是你的学习路线：（然后模型忘了输出JSON）"

    # 预期：喂脏数据时，json.loads 会抛 JSONDecodeError
    with patch.object(step4_chain, "call_llm", return_value=dirty_return):
        with pytest.raises(json.JSONDecodeError):
            step4_chain.generate_route({"目标方向": "RAG"})

def test_generate_route_too_few_stages():
    # 准备一段“合法 JSON、但只有 2 个阶段”的假返回（违反 3-6 约束）
    # 注意：这是真正的 JSON 数组，能被 json.loads 正常解析，不会崩
    too_few = json.dumps([
        {"阶段序号": 1, "主题": "A", "具体内容": "x", "阶段时长": "1周", "下一步指引": "先做x"},
        {"阶段序号": 2, "主题": "B", "具体内容": "y", "阶段时长": "1周", "下一步指引": "再做y"}
    ], ensure_ascii=False)

    # 喂给 generate_route，看它怎么处理
    with patch.object(step4_chain, "call_llm", return_value=too_few):
        result = step4_chain.generate_route({"目标方向": "RAG"})

    # 现状已改变：加了校验后，2个阶段会被拦下，返回空列表 + error 字段
    assert result["阶段列表"] == []          # 阶段列表被清空
    assert "error" in result                 # 返回里带了 error 字段