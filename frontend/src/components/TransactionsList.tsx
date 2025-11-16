import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { Transaction } from '@/types'
import { transactionsApi } from '@/services/api'
import { ArrowUpDown, TrendingDown, TrendingUp } from 'lucide-react'

interface TransactionsListProps {
  accountId?: string
  refreshTrigger?: number
}

export function TransactionsList({ accountId, refreshTrigger }: TransactionsListProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)

  const fetchTransactions = async () => {
    try {
      const data = await transactionsApi.getTransactions(accountId)
      setTransactions(data.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      ))
    } catch (error) {
      console.error('Failed to fetch transactions:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTransactions()
  }, [accountId, refreshTrigger])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      'Transport': 'bg-blue-100 text-blue-800',
      'Food & Drink': 'bg-orange-100 text-orange-800',
      'Shopping': 'bg-purple-100 text-purple-800',
      'Groceries': 'bg-green-100 text-green-800',
      'Entertainment': 'bg-pink-100 text-pink-800',
      'Bills & Utilities': 'bg-red-100 text-red-800',
      'ATM': 'bg-gray-100 text-gray-800',
      'Income': 'bg-emerald-100 text-emerald-800',
      'Housing': 'bg-yellow-100 text-yellow-800',
      'Other': 'bg-slate-100 text-slate-800'
    }
    return colors[category] || colors['Other']
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">Loading transactions...</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ArrowUpDown className="h-5 w-5" />
          Recent Transactions
        </CardTitle>
      </CardHeader>
      <CardContent>
        {transactions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No transactions found
          </div>
        ) : (
          <div className="space-y-4">
            {transactions.map((transaction) => (
              <div 
                key={transaction.id} 
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-full bg-muted">
                    {transaction.transaction_type === 'credit' ? (
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-600" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium">{transaction.merchant}</p>
                    <p className="text-sm text-muted-foreground">
                      {transaction.description}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatDate(transaction.timestamp)}
                    </p>
                  </div>
                </div>
                <div className="text-right space-y-1">
                  <p className={`font-semibold ${
                    transaction.transaction_type === 'credit' 
                      ? 'text-green-600' 
                      : 'text-red-600'
                  }`}>
                    {transaction.transaction_type === 'credit' ? '+$' : '-$'}{new Intl.NumberFormat('en-US').format(transaction.amount)}
                  </p>
                  {transaction.category && (
                    <Badge 
                      variant="secondary" 
                      className={getCategoryColor(transaction.category)}
                    >
                      {transaction.category}
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}