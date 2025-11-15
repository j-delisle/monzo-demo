import axios from 'axios'
import type { Account, Transaction, CreateTransaction, TopUpRule, CreateTopUpRule, TopUpEvent } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const accountsApi = {
  getAccounts: async (): Promise<Account[]> => {
    const response = await api.get('/accounts')
    return response.data
  },
  
  getAccount: async (accountId: string): Promise<Account> => {
    const response = await api.get(`/accounts/${accountId}`)
    return response.data
  },
}

export const transactionsApi = {
  getTransactions: async (accountId?: string): Promise<Transaction[]> => {
    const response = await api.get('/transactions', {
      params: accountId ? { account_id: accountId } : {}
    })
    return response.data
  },
  
  createTransaction: async (transaction: CreateTransaction): Promise<Transaction> => {
    const response = await api.post('/transactions', transaction)
    return response.data
  },
}

export const topUpApi = {
  getTopUpRules: async (accountId?: string): Promise<TopUpRule[]> => {
    const response = await api.get('/topup-rules', {
      params: accountId ? { account_id: accountId } : {}
    })
    return response.data
  },
  
  createTopUpRule: async (rule: CreateTopUpRule): Promise<TopUpRule> => {
    const response = await api.post('/topup-rules', rule)
    return response.data
  },
  
  getTopUpEvents: async (accountId?: string): Promise<TopUpEvent[]> => {
    const response = await api.get('/topup-events', {
      params: accountId ? { account_id: accountId } : {}
    })
    return response.data
  },
  
  triggerTopUp: async (accountId: string): Promise<{ triggered: boolean; message: string }> => {
    const response = await api.post('/trigger-topup', null, {
      params: { account_id: accountId }
    })
    return response.data
  },
}