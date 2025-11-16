import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import type { TopUpRule, CreateTopUpRule, Account, TopUpEvent } from '@/types'
import { topUpApi } from '@/services/api'
import { Settings, Plus, Clock } from 'lucide-react'
import { formatCurrency } from '@/utils/currency'

interface TopUpRulesManagerProps {
  selectedAccount: Account | null
}

export function TopUpRulesManager({ selectedAccount }: TopUpRulesManagerProps) {
  const [rules, setRules] = useState<TopUpRule[]>([])
  const [events, setEvents] = useState<TopUpEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState<CreateTopUpRule>({
    account_id: selectedAccount?.id || '',
    threshold: 0,
    topup_amount: 0
  })

  const fetchData = async () => {
    if (!selectedAccount) return
    
    try {
      const [rulesData, eventsData] = await Promise.all([
        topUpApi.getTopUpRules(selectedAccount.id),
        topUpApi.getTopUpEvents(selectedAccount.id)
      ])
      setRules(rulesData)
      setEvents(eventsData.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      ))
    } catch (error) {
      console.error('Failed to fetch topup data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedAccount) {
      setFormData(prev => ({ ...prev, account_id: selectedAccount.id }))
      fetchData()
    }
  }, [selectedAccount])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedAccount || formData.threshold <= 0 || formData.topup_amount <= 0) return

    try {
      await topUpApi.createTopUpRule(formData)
      setFormData({
        account_id: selectedAccount.id,
        threshold: 0,
        topup_amount: 0
      })
      setShowCreateForm(false)
      await fetchData()
    } catch (error) {
      console.error('Failed to create topup rule:', error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!selectedAccount) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8 text-muted-foreground">
            Select an account to manage TopUp rules
          </div>
        </CardContent>
      </Card>
    )
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>TopUp Rules</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">Loading...</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              TopUp Rules for {selectedAccount.name}
            </div>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setShowCreateForm(!showCreateForm)}
            >
              <Plus className="h-4 w-4" />
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {showCreateForm && (
            <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg bg-muted/50">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="threshold">Threshold ($)</Label>
                  <Input
                    id="threshold"
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="50.00"
                    value={formData.threshold || ''}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData(prev => ({ 
                      ...prev, 
                      threshold: parseFloat(e.target.value) || 0 
                    }))}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="topup_amount">TopUp Amount ($)</Label>
                  <Input
                    id="topup_amount"
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="100.00"
                    value={formData.topup_amount || ''}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData(prev => ({ 
                      ...prev, 
                      topup_amount: parseFloat(e.target.value) || 0 
                    }))}
                    required
                  />
                </div>
              </div>
              <Button type="submit">Create Rule</Button>
            </form>
          )}

          {rules.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No TopUp rules configured
            </div>
          ) : (
            <div className="space-y-3">
              {rules.map(rule => (
                <div key={rule.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">
                      TopUp {formatCurrency(rule.topup_amount)} when balance below {formatCurrency(rule.threshold)}
                    </p>
                    <p className="text-sm text-muted-foreground">Rule ID: {rule.id}</p>
                  </div>
                  <Badge variant={rule.enabled ? "default" : "secondary"}>
                    {rule.enabled ? "Active" : "Disabled"}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {events.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              TopUp History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {events.slice(0, 5).map(event => (
                <div key={event.id} className="flex items-center justify-between p-3 border rounded-lg bg-green-50">
                  <div>
                    <p className="font-medium">{formatCurrency(event.amount)} TopUp</p>
                    <p className="text-sm text-muted-foreground">
                      Triggered at balance: {formatCurrency(event.triggered_balance)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatDate(event.timestamp)}
                    </p>
                  </div>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    Completed
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}