const BASE = 'http://localhost:5001/api/chat'

export async function sendChatMessage(messages, context = '') {
  const res = await fetch(`${BASE}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, context }),
  })
  if (!res.ok) throw new Error('Chat request failed')
  return res.json()
}
