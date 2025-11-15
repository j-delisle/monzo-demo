import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import type { Account } from '@/types'
import { accountsApi, topUpApi } from '@/services/api'
import { Wallet, RefreshCw } from 'lucide-react'

interface AccountsListProps {
  onAccountSelect: (account: Account) => void
  selectedAccount: Account | null
  refreshTrigger?: number
}

export function AccountsList({ onAccountSelect, selectedAccount, refreshTrigger }: AccountsListProps) {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)
  const [triggeringTopUp, setTriggeringTopUp] = useState<string | null>(null)

  const fetchAccounts = async () => {
    try {
      const data = await accountsApi.getAccounts()
      setAccounts(data)
    } catch (error) {
      console.error('Failed to fetch accounts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTriggerTopUp = async (accountId: string) => {
    setTriggeringTopUp(accountId)
    try {
      const result = await topUpApi.triggerTopUp(accountId)
      console.log('TopUp result:', result)
      // Refresh accounts to show updated balance
      await fetchAccounts()
    } catch (error) {
      console.error('Failed to trigger topup:', error)
    } finally {
      setTriggeringTopUp(null)
    }
  }

  useEffect(() => {
    fetchAccounts()
  }, [refreshTrigger])

  if (loading) {
    return <div className="text-center py-4">Loading accounts...</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold mb-4">Your Accounts</h2>
      {accounts.map((account) => (
        <Card 
          key={account.id} 
          className={`cursor-pointer transition-colors ${
            selectedAccount?.id === account.id 
              ? 'ring-2 ring-primary' 
              : 'hover:bg-accent'
          }`}
          onClick={() => onAccountSelect(account)}
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div className="flex items-center space-x-2">
              <Wallet className="h-4 w-4" />
              <CardTitle className="text-sm font-medium">{account.name}</CardTitle>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                handleTriggerTopUp(account.id)
              }}
              disabled={triggeringTopUp === account.id}
            >
              {triggeringTopUp === account.id ? (
                <RefreshCw className="h-3 w-3 animate-spin" />
              ) : (
                'TopUp'
              )}
            </Button>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">£{account.balance.toFixed(2)}</div>
            <CardDescription>Account ID: {account.id}</CardDescription>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}