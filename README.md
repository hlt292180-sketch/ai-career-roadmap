# 程序员转 AI 应用开发——路线拆解工具

求职作品集项目，展示三项核心能力：**RAG + AI 编排 + 测试**。

输入一句模糊的职业转型想法（如"我是应届生，想转 AI 应用开发"），先收敛为结构化目标，再生成 3-6 个阶段的可执行学习路线——每阶段带具体知识点和"下一步该做什么"的指引。

**技术栈**：Python · Flask · DeepSeek API（`deepseek-chat`）· pytest

---

## 核心链路

```
用户输入 → converge_goal（收敛目标）→ generate_route（生成路线）→ 分阶段路线输出
                              ↑
                     RAG 知识库检索（可选）
```

两步 LLM 链式编排，中间可接入 RAG 检索知识库为路线生成提供参考依据。

| 步骤 | 函数 | 输入 | 输出 |
|------|------|------|------|
| 1 收敛 | `converge_goal()` | 模糊自然语言 | 结构化目标 JSON（方向/动机/指标/时长） |
| 2 生成 | `generate_route()` | 收敛目标 JSON | 3-6 阶段路线数组（每阶段 5 字段） |

---

## 已完成进度

### 第 1 周：链式编排 ✅
- DeepSeek API 调通
- 收敛目标 prompt + 生成路线 prompt
- 两步串成链，套 Flask 接口（`/generate`、`/ask`）

### 第 2 周：RAG 接入 ✅
- 伪 RAG（全量知识库塞 prompt）→ 验证"有据才答"机制可靠
- 朴素检索（字符重合度假 embedding）→ 验证检索管线
- 真 RAG（检索 + 生成）接入 Flask，跑通端到端
- **eval 关键发现**：假 embedding 不懂语义、只看字符重合，同义不同词时检索失败 → 已换真 embedding（DeepSeek Embedding API）

### 第 3 周：测试体系 🔄
- ✅ 动作①：pytest 单元测试入门（`test_retrieve.py`：`fake_score` 边界 + `retrieve` 合法性）
- ✅ 动作②：理解 LLM 输出怎么测（规则校验 > 精确匹配）
- ✅ 动作③：`generate_route_exam()` 自动化结构校验——阶段数 3-6 + 五个必填字段名校验
- ✅ 动作④：批量执行 5 条输入 + 自动统计通过/失败 + `try/except` 防单条崩溃拖垮整批
- 🔄 动作⑤：整理 README + 求职材料

---

## 测试体系

### 做了什么

用 **pytest** 给核心函数写自动化测试，覆盖正常路径、边界情况和异常路径：

- **纯函数测试**：`fake_score` 的边界（空字符串、重复字符）、`retrieve` 的返回数量和合法性
- **Mock 隔离 LLM**：用 `unittest.mock.patch` 替换 `call_llm`，不花 API 钱、不受网络波动影响
- **结构校验**：`generate_route_exam()` 自动检查每个输出的阶段数和字段名是否符合规范
- **批量验证**：5 条典型用户输入批量跑，自动统计通过率
- **重试机制**：阶段数不合规时自动重试（上限 3 次），`test_generate_route_retry_success` 验证重试生效

### 跑测试

```bash
pytest test_chain.py test_retrieve.py -v
```

### 批量跑暴露的真实问题

这些不是"我猜可能会出问题"，而是代码自动校验真跑出来的：

| # | 发现 |
|---|------|
| 1 | 模型字段名中英文不统一——常吐 `stage`/`topic` 而非中文五字段，导致校验不通过 |
| 2 | `converge_goal` 疑似没把 `user_input` 拼进 prompt，不同输入收敛结果雷同 |
| 3 | 模型偶发吐非法 JSON（缺逗号、引号不配对），`json.loads` 直接崩溃 |

---

## 项目结构

```
大切小/
├── app.py                # Flask 服务器（/generate、/ask）
├── step4_chain.py        # 核心链式编排（converge_goal → generate_route）
├── step7_retrieve.py     # 朴素检索（字符重合度假 embedding）
├── step8_rag.py          # 真 RAG 问答（检索 + LLM 生成）
├── step6_rag.py          # 伪 RAG（全量知识库直塞 prompt）
├── knowledge.py          # 知识库（6 条 AI 转型入门知识）
├── test_chain.py         # 链式编排 pytest 测试（4 个 case）
├── test_retrieve.py      # 检索模块 pytest 测试（2 个 case）
├── plan.md               # 开发计划 + 已知问题追踪
├── .env                  # DeepSeek API Key（已 gitignore）
└── .gitignore
```

---

## 快速开始

```bash
# 1. 安装依赖
pip install flask openai pytest

# 2. 配置 API Key（.env 文件）
DEEPSEEK_API_KEY=你的key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 3. 启动 Flask
python app.py

# 4. 调用接口
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"user_input": "我想从Java后端转AI应用开发，有3个月时间"}'
```

---

## 已知待办

详见 [plan.md](plan.md)，当前 14 条待调优项中重点：

- 阶段时长之和超总时长约束（数值校验）
- `converge_goal` user_input 拼接排查
- prompt 钉死中文字段名防止漂移
- 坏 JSON 根因根治（prompt / 后处理层面）
- 前端（React）尚未启动

---

*项目持续迭代中，每一次 commit 记录一个可验证的进展。*
