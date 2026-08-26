import { useEffect, useState } from 'react'
import LoginForm from './components/LoginForm'
import RegisterForm from './components/RegisterForm'
import TicketList from './components/TicketList'
import NewTicketForm from './components/NewTicketForm'
import { createTicket, getTickets, loginUser, registerUser, setAuthToken } from './api/client'

const decodeTokenPayload = (token) => {
  const payload = token.split('.')[1]
  const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
  const json = window.atob(normalized.padEnd(normalized.length + ((4 - normalized.length % 4) % 4), '='))
  return JSON.parse(json)
}

export default function App() {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)
  const [registering, setRegistering] = useState(false)
  const [loggingIn, setLoggingIn] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)
  const [registerMessage, setRegisterMessage] = useState('')
  const [loginMessage, setLoginMessage] = useState('')
  const [filter, setFilter] = useState('all')
  const [showNewTicket, setShowNewTicket] = useState(false)

  const fetchTickets = async () => {
    setFetching(true)
    try {
      const params = {}
      if (filter === 'mine') params.mine = true
      else if (filter === 'assigned') params.assigned = true
      else if (filter === 'related') params.related = true
      const result = await getTickets(params)
      setTickets(result)
    } finally {
      setFetching(false)
    }
  }

  useEffect(() => {
    if (currentUser) {
      fetchTickets()
    } else {
      setFetching(false)
    }
  }, [filter, currentUser])

  const handleCreate = async (payload) => {
    setLoading(true)
    try {
      await createTicket(payload)
      setShowNewTicket(false)
      await fetchTickets()
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (payload) => {
    setRegistering(true)
    setRegisterMessage('')
    try {
      const user = await registerUser(payload)
      setRegisterMessage(`已注册用户: ${user.username} (ID: ${user.id})，请登录后访问工单。`)
    } catch (error) {
      const message = error?.response?.data?.detail || '注册失败，请稍后重试'
      setRegisterMessage(String(message))
    } finally {
      setRegistering(false)
    }
  }

  const handleLogin = async (payload) => {
    setLoggingIn(true)
    setLoginMessage('')
    try {
      const result = await loginUser(payload)
      setAuthToken(result.access_token)
      const tokenPayload = decodeTokenPayload(result.access_token)
      setCurrentUser({ id: Number(tokenPayload.sub), username: tokenPayload.username })
      setLoginMessage(`已登录，Token 有效期 ${Math.floor(result.expires_in / 60)} 分钟。`)
      await fetchTickets()
    } catch (error) {
      setAuthToken(null)
      setCurrentUser(null)
      const message = error?.response?.data?.detail || '登录失败，请检查用户名和密码'
      setLoginMessage(String(message))
    } finally {
      setLoggingIn(false)
    }
  }

  // 未登录：只显示登录框和注册链接
  if (!currentUser) {
    return (
      <main className="page">
        <header>
          <h1>工单系统</h1>
          <p>快速记录问题、追踪状态并协作处理。</p>
        </header>
        <section style={{ maxWidth: '400px', margin: '2rem auto' }}>
          <LoginForm onLogin={handleLogin} loading={loggingIn} />
          {loginMessage && <p className="hint">{loginMessage}</p>}
          <div style={{ textAlign: 'center', marginTop: '1rem' }}>
            <span style={{ color: '#666' }}>还没有账号？</span>{' '}
            <a
              href="#register"
              onClick={(e) => {
                e.preventDefault()
                setShowNewTicket((v) => !v)
              }}
              style={{ color: '#0066cc', cursor: 'pointer' }}
            >
              点击注册
            </a>
          </div>
          {showNewTicket && (
            <>
              <RegisterForm onRegister={handleRegister} loading={registering} />
              {registerMessage && <p className="hint">{registerMessage}</p>}
            </>
          )}
        </section>
      </main>
    )
  }

  // 已登录：显示工单列表和新建工单按钮
  return (
    <main className="page">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>工单系统</h1>
          <p>欢迎，{currentUser.username} (ID: {currentUser.id})</p>
        </div>
        <button
          onClick={() => setShowNewTicket(!showNewTicket)}
          style={{
            padding: '0.6rem 1.2rem',
            borderRadius: '8px',
            border: 'none',
            background: '#0066cc',
            color: '#fff',
            fontSize: '1rem',
            cursor: 'pointer',
          }}
        >
          {showNewTicket ? '✕ 取消' : '+ 新建工单'}
        </button>
      </header>

      {showNewTicket && (
        <section style={{ marginBottom: '2rem' }}>
          <NewTicketForm onSubmit={handleCreate} loading={loading} creatorId={currentUser.id} />
        </section>
      )}

      <section>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ margin: 0 }}>我的工单</h2>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{ padding: '0.4rem 0.8rem', borderRadius: '6px', border: '1px solid #ddd', fontSize: '0.9rem' }}
          >
            <option value="all">全部工单</option>
            <option value="mine">我创建的</option>
            <option value="assigned">分配给我的</option>
            <option value="related">与我相关</option>
          </select>
        </div>
        {fetching ? <p>加载中...</p> : <TicketList tickets={tickets} />}
      </section>
    </main>
  )
}
