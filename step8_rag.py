import httpx, os
from openai import OpenAI
from dotenv import load_dotenv
from step7_retrieve import retrieve   # 借用上一步写好的检索

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    http_client=httpx.Client(trust_env=False)
)

def rag_answer(question):
    # 1. 检索：只拿最相关的几段
    hits = retrieve(question, top_k=2)
    context = "\n".join(hits)

    # 2. 把检索到的段落 + 问题，拼进 prompt
    prompt = f"""请只根据下面提供的资料回答用户的问题。
如果资料里没有相关内容，就说"资料中没有提到"，不要编造。

资料：
{context}

用户问题：{question}"""

    # 3. 生成
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    q = "新手容易犯什么错误？"
    print(rag_answer(q))