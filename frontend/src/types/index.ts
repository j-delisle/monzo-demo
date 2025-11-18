export interface Account {
  id: number
  uuid: string
  name: string
  balance: number
  user_id: number
}

export interface Transaction {
  id: string
  account_id: string
  amount: number
  merchant: string
  description: string
  category: string | null
  transaction_type: 'debit' | 'credit'
  timestamp: string
}

export interface CreateTransaction {
  account_id: number
  amount: number
  merchant: string
  description: string
  transaction_type: 'debit' | 'credit'
  category?: string
}

export interface TopUpRule {
  id: string
  account_id: string
  threshold: number
  topup_amount: number
  enabled: boolean
}

export interface CreateTopUpRule {
  account_id: number
  threshold: number
  topup_amount: number
}

export interface TopUpEvent {
  id: string
  account_id: string
  amount: number
  triggered_balance: number
  timestamp: string
}