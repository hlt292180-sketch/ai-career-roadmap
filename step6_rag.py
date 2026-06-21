import httpx, os
from openai import OpenAI
from dotenv import load_dotenv
from knowledge import KNOWLEDGE

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    http_client=httpx.Client(trust_env=False)
)

def ask_with_knowledge(question):
    prompt = f"""请只根据下面提供的资料回答用户的问题。
如果资料里没有相关内容，就说"资料中没有提到"，不要编造。

资料：
{KNOWLEDGE}

用户问题：{question}"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print(ask_with_knowledge("Python之父是谁？"))
