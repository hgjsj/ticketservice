import { useState } from 'react'

export default function RegisterForm({ onRegister, loading }) {
  const [form, setForm] = useState({ username: '', password: '', phone_number: '', department: '' })

  const submit = async (event) => {
    event.preventDefault()
    if (!form.username.trim() || !form.password.trim()) {
      return
    }
    await onRegister(form)
  }

  return (
    <form className="auth-form" onSubmit={submit}>
      <h2>注册用户</h2>
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
      <label>
        电话号码
        <input
          value={form.phone_number}
          onChange={(event) => setForm({ ...form, phone_number: event.target.value })}
          placeholder="可选"
        />
      </label>
      <label>
        部门
        <input
          value={form.department}
          onChange={(event) => setForm({ ...form, department: event.target.value })}
          placeholder="可选"
        />
      </label>
      <button disabled={loading} type="submit">
        {loading ? '注册中...' : '注册并使用该用户'}
      </button>
    </form>
  )
}