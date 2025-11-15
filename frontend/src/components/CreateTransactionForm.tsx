import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { CreateTransaction, Account } from '@/types'
import { transactionsApi } from '@/services/api'
import { Plus } from 'lucide-react'

interface CreateTransactionFormProps {
  accounts: Account[]
  onTransactionCreated: () => void
}

export function CreateTransactionForm({ accounts, onTransactionCreated }: CreateTransactionFormProps) {
  const [formData, setFormData] = useState<CreateTransaction>({
    account_id: accounts[0]?.id || '',
    amount: 0,
    merchant: '',
    description: '',
    transaction_type: 'debit'
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.merchant || formData.amount <= 0) return

    setLoading(true)
    try {
      await transactionsApi.createTransaction(formData)
      setFormData({
        account_id: accounts[0]?.id || '',
        amount: 0,
        merchant: '',
        description: '',
        transaction_type: 'debit'
      })
      onTransactionCreated()
    } catch (error) {
      console.error('Failed to create transaction:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof CreateTransaction, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="h-5 w-5" />
          Create Transaction
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="account">Account</Label>
            <select
              id="account"
              value={formData.account_id}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange('account_id', e.target.value)}
              className="w-full p-2 border border-input rounded-md bg-background"
            >
              {accounts.map(account => (
                <option key={account.id} value={account.id}>
                  {account.name} (£{account.balance.toFixed(2)})
                </option>
              ))}
            </select>
          </div>

          <div>
            <Label htmlFor="merchant">Merchant</Label>
            <Input
              id="merchant"
              type="text"
              placeholder="e.g. Starbucks, Uber, Tesco"
              value={formData.merchant}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('merchant', e.target.value)}
              required
            />
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              type="text"
              placeholder="Transaction description"
              value={formData.description}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('description', e.target.value)}
            />
          </div>

          <div>
            <Label htmlFor="amount">Amount (£)</Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="0.00"
              value={formData.amount || ''}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('amount', parseFloat(e.target.value) || 0)}
              required
            />
          </div>

          <div>
            <Label htmlFor="type">Transaction Type</Label>
            <select
              id="type"
              value={formData.transaction_type}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange('transaction_type', e.target.value as 'debit' | 'credit')}
              className="w-full p-2 border border-input rounded-md bg-background"
            >
              <option value="debit">Debit (Money Out)</option>
              <option value="credit">Credit (Money In)</option>
            </select>
          </div>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'Creating...' : 'Create Transaction'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}