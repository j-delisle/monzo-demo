export interface Account {
  id: string
  name: string
  balance: number
  user_id: string
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
  account_id: string
  amount: number
  merchant: string
  description: string
  transaction_type: 'debit' | 'credit'
}

export interface TopUpRule {
  id: string
  account_id: string
  threshold: number
  topup_amount: number
  enabled: boolean
}

export interface CreateTopUpRule {
  account_id: string
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