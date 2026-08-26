import { useState } from 'react'

export default function LoginForm({ onLogin, loading }) {
  const [form, setForm] = useState({ username: '', password: '' })

  const submit = async (event) => {
    event.preventDefault()
    if (!form.username.trim() || !form.password.trim()) {
      return
    }
    await onLogin(form)
  }

  return (
    <form className="auth-form" onSubmit={submit}>
      <h2>登录</h2>
      <label>
        用户名
        <input
          value={form.username}
          onChange={(event) => setForm({ ...form, username: event.target.value })}
          placeholder="例如: alice"
        />
      </label>
      <label>
        密码
        <input
          type="password"
          value={form.password}
          onChange={(event) => setForm({ ...form, password: event.target.value })}
          placeholder="输入密码"
        />
      </label>
      <button disabled={loading} type="submit">
        {loading ? '登录中...' : '登录并获取 Token'}
      </button>
    </form>
  )
}