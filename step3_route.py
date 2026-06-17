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
        {"role": "system", "content": """角色：你是ai应用开发培训路线规划师，你需要拿着收敛好的目标，生成分阶段路线。任务：把收敛好的目标，拆分成一条分阶段，可执行的转型路线。输入：你会收到一个包含目标方向，动机，指标，时间约束的json数据。输出格式：嵌套结构：外层阶段列表数组。每个阶段五个字段（阶段序号/主题（这阶段学什么）/具体内容（具体知识点/任务）/阶段时长（这阶段花多久）/下一步指引（一句人话怎么下手））。关键规则：动机影响骨架（就业导向 → 偏实战、早出作品





体系化转行 → 偏基础、成体系



其它/兜底 → 均衡（基础+实战兼顾）），阶段数范围（3-6个阶段）（阶段数由你按时长定），阶段时长要对齐总时间（各阶段时长加起来不超过用户的时间约束。），下一步指引的调性（用减压、鼓励的口吻，只给最小起步动作，不要罗列一堆任务。），只输出 JSON（不要多余的话、不要 ```json 包裹）

"""},
        {"role": "user", "content": """现有技能：{
  "目标方向": "RAG 应用",
  "动机": "体系化转行",
  "指标": "改成不那么赶的，像"系统掌握 AI 应用开发的核心知识体系，能讲清 RAG 原理并独立实现"",
  "时间约束": "6个月"
}"""},
    ],
)

# 打印完整返回内容
print("=== API 完整响应 ===")
print(response)
print("\n=== 只提取回复文本 ===")
print(response.choices[0].message.content)
print("\n=== token 用量 ===")
print(response.usage)