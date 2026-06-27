import { useState } from 'react'

function App() {
  const [userInput, setUserInput] = useState('')
  const [route, setRoute] = useState(null)
  const [loading, setLoading] = useState(false)      // 新增：是否正在生成

  const handleClick = async () => {
    setLoading(true)                                  // 开始：进入加载状态
    setRoute(null)                                    // 清掉上次的结果
    const res = await fetch('http://localhost:5000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: userInput }),
    })
    const data = await res.json()
    setRoute(data)
    setLoading(false)                                 // 结束：退出加载状态
  }

  return (
    <div>
      <h1>AI 转型路线规划</h1>
      <textarea
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        placeholder="比如：我是会计，想转数据分析，有半年时间"
        rows={4}
      />
      <br />
      <button onClick={handleClick} disabled={loading}>
        {loading ? '生成中…' : '生成路线'}
      </button>

      {route && route.阶段列表.map((阶段) => (
        <div
          key={阶段.阶段序号}
          style={{
            border: '1px solid #ddd',
            borderRadius: 8,
            padding: 16,
            marginTop: 12,
            backgroundColor: '#fafafa',
          }}
        >
          <h3 style={{ marginTop: 0, color: '#2563eb' }}>
            阶段 {阶段.阶段序号}：{阶段.主题}
          </h3>
          <p>具体内容：{阶段.具体内容}</p>
          <p>阶段时长：{阶段.阶段时长}</p>
          <p>下一步：{阶段.下一步指引}</p>
        </div>
      ))}
    </div>
  )
}

export default App