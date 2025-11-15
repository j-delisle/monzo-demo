import { useState, useEffect } from 'react'
import type { Account } from '@/types'
import { accountsApi } from '@/services/api'
import { AccountsList } from '@/components/AccountsList'
import { TransactionsList } from '@/components/TransactionsList'
import { CreateTransactionForm } from '@/components/CreateTransactionForm'
import { TopUpRulesManager } from '@/components/TopUpRulesManager'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'

export function Dashboard() {
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null)
  const [accounts, setAccounts] = useState<Account[]>([])
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const { user, logout } = useAuth()

  const fetchAccounts = async () => {
    try {
      const data = await accountsApi.getAccounts()
      setAccounts(data)
      if (selectedAccount) {
        const updated = data.find(acc => acc.id === selectedAccount.id)
        if (updated) {
          setSelectedAccount(updated)
        }
      }
    } catch (error) {
      console.error('Failed to fetch accounts:', error)
    }
  }

  useEffect(() => {
    fetchAccounts()
  }, [refreshTrigger])

  const handleTransactionCreated = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  const handleAccountSelect = (account: Account) => {
    setSelectedAccount(account)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Monzo Demo Dashboard
            </h1>
            <p className="text-gray-600">
              Welcome back, {user?.name}! Manage your accounts, transactions, and auto TopUp rules
            </p>
          </div>
          <Button variant="outline" onClick={logout}>
            Sign Out
          </Button>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <AccountsList 
              onAccountSelect={handleAccountSelect}
              selectedAccount={selectedAccount}
              refreshTrigger={refreshTrigger}
            />
          </div>

          <div className="lg:col-span-1 space-y-6">
            <CreateTransactionForm 
              accounts={accounts}
              onTransactionCreated={handleTransactionCreated}
            />
            <TransactionsList 
              accountId={selectedAccount?.id}
              refreshTrigger={refreshTrigger}
            />
          </div>

          <div className="lg:col-span-1">
            <TopUpRulesManager 
              selectedAccount={selectedAccount}
            />
          </div>
        </div>

        <footer className="mt-12 text-center text-gray-500">
          <p>
            Built with React, TypeScript, FastAPI, and Go • 
            Auto TopUp & Transaction Categorization Demo
          </p>
        </footer>
      </div>
    </div>
  )
}