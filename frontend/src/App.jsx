import { useState } from 'react'
import './App.css'

/* 示例 placeholder 文本，引导用户 */
const PLACEHOLDER = `说说你的情况，例如：
"我是 Java 后端开发，有 2 年经验，想转 AI 应用开发方向，有 3 个月时间"`

const ASK_PLACEHOLDER = `问点关于 AI 转型的问题，例如：
"新手最容易犯什么错误？" / "大模型 API 怎么选？"`

function App() {
  const [tab, setTab] = useState('route')   // 当前标签页：route=路线规划 / ask=知识库问答

  // ===== 路线规划状态 =====
  const [userInput, setUserInput] = useState('')
  const [route, setRoute] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [hasSearched, setHasSearched] = useState(false)

  // ===== 知识库问答状态 =====
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [askLoading, setAskLoading] = useState(false)
  const [askError, setAskError] = useState(null)

  // ===== 路线规划：调 /generate =====
  const handleGenerate = async () => {
    const trimmed = userInput.trim()
    if (!trimmed) return

    setLoading(true)
    setError(null)
    setRoute(null)
    setHasSearched(true)

    try {
      const res = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: trimmed }),
      })

      if (!res.ok) {
        throw new Error(`服务器返回 ${res.status}，请确认 Flask 已启动`)
      }

      const data = await res.json()

      if (data.error) {
        setError(data.error)
        setRoute(null)
      } else if (!data.阶段列表 || data.阶段列表.length === 0) {
        setError('模型未能生成有效路线，请换个说法再试一次')
        setRoute(null)
      } else {
        setRoute(data)
      }
    } catch (err) {
      setError(
        err.message === 'Failed to fetch'
          ? '无法连接到后端服务，请确认 Flask 已启动（python app.py）'
          : err.message
      )
    } finally {
      setLoading(false)
    }
  }

  // ===== 知识库问答：调 /ask =====
  const handleAsk = async () => {
    const trimmed = question.trim()
    if (!trimmed) return

    setAskLoading(true)
    setAskError(null)
    setAnswer(null)

    try {
      const res = await fetch('http://localhost:5000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmed }),
      })

      if (!res.ok) {
        throw new Error(`服务器返回 ${res.status}，请确认 Flask 已启动`)
      }

      const data = await res.json()
      if (data.error) {
        setAskError(data.error)
      } else {
        setAnswer(data.answer)
      }
    } catch (err) {
      setAskError(
        err.message === 'Failed to fetch'
          ? '无法连接到后端服务，请确认 Flask 已启动（python app.py）'
          : err.message
      )
    } finally {
      setAskLoading(false)
    }
  }

  /* 回车快捷发送（Shift+Enter 换行） */
  const makeKeyDownHandler = (fn) => (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      fn()
    }
  }

  return (
    <div className="app">
      {/* ===== Header ===== */}
      <header className="header">
        <h1 className="header-title">
          你的<span className="accent">AI 转型</span>路线图
        </h1>
        <p className="header-sub">
          基于 RAG 知识库，AI 帮你规划学习路径、解答转型疑问
        </p>
      </header>

      {/* ===== 标签页切换 ===== */}
      <div className="tabs">
        <button
          className={`tab${tab === 'route' ? ' active' : ''}`}
          onClick={() => setTab('route')}
        >
          路线规划
        </button>
        <button
          className={`tab${tab === 'ask' ? ' active' : ''}`}
          onClick={() => setTab('ask')}
        >
          知识库问答
        </button>
      </div>

      {/* ============ 标签页一：路线规划 ============ */}
      {tab === 'route' && (
        <>
          <div className="input-card">
            <span className="input-label">你的现状 & 目标</span>
            <textarea
              className="input-textarea"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyDown={makeKeyDownHandler(handleGenerate)}
              placeholder={PLACEHOLDER}
              rows={4}
            />
            <button
              className={`generate-btn${loading ? ' loading' : ''}`}
              onClick={handleGenerate}
              disabled={loading || !userInput.trim()}
            >
              {loading ? '正在生成路线…' : '✦ 生成路线'}
            </button>
          </div>

          {/* 加载骨架屏 */}
          {loading && (
            <div className="skeleton-list">
              {[1, 2, 3].map((i) => (
                <div className="skeleton-card" key={i}>
                  <div className="skeleton-line short" />
                  <div className="skeleton-line medium" />
                  <div className="skeleton-line long" />
                  <div className="skeleton-line medium" />
                </div>
              ))}
            </div>
          )}

          {/* 错误提示 */}
          {error && <div className="error-box">⚠ {error}</div>}

          {/* 结果区：阶段时间线 */}
          {route && route.阶段列表 && route.阶段列表.length > 0 && (
            <section className="result-section">
              <h2 className="result-header">你的学习路线</h2>
              <div className="timeline">
                {route.阶段列表.map((阶段) => (
                  <div className="stage-card" key={阶段.阶段序号}>
                    <div className="stage-header">
                      <span className="stage-badge">{阶段.阶段序号}</span>
                      <h3 className="stage-title">{阶段.主题}</h3>
                    </div>
                    <p className="stage-body">{阶段.具体内容}</p>
                    <div className="stage-footer">
                      <span className="stage-duration">{阶段.阶段时长}</span>
                      <span className="stage-next">{阶段.下一步指引}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* 空状态 */}
          {!loading && !error && !route && !hasSearched && (
            <div className="empty-state">
              <div className="empty-icon">🌌</div>
              <p>
                在上方输入你的职业现状和目标
                <br />
                AI 将结合知识库为你规划分阶段学习路线
              </p>
            </div>
          )}
        </>
      )}

      {/* ============ 标签页二：知识库问答 ============ */}
      {tab === 'ask' && (
        <>
          <div className="input-card">
            <span className="input-label">向知识库提问</span>
            <textarea
              className="input-textarea"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={makeKeyDownHandler(handleAsk)}
              placeholder={ASK_PLACEHOLDER}
              rows={3}
            />
            <button
              className={`generate-btn${askLoading ? ' loading' : ''}`}
              onClick={handleAsk}
              disabled={askLoading || !question.trim()}
            >
              {askLoading ? '正在检索回答…' : '✦ 提问'}
            </button>
          </div>

          {/* 加载骨架屏 */}
          {askLoading && (
            <div className="skeleton-list" style={{ paddingLeft: 0 }}>
              <div className="skeleton-card">
                <div className="skeleton-line long" />
                <div className="skeleton-line medium" />
                <div className="skeleton-line long" />
              </div>
            </div>
          )}

          {/* 错误提示 */}
          {askError && <div className="error-box">⚠ {askError}</div>}

          {/* 回答区 */}
          {answer && (
            <section className="result-section">
              <h2 className="result-header">基于知识库的回答</h2>
              <div className="answer-card">{answer}</div>
              <p className="answer-note">
                ✦ 此回答只依据知识库内容生成，资料中没有的会如实说明
              </p>
            </section>
          )}

          {/* 空状态 */}
          {!askLoading && !askError && !answer && (
            <div className="empty-state">
              <div className="empty-icon">📚</div>
              <p>
                向知识库提一个关于 AI 转型的问题
                <br />
                系统会先检索最相关的资料，再据此回答（RAG）
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default App
