export default function TicketList({ tickets }) {
  if (!tickets.length) {
    return <p className="empty">暂无工单。</p>
  }

  return (
    <ul className="ticket-list">
      {tickets.map((ticket) => (
        <li key={ticket.id} className="ticket-card">
          <div className="ticket-head">
            <h3>{ticket.title}</h3>
            <span className={`badge badge-${ticket.status}`}>{ticket.status}</span>
          </div>
          <p>{ticket.description}</p>
          <div className="ticket-foot">
            <span>优先级: {ticket.priority}</span>
            <span>创建人ID: {ticket.creator_id}</span>
            {ticket.assignee_id ? <span>分配给: {ticket.assignee_id}</span> : <span style={{ color: '#999' }}>未分配</span>}
          </div>
        </li>
      ))}
    </ul>
  )
}
