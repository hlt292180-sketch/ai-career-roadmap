import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import httpx


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    http_client=httpx.Client(trust_env=False)
)

def call_llm(prompt):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"} #强制模型只输出合法 JSON
        
    )
    return response.choices[0].message.content

# 第一段:收敛目标 → 四字段 JSON
def converge_goal(user_input):
    prompt = f"""【角色】你是帮助程序员从0开始转ai应用开发的需求收敛师,只干收敛这件事 【任务】把用户的模糊输入,收敛成一个可衡量目标 【输入】用户会给:现有技能 / 目标程度 / 时长【输出要求】只输出 JSON,包含四个字段:

* 目标方向:RAG 应用、 Agent、有模型微调、AI 工具集成/...(只需给出一个)
* 动机:从输入识别动机倾向(就业导向/体系化转行/...)
* 指标:必须可验证——别人能判断"做到没有"（如能独立做出一个带 RAG 的问答应用并部署上线）
* 时间约束:（1周/1个月/...) 【关键规则】指标必须可衡量;只输出 JSON,不要多余的话(不要输出路线/不要讲怎么做)

用户输入是:{user_input}"""
    raw = call_llm(prompt)
    return json.loads(raw)

# 第二段:用收敛结果 → 生成路线
def generate_route(goal_json):
    prompt = """角色：你是ai应用开发培训路线规划师，你需要拿着收敛好的目标，生成分阶段路线。任务：把收敛好的目标，拆分成一条分阶段，可执行的转型路线。输入：你会收到一个包含目标方向，动机，指标，时间约束的json数据。输出格式：嵌套结构：外层阶段列表数组。每个阶段五个字段（阶段序号/主题（这阶段学什么）/具体内容（具体知识点/任务）/阶段时长（这阶段花多久）/下一步指引（一句人话怎么下手））。关键规则：动机影响骨架（就业导向 → 偏实战、早出作品
体系化转行 → 偏基础、成体系
其它/兜底 → 均衡（基础+实战兼顾）），阶段数范围（3-6个阶段）（阶段数由你按时长定），阶段时长要对齐总时间（各阶段时长加起来不超过用户的时间约束。），下一步指引的调性（用减压、鼓励的口吻，只给最小起步动作，不要罗列一堆任务。），只输出 JSON（不要多余的话、不要 ```json 包裹）"""   # ← 这里填你动作③的路线生成 prompt
    max_retries = 3   # 最多试 3 次，防止模型一直不听话导致死循环
    for attempt in range(max_retries):
        raw = call_llm(prompt)
        arr = json.loads(raw)
        if 3 <= len(arr) <= 6:
            return {"阶段列表": arr}   # 合规，直接返回，不再重试
        # 不合规：什么都不做，循环会自动进入下一次重试

    # 循环跑完 3 次还没返回，说明 3 次都不合规，放弃
    return {"阶段列表": [], "error": f"重试{max_retries}次后阶段数仍不符合要求"}


def generate_route_exam(route):
    arr = route["阶段列表"]

    # 规则一：阶段数 3-6，不在范围就 return False
    if not (3 <= len(arr) <= 6): 
        return False

    # 规则二：每个阶段都得有这五个字段
    ziduan = ["阶段序号", "主题", "具体内容", "阶段时长", "下一步指引"]
    for i in arr:
        for k in ziduan:
            if k not in i:
                return False

    # 两条都过了
    return True
    
if __name__ == "__main__":

    inputs = [
        "我是应届软件工程毕业生,想转AI应用开发,只想先就业",
        "我是会计,想转数据分析,有半年时间",
        "零基础想学Python做自动化办公,业余学",
        "前端工程师想补后端能力,想系统转全栈",
        "做了两年测试,想转开发,时间紧",
    ]

    results = []                    # 循环前：准备一个空列表装结果

    for user_input in inputs:
        print("=" * 40)
        print("原始输入:", user_input)
        try:
            goal = converge_goal(user_input)
            route = generate_route(goal)
            是否合格 = generate_route_exam(route)
            print("是否合格:", 是否合格)
            print("路线:", route)
        except Exception as e:
            print("这条崩了:", e)
            是否合格 = False          # 崩了就算失败
        results.append(是否合格)       # 不管过没过、崩没崩，都记一笔
    print(f"总共:{len(results)}条")
    print(f"通过了{results.count(True)}条")
    print(f"失败了{len(results) - results.count(True)}条")
