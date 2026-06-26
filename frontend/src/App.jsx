import { useState } from 'react'

function App() {
  const [userInput, setUserInput] = useState('')
  const [route, setRoute] = useState(null)

  const handleClick = async () => {
    const res = await fetch('http://localhost:5000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: userInput }),
    })
    const data = await res.json()
    setRoute(data)
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
      <button onClick={handleClick}>生成路线</button>

      {route && route.阶段列表.map((阶段) => (
        <div key={阶段.阶段序号}>
          <h3>阶段 {阶段.阶段序号}：{阶段.主题}</h3>
          <p>具体内容：{阶段.具体内容}</p>
          <p>阶段时长：{阶段.阶段时长}</p>
          <p>下一步：{阶段.下一步指引}</p>
        </div>
      ))}
    </div>
  )
}

export default App