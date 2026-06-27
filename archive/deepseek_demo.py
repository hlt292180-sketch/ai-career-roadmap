"""
DeepSeek API 演示脚本
功能：调用 DeepSeek v4 API，发送"你好"，打印完整返回内容
用法：先设置环境变量 DEEPSEEK_API_KEY，然后运行 python deepseek_demo.py
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# 从环境变量读取 API Key（安全做法，避免硬编码）
api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    print("错误：未找到环境变量 DEEPSEEK_API_KEY")
    print("请先在该项目文件下创建.env文件:DEEPSEEK_API_KEY = '你的key' ")
    exit(1)

# 创建客户端，指向 DeepSeek API 地址
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",  # DeepSeek 兼容 OpenAI 接口
)

# 调用 DeepSeek v4，发送"你好"
response = client.chat.completions.create(
    model="deepseek-chat",  # DeepSeek v4 模型名
    messages=[
        {"role": "system", "content": """【角色】你是帮助程序员从0开始转ai应用开发的需求收敛师,只干收敛这件事 【任务】把用户的模糊输入,收敛成一个可衡量目标 【输入】用户会给:现有技能 / 目标程度 / 时长【输出要求】只输出 JSON,包含四个字段:

* 目标方向:RAG 应用、 Agent、有模型微调、AI 工具集成/...(只需给出一个)
* 动机:从输入识别动机倾向(就业导向/体系化转行/...)
* 指标:必须可验证——别人能判断"做到没有"（如能独立做出一个带 RAG 的问答应用并部署上线）
* 时间约束:（1周/1个月/...) 【关键规则】指标必须可衡量;只输出 JSON,不要多余的话(不要输出路线/不要讲怎么做)"""},
        {"role": "user", "content": """现有技能：会一点点python基础


目标程度：想要赚钱

时长：6个月"""},
    ],
)

# 打印完整返回内容
print("=== API 完整响应 ===")
print(response)
print("\n=== 只提取回复文本 ===")
print(response.choices[0].message.content)
print("\n=== token 用量 ===")
print(response.usage)