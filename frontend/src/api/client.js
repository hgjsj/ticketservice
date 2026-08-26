import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || ''
})

export const setAuthToken = (token) => {
  if (token) {
    client.defaults.headers.common.Authorization = `Bearer ${token}`
    return
  }
  delete client.defaults.headers.common.Authorization
}

export const getTickets = async (params = {}) => {
  const { data } = await client.get('/api/ticket/tickets', { params })
  return data
}

export const createTicket = async (payload) => {
  const { data } = await client.post('/api/ticket/tickets', payload)
  return data
}

export const registerUser = async (payload) => {
  const { data } = await client.post('/api/auth/register', payload)
  return data
}

export const loginUser = async (payload) => {
  const { data } = await client.post('/api/auth/login', payload)
  return data
}
