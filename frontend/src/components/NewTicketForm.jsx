import { useState } from 'react'
import { useEffect } from 'react'

const INITIAL = {
  title: '',
  description: '',
  priority: 'medium'
}

export default function NewTicketForm({ onSubmit, loading, creatorId }) {
  const [form, setForm] = useState(INITIAL)

  useEffect(() => {
    if (!creatorId) {
      return
    }
    setForm((prev) => ({ ...prev, creator_id: creatorId }))
  }, [creatorId])

  const submit = async (event) => {
    event.preventDefault()
    if (!form.title.trim() || !form.description.trim() || !creatorId) {
      return
    }
    await onSubmit(form)
    setForm(INITIAL)
  }

  return (
    <form className="ticket-form" onSubmit={submit}>
      <h2>新建工单</h2>
      {!creatorId ? <p className="hint">请先注册用户后再创建工单。</p> : null}
      <label>
        标题
        <input
          value={form.title}
          onChange={(event) => setForm({ ...form, title: event.target.value })}
          placeholder="例如: 支付接口返回 500"
        />
      </label>
      <label>
        描述
        <textarea
          value={form.description}
          onChange={(event) => setForm({ ...form, description: event.target.value })}
          placeholder="描述复现步骤、期望结果与实际结果"
          rows={4}
        />
      </label>
      <label>
        优先级
        <select
          value={form.priority}
          onChange={(event) => setForm({ ...form, priority: event.target.value })}
        >
          <option value="low">low</option>
          <option value="medium">medium</option>
          <option value="high">high</option>
          <option value="urgent">urgent</option>
        </select>
      </label>
      <button disabled={loading || !creatorId} type="submit">{loading ? '提交中...' : '创建工单'}</button>
    </form>
  )
}
